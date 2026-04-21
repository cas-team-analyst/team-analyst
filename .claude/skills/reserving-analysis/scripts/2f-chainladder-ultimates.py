# Calculates Chain Ladder ultimates by reading LDF selections from Excel, building cumulative
# development factors (CDFs), and projecting ultimate values for each period and measure.

"""
Chain Ladder core: build CDFs from selected LDFs and project Chain Ladder ultimates.

goal: Calculate Chain Ladder ultimates for all periods and measures using selected LDFs.

inputs:
    ../processed-data/1_triangles.parquet - Triangle data (for ordered age list and diagonal)
    ../selections/Chain Ladder Selections - LDFs.xlsx - LDF selections by measure

outputs:
    ../ultimates/projected-ultimates.parquet - Combined ultimates file with CL columns
    ../ultimates/projected-ultimates.csv - Same data in CSV format

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 2f-chainladder-ultimates.py
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path

from modules import config

# Paths from modules/config.py — override here if needed:
INPUT_TRIANGLE_DATA    = config.PROCESSED_DATA + "1_triangles.parquet"
INPUT_SELECTIONS_EXCEL = config.SELECTIONS + "Chain Ladder Selections - LDFs.xlsx"
OUTPUT_PATH            = config.ULTIMATES


# Excel reading helpers
_INTERVAL_RE = re.compile(r'^\d+-\d+$')


def _is_interval_row(row_series) -> bool:
    """Return True if the row looks like an interval label row (e.g. '12-24', 'Tail')."""
    vals = [str(v).strip() for v in row_series.iloc[1:] if pd.notna(v) and str(v).strip()]
    matches = sum(1 for v in vals if _INTERVAL_RE.match(v) or v.lower() == 'tail')
    return matches >= 3


def find_row_by_label(df: pd.DataFrame, label: str):
    """Return (row_index, row_series) for the first row whose first cell matches label."""
    mask = df.iloc[:, 0].astype(str).str.strip() == label
    indices = df[mask].index
    if len(indices) == 0:
        return None, None
    idx = indices[0]
    return idx, df.iloc[idx]


def find_interval_row_above(df: pd.DataFrame, row_idx: int, max_scan: int = 20):
    """
    Scan upward from row_idx to find the nearest interval header row.
    Returns the row series or None.
    """
    for offset in range(1, min(max_scan, row_idx + 1)):
        candidate = df.iloc[row_idx - offset]
        if _is_interval_row(candidate):
            return candidate
    return None


def read_labeled_selections(df: pd.DataFrame, label: str) -> dict:
    """
    Read a selection row identified by its label in column 0.
    Finds the matching interval header by scanning upward.
    Returns {interval_str: float_value} or empty dict.
    """
    row_idx, sel_row = find_row_by_label(df, label)
    if sel_row is None:
        return {}

    interval_row = find_interval_row_above(df, row_idx)
    if interval_row is None:
        return {}

    selections = {}
    for col_idx in range(1, len(sel_row)):
        interval = interval_row.iloc[col_idx]
        ldf_value = sel_row.iloc[col_idx]
        if pd.notna(interval) and pd.notna(ldf_value):
            try:
                selections[str(interval).strip()] = float(ldf_value)
            except (ValueError, TypeError):
                continue
    return selections


def get_tail(selections: dict) -> float:
    """Return tail factor from selections dict, checking both 'Tail' and 'tail'."""
    return float(selections.get('Tail', selections.get('tail', 1.0)))


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


def read_selections_from_excel(excel_path: str, measure: str, ages: list) -> dict:
    """
    Read LDF selections from the Chain Ladder Selections Excel file for a specific measure.
    Priority: 'Selection' row (actuary final) → 'AI Selection' row (fallback).
    Uses robust upward-scanning interval detection.
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=measure, engine='openpyxl', engine_kwargs={'data_only': True})
        # Try actuary selection first, fall back to AI selection
        for label in ("Selection", "AI Selection"):
            selections = read_labeled_selections(df, label)
            if selections:
                print(f"  Found {len(selections)} LDF selection(s) for {measure} (row: '{label}')")
                return selections
        raise ValueError(
            f"No values found in 'Selection' or 'AI Selection' row for sheet '{measure}'."
        )
    except Exception as e:
        print(f"  Warning: Could not read selections for {measure}: {e}")
        return {}


def build_cdfs(selections: dict, ages: list, measure: str) -> pd.DataFrame:
    """
    Convert selected LDFs (including tail if present) into cumulative CDFs per age.
    
    Args:
        selections: Dictionary mapping interval to selected LDF
        ages: List of ordered age values
        measure: Measure name
    
    Returns:
        DataFrame with columns: measure, age, cdf, pct_developed
    """
    if not selections:
        return pd.DataFrame(columns=['measure', 'age', 'cdf', 'pct_developed'])
    
    # Create interval labels from ages
    intervals = {f"{ages[i]}-{ages[i+1]}": i for i in range(len(ages) - 1)}
    
    # Get tail factor (if present, otherwise 1.0)
    tail = get_tail(selections)
    
    # Build CDFs from oldest to youngest
    # Start with tail at the oldest age
    cdfs = {ages[-1]: tail}
    
    # Work backwards through the ages
    for i in range(len(ages) - 2, -1, -1):
        interval = f"{ages[i]}-{ages[i+1]}"
        ldf = selections.get(interval, np.nan)
        
        if pd.notna(ldf):
            cdfs[ages[i]] = ldf * cdfs[ages[i + 1]]
        else:
            cdfs[ages[i]] = np.nan
    
    # Convert to DataFrame
    rows = []
    for age, cdf in cdfs.items():
        rows.append({
            'measure': measure,
            'age': age,
            'cdf': cdf,
            'pct_developed': 1.0 / cdf if (pd.notna(cdf) and cdf > 0) else np.nan
        })
    
    return pd.DataFrame(rows)


