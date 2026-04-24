# Computes initial expected ultimates by multiplying expected loss rates and frequencies
# by exposure to get expected ultimate losses and claim counts for each period.
#
# Fallback behavior:
# If the expected loss rates file is not provided, this script derives an expected
# loss rate by period from diagonal loss/exposure and smooths it with a 3-year
# rolling average (rounded to 3 decimals).

"""
goal: Calculate Initial Expected ultimates for all periods and measures.

inputs:
    ../processed-data/1_triangles.parquet - Triangle data including Exposure measure (diagonal used)
    ../processed-data/1_expected_loss_rates.parquet - Optional expected loss rates and frequencies by period

outputs:
    ../ultimates/projected-ultimates.parquet - Combined ultimates file with IE columns
    ../ultimates/projected-ultimates.csv - Same data in CSV format

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 3-initial-expected.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

from modules import config

# Paths from modules/config.py — override here if needed:
# NOTE: Set INPUT_EXPECTED_RATES to None if expected loss rate data is not available.
#       In that case, this script uses the built-in fallback based on
#       a 3-year rolling average of diagonal loss per unit of exposure.
INPUT_TRIANGLE_DATA  = config.PROCESSED_DATA + "1_triangles.parquet"
INPUT_EXPECTED_RATES = config.PROCESSED_DATA + "1_expected_loss_rates.parquet"  # Set to None if not available
OUTPUT_PATH          = config.ULTIMATES


def extract_diagonal(triangle_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the latest (diagonal) value for each period × measure combination.
    
    The diagonal represents the most mature value for each period, which is
    the current actual value at the valuation date.
    
    Args:
        triangle_data: DataFrame with triangle data
    
    Returns:
        DataFrame with columns: period, measure, age, value
    """
    # For each period × measure, get the latest age (diagonal value)
    diagonal = triangle_data.groupby(['period', 'measure'], observed=True).agg({
        'value': 'last',  # Last value is the most mature (diagonal)
        'age': 'last'
    }).reset_index()
    
    print(f"  Extracted diagonal for {len(diagonal)} period × measure combinations")
    return diagonal


def extract_exposure_diagonal(triangle_data: pd.DataFrame) -> dict:
    """
    Extract the latest (diagonal) exposure value for each period.
    
    The diagonal represents the most mature value for each period, which is
    the total exposure for that period.
    
    Args:
        triangle_data: DataFrame with triangle data including Exposure measure
    
    Returns:
        Dictionary mapping period (str) to exposure value (float)
    """
    # Filter to Exposure measure only
    exposure_data = triangle_data[triangle_data['measure'] == 'Exposure'].copy()
    
    if exposure_data.empty:
        raise ValueError("No Exposure measure found in triangle data. Initial Expected calculation requires Exposure.")
    
    # For each period, get the latest age (diagonal value)
    # Group by period and take the last value (most mature)
    exposure_diagonal = exposure_data.groupby('period', observed=True).agg({
        'value': 'last',  # Last value is the most mature (diagonal)
        'age': 'last'
    }).reset_index()
    
    # Convert to dictionary
    exposure_dict = dict(zip(
        exposure_diagonal['period'].astype(str),
        exposure_diagonal['value'].astype(float)
    ))
    
    print(f"  Extracted exposure for {len(exposure_dict)} period(s)")
    return exposure_dict


