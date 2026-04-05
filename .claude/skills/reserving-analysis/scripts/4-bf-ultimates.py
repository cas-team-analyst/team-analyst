# Computes Bornhuetter-Ferguson ultimates by combining Chain Ladder percent developed
# with Initial Expected ultimates to produce a credibility-weighted estimate.

"""
BF core: compute Bornhuetter-Ferguson ultimates from CL and IE outputs.

goal: Calculate Bornhuetter-Ferguson ultimates for all periods and measures.

Formula:
    BF Ultimate = Actual + (1 - pct_developed) × Expected
    BF IBNR     = (1 - pct_developed) × Expected

inputs:
    ../processed-data/1_triangles.parquet - Triangle data (for diagonal/actual values)
    ../ultimates/chain-ladder.parquet - CL ultimates with pct_developed
    ../ultimates/initial-expected.parquet - Expected ultimates by period and measure

outputs:
    ../ultimates/bornhuetter-ferguson.parquet - BF ultimates with IBNR
    ../ultimates/bornhuetter-ferguson.csv - Same data in CSV format

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 4-bf-ultimates.py
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Replace these when using this file in an actual project:
# NOTE: Set INPUT_IE_ULTIMATES to None if Initial Expected data is not available.
#       This script will exit gracefully since BF requires Initial Expected ultimates.
INPUT_TRIANGLE_DATA = "../processed-data/1_triangles.parquet"
INPUT_CL_ULTIMATES = "../ultimates/chain-ladder.parquet"
INPUT_IE_ULTIMATES = "../ultimates/initial-expected.parquet"  # Set to None if not available
OUTPUT_PATH = "../ultimates/"


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


def compute_bf_ultimates(diagonal: pd.DataFrame, cl_ultimates: pd.DataFrame, 
                         ie_ultimates: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Bornhuetter-Ferguson ultimates.
    
    BF combines the actual losses (diagonal) with expected IBNR based on:
    - Percent developed from Chain Ladder
    - Expected ultimate from Initial Expected
    
    BF IBNR = (1 - pct_developed) × Expected
    BF Ultimate = Actual + BF IBNR
    
    Args:
        diagonal: DataFrame with actual values (period, measure, age, value)
        cl_ultimates: DataFrame with CL results including pct_developed
        ie_ultimates: DataFrame with expected ultimates
    
    Returns:
        DataFrame with columns: period, measure, current_age, actual, pct_developed,
                                expected_ultimate, bf_ibnr, bf_ultimate
    """
    # Create lookups
    pct_lookup = cl_ultimates.set_index(['measure', 'current_age'])['pct_developed'].to_dict()
    ie_lookup = ie_ultimates.set_index(['period', 'measure'])['expected_ultimate'].to_dict()
    
    rows = []
    skipped_measures = set()
    
    for _, r in diagonal.iterrows():
        measure = str(r['measure'])
        period = str(r['period'])
        age = str(r['age'])
        actual = r['value']
        
        # Skip Exposure measure (not needed for BF)
        if measure == 'Exposure':
            continue
        
        # Get percent developed from CL
        pct_dev = pct_lookup.get((measure, age), np.nan)
        
        # Get expected ultimate from IE
        expected = ie_lookup.get((period, measure), np.nan)
        
        # Calculate BF values
        if pd.notna(pct_dev) and pd.notna(expected):
            bf_ibnr = (1 - pct_dev) * expected
            bf_ultimate = actual + bf_ibnr
        else:
            bf_ibnr = np.nan
            bf_ultimate = np.nan
            if pd.isna(expected):
                skipped_measures.add(measure)
        
        rows.append({
            'period': period,
            'measure': measure,
            'current_age': age,
            'actual': actual,
            'pct_developed': pct_dev,
            'expected_ultimate': expected,
            'bf_ibnr': bf_ibnr,
            'bf_ultimate': bf_ultimate,
        })
    
    if skipped_measures:
        print(f"  Note: Some measures missing expected ultimates: {', '.join(sorted(skipped_measures))}")
        print(f"        BF calculation requires Initial Expected ultimates for all measures")
    
    result_df = pd.DataFrame(rows)
    print(f"  Computed {len(result_df)} BF ultimate(s)")
    
    return result_df


