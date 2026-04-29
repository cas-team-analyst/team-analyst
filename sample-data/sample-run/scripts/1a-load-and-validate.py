"""
Data preparation script for triangle analysis.

Reads raw triangle data, optional prior selections, and optional expected loss rates,
validates them, and saves to standardized format.

Run from scripts/ directory: python 1a-load-and-validate.py
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
    Reads a triangle sheet from the 'Triangle Examples 1.xlsx' file.

    Handles two header layouts:
      - 2-row header (Paid 1, Inc 1): row 0 = label row, row 1 = AY + dev ages
      - 1-row header (Ct 1): row 0 = AY + dev ages

    kwargs expected:
        measure (str): "Paid Loss", "Incurred Loss", "Reported Count", etc.
        unit_type (str): "Dollars" or "Count"
        two_header_rows (bool): True for Paid 1 / Inc 1, False for Ct 1
    """
    measure = kwargs.get("measure", "Unknown")
    unit_type = kwargs.get("unit_type", "Dollars")
    two_header_rows = kwargs.get("two_header_rows", True)
    source_name = kwargs.get("source", sheet_name or "unknown")

    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    if two_header_rows:
        # Row 0: label row (ignore); Row 1: "Accident Year", 11, 23, 35, ...
        header_row = df_raw.iloc[1]
        data = df_raw.iloc[2:].copy()
    else:
        # Row 0: "Accident Year", 11, 23, 35, ...
        header_row = df_raw.iloc[0]
        data = df_raw.iloc[1:].copy()

    # Build column names: first col = 'period', rest = age strings
    cols = ['period'] + [str(int(v)) for v in header_row.iloc[1:]]
    data.columns = cols

    # Drop rows where period is null or non-numeric
    data = data[pd.to_numeric(data['period'], errors='coerce').notna()].copy()
    data['period'] = data['period'].apply(lambda x: str(int(float(x))))

    # Melt to long format
    long = data.melt(id_vars='period', var_name='age', value_name='value')
    long = long[long['value'].notna()].copy()
    long['value'] = long['value'].astype(float)

    long['measure'] = measure
    long['unit_type'] = unit_type
    long['source'] = source_name
    long['details'] = ''

    return long


def read_and_process_triangles():
    """
    Reads Paid Loss, Incurred Loss, Reported Count, and Exposure from
    'Triangle Examples 1.xlsx' and saves to standardized parquet/CSV.

    Source file: raw-data/Triangle Examples 1.xlsx
      - Sheet 'Paid 1'   : Paid Loss triangle (2-row header)
      - Sheet 'Inc 1'    : Incurred Loss triangle (2-row header)
      - Sheet 'Ct 1'     : Reported Count triangle (1-row header)
      - Sheet 'Exposure' : Payroll exposure, 2 columns (Accident Year, Payroll)
    """
    file_path = DATA_FILE_PATH + "Triangle Examples 1.xlsx"

    # --- Paid Loss ---
    paid = read_triangle_data(
        file_path=file_path,
        sheet_name="Paid 1",
        measure="Paid Loss",
        unit_type="Dollars",
        two_header_rows=True,
        source="Triangle Examples 1.xlsx / Paid 1"
    )

    # --- Incurred Loss ---
    incurred = read_triangle_data(
        file_path=file_path,
        sheet_name="Inc 1",
        measure="Incurred Loss",
        unit_type="Dollars",
        two_header_rows=True,
        source="Triangle Examples 1.xlsx / Inc 1"
    )

    # --- Reported Count (Ct 1 has 1-row header, no 'Age of Evaluation' label row) ---
    counts = read_triangle_data(
        file_path=file_path,
        sheet_name="Ct 1",
        measure="Reported Count",
        unit_type="Count",
        two_header_rows=False,
        source="Triangle Examples 1.xlsx / Ct 1"
    )

    # --- Exposure (simple 2-column table) ---
    exp_raw = pd.read_excel(file_path, sheet_name="Exposure", header=0,
                            engine='openpyxl')
    exp_raw.columns = ['period', 'value']
    exp_raw = exp_raw[pd.to_numeric(exp_raw['period'], errors='coerce').notna()].copy()
    exp_raw['period'] = exp_raw['period'].apply(lambda x: str(int(float(x))))
    exp_raw['value'] = pd.to_numeric(exp_raw['value'], errors='coerce')
    exp_raw = exp_raw[exp_raw['value'].notna()].copy()
    exp_raw['age'] = None
    exp_raw['measure'] = 'Exposure'
    exp_raw['unit_type'] = 'Count'
    exp_raw['source'] = 'Triangle Examples 1.xlsx / Exposure'
    exp_raw['details'] = ''
    exposure = exp_raw[['period', 'age', 'value', 'measure', 'unit_type', 'source', 'details']]

    # --- Determine ordered categories from paid triangle ---
    all_periods = sorted(paid['period'].unique(), key=lambda x: int(x))
    all_ages = sorted(paid['age'].unique(), key=lambda x: int(x))

    # --- Combine ---
    all_data = pd.concat([paid, incurred, counts, exposure], ignore_index=True)

    # CRITICAL: Re-apply ordered categoricals after concat
    all_data['period'] = pd.Categorical(
        all_data['period'],
        categories=all_periods,
        ordered=True
    )
    all_data['age'] = pd.Categorical(
        all_data['age'],
        categories=all_ages,
        ordered=True
    )
    all_data['measure'] = all_data['measure'].astype('category')
    all_data['unit_type'] = all_data['unit_type'].astype('category')
    all_data['source'] = all_data['source'].astype('category')

    # Validate
    validate_combined_data(all_data)

    # Save
    all_data.to_parquet(OUTPUT_PATH + "1_triangles.parquet", index=False)
    all_data.to_csv(OUTPUT_PATH + "1_triangles.csv", index=False)


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