def build_fallback_expected_rates(diagonal: pd.DataFrame, exposure: dict) -> pd.DataFrame:
    """
    Build fallback expected loss rates when no expected rates input file is available.

    Method by period:
    1. Compute diagonal loss per unit exposure
    2. Smooth with a 3-year rolling average
    3. Round to 3 decimals

    The fallback produces expected_loss_rate only. expected_freq is left as NaN.

    Args:
        diagonal: DataFrame with diagonal values (period, measure, age, value)
        exposure: Dictionary mapping period (str) to exposure value (float)

    Returns:
        DataFrame with columns: period, expected_loss_rate, expected_freq
    """
    diagonal_loss = diagonal[diagonal['measure'].isin(['Incurred Loss', 'Paid Loss'])].copy()

    if diagonal_loss.empty:
        raise ValueError(
            "Fallback expected-rate calculation requires 'Incurred Loss' or 'Paid Loss' in triangle data."
        )

    preferred_measure = 'Incurred Loss' if (diagonal_loss['measure'] == 'Incurred Loss').any() else 'Paid Loss'
    diagonal_loss = diagonal_loss[diagonal_loss['measure'] == preferred_measure].copy()

    diagonal_loss['period'] = diagonal_loss['period'].astype(str)
    diagonal_loss['loss_value'] = diagonal_loss['value'].astype(float)
    diagonal_loss['exposure'] = diagonal_loss['period'].map(exposure).astype(float)

    if (diagonal_loss['exposure'] <= 0).any():
        bad_periods = diagonal_loss.loc[diagonal_loss['exposure'] <= 0, 'period'].tolist()
        raise ValueError(
            f"Fallback expected-rate calculation requires positive exposure. Non-positive exposure for period(s): {bad_periods}"
        )

    diagonal_loss['raw_loss_rate'] = diagonal_loss['loss_value'] / diagonal_loss['exposure']
    diagonal_loss['period_num'] = pd.to_numeric(diagonal_loss['period'], errors='coerce')
    diagonal_loss = diagonal_loss.sort_values(by=['period_num', 'period'], kind='stable')
    diagonal_loss['expected_loss_rate'] = (
        diagonal_loss['raw_loss_rate']
        .rolling(window=3, min_periods=1)
        .mean()
        .round(3)
    )

    fallback = diagonal_loss[['period', 'expected_loss_rate']].copy()
    fallback['expected_freq'] = np.nan

    print(f"  Built fallback expected loss rates from '{preferred_measure}' using 3-year rolling average")
    print(f"  Fallback generated for {len(fallback)} period(s)")

    return fallback


def compute_initial_ultimate_ies(expected_rates: pd.DataFrame, exposure: dict, diagonal: pd.DataFrame) -> pd.DataFrame:
    """
    Compute initial expected ultimates by multiplying rates and frequencies by exposure,
    and then compute IBNR by subtracting actual diagonal values.
    
    For each period:
    - Expected Loss Ultimate = Expected Loss Rate * Exposure (applies to Incurred Loss and Paid Loss)
    - Expected Count Ultimate = Expected Frequency * Exposure (applies to Reported Count and Closed Count)
    - IBNR_IE = Ultimate_IE - Actual
    
    Args:
        expected_rates: DataFrame with columns: period, expected_loss_rate, expected_freq
        exposure: Dictionary mapping period to exposure value
        diagonal: DataFrame with diagonal (actual) values by period, measure, age
    
    Returns:
        DataFrame with columns: period, measure, current_age, actual, ultimate_ie, ibnr_ie
    """
    # Create lookup for diagonal (actual) values
    diagonal_lookup = diagonal.set_index(['period', 'measure'])[['age', 'value']].to_dict('index')
    
    rows = []
    
    for _, row in expected_rates.iterrows():
        period = str(row['period'])
        
        # Get exposure for this period
        exp = exposure.get(period)
        if exp is None or pd.isna(exp):
            print(f"  Warning: No exposure found for period {period}, skipping")
            continue
        
        # Compute loss ultimate (applies to both Incurred and Paid)
        if pd.notna(row.get('expected_loss_rate')):
            loss_ultimate = float(row['expected_loss_rate']) * float(exp)
            
            for measure in ['Incurred Loss', 'Paid Loss']:
                # Get actual value from diagonal
                actual_info = diagonal_lookup.get((period, measure), {})
                actual = actual_info.get('value', np.nan)
                current_age = str(actual_info.get('age', '')) if actual_info.get('age') else None
                
                # Compute IBNR
                if pd.notna(actual) and pd.notna(loss_ultimate):
                    ibnr_ie = loss_ultimate - actual
                else:
                    ibnr_ie = np.nan
                
                rows.append({
                    'period': period,
                    'measure': measure,
                    'current_age': current_age,
                    'actual': actual,
                    'ultimate_ie': loss_ultimate,
                    'ibnr_ie': ibnr_ie
                })
        
        # Compute count ultimate (applies to both Reported and Closed)
        if pd.notna(row.get('expected_freq')):
            count_ultimate = float(row['expected_freq']) * float(exp)
            
            for measure in ['Reported Count', 'Closed Count']:
                # Get actual value from diagonal
                actual_info = diagonal_lookup.get((period, measure), {})
                actual = actual_info.get('value', np.nan)
                current_age = str(actual_info.get('age', '')) if actual_info.get('age') else None
                
                # Compute IBNR
                if pd.notna(actual) and pd.notna(count_ultimate):
                    ibnr_ie = count_ultimate - actual
                else:
                    ibnr_ie = np.nan
                
                rows.append({
                    'period': period,
                    'measure': measure,
                    'current_age': current_age,
                    'actual': actual,
                    'ultimate_ie': count_ultimate,
                    'ibnr_ie': ibnr_ie
                })
    
    if not rows:
        raise ValueError("No initial expected ultimates could be computed. Check that expected_loss_rate and expected_freq have values.")
    
    result_df = pd.DataFrame(rows)
    
    # Convert to appropriate types
    result_df['period'] = result_df['period'].astype(str)
    result_df['measure'] = result_df['measure'].astype('category')
    result_df['current_age'] = result_df['current_age'].astype(str)
    for col in ['actual', 'ultimate_ie', 'ibnr_ie']:
        result_df[col] = result_df[col].astype(float)
    
    print(f"  Computed {len(result_df)} expected ultimate(s) across {len(result_df['period'].unique())} period(s)")
    
    return result_df


