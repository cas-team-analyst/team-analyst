"""
Data preparation script for triangle analysis.

Reads raw triangle data, optional prior selections, and optional expected loss rates,
validates them, and saves to standardized format.

Run from scripts/ directory: python 1a-prep-data.py
"""

import pandas as pd
from pathlib import Path
from typing import Optional

from modules import config
from modules.validators import (
    validate_combined_data,
    validate_prior_selections, 
    validate_expected_loss_rates
)

# Paths from modules/config.py — override here if needed:
DATA_FILE_PATH = config.RAW_DATA
OUTPUT_PATH = config.PROCESSED_DATA
EXPECTED_LOSS_RATES_FILE = None  # Optional: path to expected loss rates file


# =============================================================================
# TODO: IMPLEMENT DATA READING FUNCTIONS BELOW
# =============================================================================

def read_triangle_data(
    file_path: str,
    sheet_name: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Reads a loss or count triangle from 'Triangle Examples 1.xlsx'.

    Loss sheets (Paid 1, Inc 1): 2 header rows.
      Row 0: "Age of Evaluation" label
      Row 1: "Accident Year" + numeric maturities in months
      Rows 2+: AY values

    Count sheet (Ct 1): 1 header row.
      Row 0: "Accident Year" + numeric maturities in months
      Rows 1+: AY values

    Exposure sheet: 2-column table, 1 header row.
      Row 0: "Accident Year", "Payroll"
      Rows 1+: AY, payroll value
    """
    measure   = kwargs.get("measure", "Paid Loss")
    unit_type = kwargs.get("unit_type", "Dollars")
    source    = kwargs.get("source", "Triangle Examples 1.xlsx")
    n_header_rows = kwargs.get("n_header_rows", 2)

    raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    if measure == "Exposure":
        # Simple 2-column table; row 0 is header
        rows = []
        for _, row in raw.iloc[1:].iterrows():
            if pd.isna(row.iloc[0]):
                continue
            rows.append({
                "period":    str(int(row.iloc[0])),
                "age":       None,
                "value":     float(row.iloc[1]),
                "measure":   "Exposure",
                "unit_type": "Count",
                "source":    source,
                "details":   "",
            })
        return pd.DataFrame(rows)

    # Loss / count triangle
    maturity_row = raw.iloc[n_header_rows - 1]
    maturities   = [str(int(v)) for v in maturity_row.iloc[1:] if pd.notna(v)]

    rows = []
    for _, raw_row in raw.iloc[n_header_rows:].iterrows():
        ay = raw_row.iloc[0]
        if pd.isna(ay):
            continue
        period = str(int(ay))
        for col_idx, maturity in enumerate(maturities, start=1):
            val = raw_row.iloc[col_idx]
            if pd.notna(val):
                rows.append({
                    "period":    period,
                    "age":       maturity,
                    "value":     float(val),
                    "measure":   measure,
                    "unit_type": unit_type,
                    "source":    source,
                    "details":   "",
                })
    return pd.DataFrame(rows)


def read_and_process_triangles():
    """Read all triangles from Triangle Examples 1.xlsx and save to parquet/CSV."""
    src_file = DATA_FILE_PATH + "Triangle Examples 1.xlsx"

    print("  Reading Paid Loss (sheet 'Paid 1')...")
    paid = read_triangle_data(src_file, sheet_name="Paid 1",
                              measure="Paid Loss", unit_type="Dollars",
                              n_header_rows=2)

    print("  Reading Incurred Loss (sheet 'Inc 1')...")
    incurred = read_triangle_data(src_file, sheet_name="Inc 1",
                                  measure="Incurred Loss", unit_type="Dollars",
                                  n_header_rows=2)

    print("  Reading Reported Count (sheet 'Ct 1')...")
    reported = read_triangle_data(src_file, sheet_name="Ct 1",
                                  measure="Reported Count", unit_type="Count",
                                  n_header_rows=1)

    print("  Reading Exposure (sheet 'Exposure')...")
    exposure = read_triangle_data(src_file, sheet_name="Exposure",
                                  measure="Exposure", unit_type="Count")

    # Derive ordered categories from the paid triangle (most complete)
    period_cats = sorted(paid["period"].unique(), key=lambda x: int(x))
    age_cats    = sorted(paid["age"].unique(), key=lambda x: int(x))

    all_data = pd.concat([paid, incurred, reported, exposure], ignore_index=True)

    # Apply ordered categoricals
    all_data["period"] = pd.Categorical(all_data["period"],
                                        categories=period_cats, ordered=True)
    all_data["age"] = pd.Categorical(all_data["age"],
                                     categories=age_cats, ordered=True)
    all_data["measure"]   = all_data["measure"].astype("category")
    all_data["unit_type"] = all_data["unit_type"].astype("category")
    all_data["source"]    = all_data["source"].astype("category")

    validate_combined_data(all_data)

    all_data.to_parquet(OUTPUT_PATH + "1_triangles.parquet", index=False)
    all_data.to_csv(OUTPUT_PATH + "1_triangles.csv", index=False)
    print(f"  Saved {len(all_data)} rows to processed-data/1_triangles.parquet")


def read_and_process_prior_selections(triangle_data: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Read and validate prior selections if they exist."""
    prior_file = OUTPUT_PATH + "../prior-selections.csv"
    
    if not Path(prior_file).exists():
        print("  No prior selections file found (optional)")
        return None
    
    print(f"  Found prior selections file: {prior_file}")
    df_prior = pd.read_csv(prior_file)
    
    # Ensure required columns
    required = ['measure', 'interval', 'selection']
    if not all(col in df_prior.columns for col in required):
        raise ValueError(f"Prior selections must have columns: {', '.join(required)}")
    
    if 'reasoning' not in df_prior.columns:
        df_prior['reasoning'] = ''
    
    if df_prior.empty:
        print("  Prior selections file is empty")
        return None
    
    validate_prior_selections(df_prior, triangle_data)
    
    # Ensure consistent types
    df_prior = df_prior[['measure', 'interval', 'selection', 'reasoning']].copy()
    df_prior['measure'] = df_prior['measure'].astype(str)
    df_prior['interval'] = df_prior['interval'].astype(str)
    df_prior['selection'] = df_prior['selection'].astype(float)
    df_prior['reasoning'] = df_prior['reasoning'].fillna('').astype(str)
    
    print(f"  Validated {len(df_prior)} prior selections")
    return df_prior



def read_and_process_expected_loss_rates(triangle_data: pd.DataFrame, file_path: Optional[str] = None) -> Optional[pd.DataFrame]:
    """Read and validate expected loss rates if they exist."""
    if file_path is None:
        if EXPECTED_LOSS_RATES_FILE is None:
            print("  Expected loss rates not configured")
            return None
        file_path = DATA_FILE_PATH + EXPECTED_LOSS_RATES_FILE
    
    if not Path(file_path).exists():
        print("  No expected loss rates file found (optional)")
        return None
    
    print(f"  Found expected loss rates file: {file_path}")
    
    # Read file
    if file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.lower().endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path, engine='openpyxl', engine_kwargs={'data_only': True})
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
    
    # Clean data
    df = df.dropna(subset=['period', 'expected_loss_rate', 'expected_freq'], how='all')
    df = df.dropna(subset=['period'])
    df['period'] = df['period'].astype(str).str.strip()
    df = df.dropna(subset=['expected_loss_rate', 'expected_freq'], how='all')