def project_ultimates(diagonal: pd.DataFrame, cdf_df: pd.DataFrame) -> pd.DataFrame:
    """
    Multiply each diagonal value by its CDF to get the Chain Ladder ultimate.
    
    Args:
        diagonal: DataFrame with columns: period, measure, age, value
        cdf_df: DataFrame with columns: measure, age, cdf, pct_developed
    
    Returns:
        DataFrame with columns: period, measure, current_age, actual, cdf, 
                                pct_developed, ultimate_cl, ibnr_cl
    """
    # Create lookup for CDFs
    cdf_lookup = cdf_df.set_index(['measure', 'age'])[['cdf', 'pct_developed']]
    
    rows = []
    for _, r in diagonal.iterrows():
        key = (str(r['measure']), str(r['age']))
        
        if key in cdf_lookup.index:
            cdf = cdf_lookup.loc[key, 'cdf']
            pct = cdf_lookup.loc[key, 'pct_developed']
            
            if pd.notna(cdf) and pd.notna(r['value']):
                ultimate = r['value'] * cdf
                ibnr = ultimate - r['value']
            else:
                ultimate = ibnr = np.nan
        else:
            cdf = pct = ultimate = ibnr = np.nan
        
        rows.append({
            'period': str(r['period']),
            'measure': str(r['measure']),
            'current_age': str(r['age']),
            'actual': r['value'],
            'cdf': cdf,
            'pct_developed': pct,
            'ultimate_cl': ultimate,
            'ibnr_cl': ibnr,
        })
    
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("Computing Chain Ladder ultimates from selections...")
    
    # Load triangle data
    print(f"\nReading triangle data from: {INPUT_TRIANGLE_DATA}")
    df_triangles = pd.read_parquet(INPUT_TRIANGLE_DATA)
    
    # Get ordered list of ages
    ages = [str(a) for a in df_triangles['age'].cat.categories]
    print(f"  Found {len(ages)} age periods: {ages[0]} to {ages[-1]}")
    
    # Get list of measures (excluding Exposure if present)
    measures = [m for m in df_triangles['measure'].cat.categories if m != 'Exposure']
    print(f"  Found {len(measures)} measure(s): {', '.join(measures)}")
    
    # Extract diagonal values
    print("\nExtracting diagonal values...")
    diagonal = extract_diagonal(df_triangles)
    
    # Check if selections file exists
    selections_path = Path(INPUT_SELECTIONS_EXCEL)
    if not selections_path.exists():
        print(f"\nError: Selections file not found: {INPUT_SELECTIONS_EXCEL}")
        print("Please ensure Chain Ladder Selections - LDFs.xlsx exists with LDF selections.")
        exit(1)
    
    print(f"\nReading LDF selections from: {INPUT_SELECTIONS_EXCEL}")
    
    # Read selections for each measure and build CDFs
    all_cdfs = []
    for measure in measures:
        print(f"\nProcessing {measure}...")
        selections = read_selections_from_excel(str(selections_path), measure, ages)
        
        if selections:
            cdf_df = build_cdfs(selections, ages, measure)
            all_cdfs.append(cdf_df)
        else:
            print(f"  Skipping {measure} (no valid selections found)")
    
    if not all_cdfs:
        print("\nError: No valid LDF selections found in any sheet.")
        print("Please ensure the Excel file has 'Selection' rows with LDF values.")
        exit(1)
    
    # Combine all CDFs
    combined_cdfs = pd.concat(all_cdfs, ignore_index=True)
    print(f"\nBuilt CDFs for {len(combined_cdfs)} measure × age combinations")
    
    # Project ultimates
    print("\nProjecting Chain Ladder ultimates...")
    df_cl = project_ultimates(diagonal, combined_cdfs)
    
    # Convert to appropriate types
    df_cl['period'] = df_cl['period'].astype(str)
    df_cl['measure'] = df_cl['measure'].astype('category')
    df_cl['current_age'] = df_cl['current_age'].astype(str)
    for col in ['actual', 'cdf', 'pct_developed', 'ultimate_cl', 'ibnr_cl']:
        df_cl[col] = df_cl[col].astype(float)
    
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
            df_cl,
            on=['period', 'measure', 'current_age'],
            how='outer',
            suffixes=('', '_new')
        )
        
        # Update/add CL columns from new data
        for col in ['actual', 'cdf', 'pct_developed', 'ultimate_cl', 'ibnr_cl']:
            if col + '_new' in df_combined.columns:
                df_combined[col] = df_combined[col + '_new'].combine_first(df_combined.get(col, pd.Series()))
                df_combined.drop(columns=[col + '_new'], inplace=True)
            elif col not in df_combined.columns and col in df_cl.columns:
                df_combined[col] = df_cl.set_index(['period', 'measure', 'current_age'])[col]
        
        df_final = df_combined
        print(f"  Combined with {len(df_existing)} existing row(s)")
    else:
        df_final = df_cl
        print(f"\nCreating new projected-ultimates file")
    
    # Save results
    df_final.to_parquet(output_parquet, index=False)
    df_final.to_csv(output_csv, index=False)
    
    print(f"\nSaved Chain Ladder ultimates to projected-ultimates:")
    print(f"  Parquet: {output_parquet}")
    print(f"  CSV: {output_csv}")
    
    print("\nSample of results:")
    print(df_cl.head(15).to_string(index=False))
    
    print("\nSummary by measure:")
    summary = df_cl.groupby('measure', observed=True).agg({
        'ultimate_cl': 'sum',
        'ibnr_cl': 'sum',
        'actual': 'sum'
    }).round(0)
    print(summary.to_string())
    
    print("\nChain Ladder calculation complete!")