if __name__ == "__main__":
    print("Computing Initial Expected ultimates...")

    # Load triangle data
    print(f"\nReading triangle data from: {INPUT_TRIANGLE_DATA}")
    df_triangles = pd.read_parquet(INPUT_TRIANGLE_DATA)

    # Extract diagonal values
    print("\nExtracting diagonal values...")
    diagonal = extract_diagonal(df_triangles)

    # Ensure string types for matching
    diagonal['period'] = diagonal['period'].astype(str)
    diagonal['measure'] = diagonal['measure'].astype(str)
    diagonal['age'] = diagonal['age'].astype(str)

    # Extract exposure diagonal
    print("\nExtracting exposure values...")
    exposure_dict = extract_exposure_diagonal(df_triangles)

    # Load expected rates, or build fallback if not available
    if INPUT_EXPECTED_RATES is not None and Path(INPUT_EXPECTED_RATES).exists():
        print(f"\nReading expected rates from: {INPUT_EXPECTED_RATES}")
        df_expected_rates = pd.read_parquet(INPUT_EXPECTED_RATES)
    else:
        if INPUT_EXPECTED_RATES is None:
            print("\nINPUT_EXPECTED_RATES is set to None. Using fallback expected-rate method.")
        else:
            print(f"\nExpected rates file not found: {INPUT_EXPECTED_RATES}")
            print("Using fallback expected-rate method.")
        df_expected_rates = build_fallback_expected_rates(diagonal, exposure_dict)

    # Compute initial expected ultimates
    print("\nComputing initial expected ultimates...")
    df_ie = compute_initial_ultimate_ies(df_expected_rates, exposure_dict, diagonal)
    
    # Create output directory if it doesn't exist
    output_dir = Path(OUTPUT_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if projected-ultimates already exists and merge if so
    output_parquet = output_dir / "projected-ultimates.parquet"
    output_csv = output_dir / "projected-ultimates.csv"
    
    if output_parquet.exists():
        print(f"\nMerging with existing data in: {output_parquet}")
        df_existing = pd.read_parquet(output_parquet)
        
        # Merge on period, measure, current_age (outer join to keep all rows)
        df_combined = df_existing.merge(
            df_ie[['period', 'measure', 'current_age', 'ultimate_ie', 'ibnr_ie']],
            on=['period', 'measure', 'current_age'],
            how='outer',
            suffixes=('', '_new')
        )
        
        # Update/add IE columns from new data
        for col in ['ultimate_ie', 'ibnr_ie']:
            if col + '_new' in df_combined.columns:
                df_combined[col] = df_combined[col + '_new'].combine_first(df_combined.get(col, pd.Series()))
                df_combined.drop(columns=[col + '_new'], inplace=True)
            elif col not in df_combined.columns and col in df_ie.columns:
                df_combined[col] = df_ie.set_index(['period', 'measure', 'current_age'])[col]
        
        df_final = df_combined
        print(f"  Combined with {len(df_existing)} existing row(s)")
    else:
        df_final = df_ie
        print(f"\nCreating new projected-ultimates file")
    
    # Save results
    df_final.to_parquet(output_parquet, index=False)
    df_final.to_csv(output_csv, index=False)
    
    print(f"\nSaved initial expected ultimates to projected-ultimates:")
    print(f"  Parquet: {output_parquet}")
    print(f"  CSV: {output_csv}")
    
    print("\nSample of results:")
    print(df_ie.head(10).to_string(index=False))
    
    print("\nSummary by measure:")
    summary = df_ie.groupby('measure', observed=True).agg({
        'ultimate_ie': 'sum',
        'ibnr_ie': 'sum',
        'actual': 'sum'
    }).round(0)
    print(summary.to_string())
    
    print("\nInitial Expected calculation complete!")