if __name__ == "__main__":
    """Run the data preparation process."""
    print("="*70)
    print("TRIANGLE DATA PREPARATION SCRIPT")
    print("="*70)
    
    try:
        # Process triangle data
        print("\n[1/3] Processing triangle data...")
        read_and_process_triangles()
        print(f"✓ Triangle data complete: {OUTPUT_PATH}1_triangles.parquet/.csv")
        
        # Load triangles and validate
        print("  Validating combined data...")
        df_triangles = pd.read_parquet(OUTPUT_PATH + "1_triangles.parquet")
        validate_combined_data(df_triangles)
        print(f"  ✓ Validation passed: {len(df_triangles)} rows")
        
        # Process prior selections (optional)
        print("\n[2/3] Processing prior selections (if available)...")
        df_prior = read_and_process_prior_selections(df_triangles)
        if df_prior is not None:
            validate_prior_selections(df_prior, df_triangles)
            output_file = OUTPUT_PATH + "../prior-selections.csv"
            df_prior.to_csv(output_file, index=False)
            print(f"✓ Prior selections validated and saved to: {output_file}")
        
        # Process expected loss rates (optional)
        print("\n[3/3] Processing expected loss rates (if available)...")
        df_expected = read_and_process_expected_loss_rates(df_triangles)
        if df_expected is not None:
            validate_expected_loss_rates(df_expected, df_triangles)
            print(f"✓ Expected loss rates validated and saved to: {OUTPUT_PATH}1_expected_loss_rates.parquet/.csv")
        
        print("\n" + "="*70)
        print("✓ DATA PREPARATION COMPLETE!")
        print("="*70)
        
    except NotImplementedError as e:
        print("\n" + str(e))
        print("\nNEXT STEPS:")
        print("1. Implement read_triangle_data() to read your raw data source")
        print("2. Implement read_and_process_triangles() to combine triangles")
        print("3. Ensure output passes validate_combined_data() checks")
        print("4. Run this script again")
        print("\nSee function docstrings for detailed requirements.")
        print("="*70)
        exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {type(e).__name__}: {e}")
        print("="*70)
        exit(1)