if __name__ == "__main__":
    print("Computing Bornhuetter-Ferguson ultimates...")
    
    # Check if Initial Expected data is configured
    if INPUT_IE_ULTIMATES is None:
        print("\nINPUT_IE_ULTIMATES is set to None.")
        print("Bornhuetter-Ferguson calculation requires Initial Expected ultimates.")
        print("Skipping BF calculation.")
        sys.exit(0)
    
    # Load triangle data for diagonal
    print(f"\nReading triangle data from: {INPUT_TRIANGLE_DATA}")
    df_triangles = pd.read_parquet(INPUT_TRIANGLE_DATA)
    
    # Extract diagonal
    print("\nExtracting diagonal values...")
    diagonal = extract_diagonal(df_triangles)
    
    # Load Chain Ladder ultimates
    cl_path = Path(INPUT_CL_ULTIMATES)
    if not cl_path.exists():
        print(f"\nError: Chain Ladder ultimates not found: {INPUT_CL_ULTIMATES}")
        print("Please run 2c-chainladder-ultimates.py first.")
        exit(1)
    
    print(f"\nReading Chain Ladder ultimates from: {INPUT_CL_ULTIMATES}")
    df_cl = pd.read_parquet(INPUT_CL_ULTIMATES)
    
    # Load Initial Expected ultimates
    ie_path = Path(INPUT_IE_ULTIMATES)
    if not ie_path.exists():
        print(f"\nInitial Expected ultimates not found: {INPUT_IE_ULTIMATES}")
        print("Bornhuetter-Ferguson calculation requires Initial Expected ultimates.")
        print("Please run 3-ie-ultimates.py first, or set INPUT_IE_ULTIMATES to None to skip this script.")
        sys.exit(0)
    
    print(f"Reading Initial Expected ultimates from: {INPUT_IE_ULTIMATES}")
    df_ie = pd.read_parquet(INPUT_IE_ULTIMATES)
    
    # Ensure all columns are strings for matching
    diagonal['period'] = diagonal['period'].astype(str)
    diagonal['measure'] = diagonal['measure'].astype(str)
    diagonal['age'] = diagonal['age'].astype(str)
    
    df_cl['measure'] = df_cl['measure'].astype(str)
    df_cl['current_age'] = df_cl['current_age'].astype(str)
    
    df_ie['period'] = df_ie['period'].astype(str)
    df_ie['measure'] = df_ie['measure'].astype(str)
    
    # Compute BF ultimates
    print("\nComputing Bornhuetter-Ferguson ultimates...")
    df_bf = compute_bf_ultimates(diagonal, df_cl, df_ie)
    
    # Convert to appropriate types
    df_bf['period'] = df_bf['period'].astype(str)
    df_bf['measure'] = df_bf['measure'].astype('category')
    df_bf['current_age'] = df_bf['current_age'].astype(str)
    for col in ['actual', 'pct_developed', 'expected_ultimate', 'bf_ibnr', 'bf_ultimate']:
        df_bf[col] = df_bf[col].astype(float)
    
    # Create output directory if it doesn't exist
    output_dir = Path(OUTPUT_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save results
    output_parquet = output_dir / "bornhuetter-ferguson.parquet"
    output_csv = output_dir / "bornhuetter-ferguson.csv"
    
    df_bf.to_parquet(output_parquet, index=False)
    df_bf.to_csv(output_csv, index=False)
    
    print(f"\nSaved Bornhuetter-Ferguson ultimates:")
    print(f"  Parquet: {output_parquet}")
    print(f"  CSV: {output_csv}")
    
    print("\nSample of results:")
    print(df_bf.head(15).to_string(index=False))
    
    print("\nSummary by measure:")
    summary = df_bf.groupby('measure', observed=True).agg({
        'bf_ultimate': 'sum',
        'bf_ibnr': 'sum',
        'actual': 'sum',
        'expected_ultimate': 'sum'
    }).round(0)
    print(summary.to_string())
    
    print("\nBornhuetter-Ferguson calculation complete!")
