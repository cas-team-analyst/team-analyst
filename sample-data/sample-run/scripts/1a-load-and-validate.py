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
    Read a triangle from the Excel file in the format used by Triangle Examples 1.xlsx.

    Supports two layouts:
    - two_header_rows=True  (Paid 1, Inc 1): Row 1 is label, Row 2 has ages, data starts row 3
    - two_header_rows=False (Ct 1):           Row 1 has ages,                data starts row 2

    Additional kwargs:
        measure (str): e.g. "Paid Loss", "Incurred Loss", "Reported Count"
        unit_type (str): "Dollars" or "Count"
        two_header_rows (bool): default True
    """
    import openpyxl
    measure = kwargs.get("measure", "Paid Loss")
    unit_type = kwargs.get("unit_type", "Dollars")
    two_header_rows = kwargs.get("two_header_rows", True)
    source = kwargs.get("source", sheet_name or "unknown")

    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))

    if two_header_rows:
        # Row index 1 (0-based) has ages; row index 0 is label row
        age_row = rows[1]
        data_rows = rows[2:]
    else:
        age_row = rows[0]
        data_rows = rows[1:]

    # Extract age labels — skip col 0 (which is "Accident Year")
    ages = []
    for v in age_row[1:]:
        if v is None:
            break
        ages.append(str(int(float(v))))

    records = []
    for row in data_rows:
        if row[0] is None or not isinstance(row[0], (int, float)):
            continue
        period = str(int(row[0]))
        for i, age in enumerate(ages):
            val = row[i + 1]
            if val is None:
                continue
            try:
                val = float(val)
            except (TypeError, ValueError):
                continue
            records.append({
                "period": period,
                "age": age,
                "value": val,
                "measure": measure,
                "unit_type": unit_type,
                "source": source,
                "details": "",
            })

    return pd.DataFrame(records)


def read_and_process_triangles():
    """
    Reads Paid Loss, Incurred Loss, Reported Count, and Exposure from
    Triangle Examples 1.xlsx and saves to the canonical parquet format.
    """
    import openpyxl
    file_path = DATA_FILE_PATH + "Triangle Examples 1.xlsx"

    print(f"  Reading data from: {file_path}")

    # --- Paid Loss ---
    paid = read_triangle_data(file_path, sheet_name="Paid 1",
                              measure="Paid Loss", unit_type="Dollars",
                              two_header_rows=True, source="Paid 1")
    print(f"  Paid Loss: {len(paid)} rows, {paid['period'].nunique()} accident years")

    # --- Incurred Loss ---
    incurred = read_triangle_data(file_path, sheet_name="Inc 1",
                                  measure="Incurred Loss", unit_type="Dollars",
                                  two_header_rows=True, source="Inc 1")
    print(f"  Incurred Loss: {len(incurred)} rows, {incurred['period'].nunique()} accident years")

    # --- Reported Count (Ct 1 has no separate Age of Evaluation header row) ---
    count = read_triangle_data(file_path, sheet_name="Ct 1",
                               measure="Reported Count", unit_type="Count",
                               two_header_rows=False, source="Ct 1")
    print(f"  Reported Count: {len(count)} rows, {count['period'].nunique()} accident years")

    # --- Exposure (Payroll) ---
    # The Exposure sheet has formula-based values; use data_only=True to get results
    # 2001 is actual; subsequent years use =B(n-1)*1.02 — compute from 2001 base
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws_exp = wb["Exposure"]
    exp_rows = list(ws_exp.iter_rows(min_row=2, values_only=True))

    base_value = None
    exposure_records = []
    for row in exp_rows:
        if row[0] is None:
            continue
        ay = int(float(row[0]))
        raw_val = row[1]
        if isinstance(raw_val, (int, float)) and raw_val is not None:
            base_value = float(raw_val)
            exposure_records.append({"period": str(ay), "value": base_value})
        elif base_value is not None:
            # Formula-driven: compute 2% annual growth from prior year
            base_value = base_value * 1.02
            exposure_records.append({"period": str(ay), "value": base_value})

    exposure_df = pd.DataFrame(exposure_records)
    exposure_df["measure"] = "Exposure"
    exposure_df["unit_type"] = "Count"
    exposure_df["source"] = "Exposure"
    exposure_df["details"] = ""
    exposure_df["age"] = None
    print(f"  Exposure: {len(exposure_df)} accident years (payroll)")

    # --- Derive ordered categories from paid triangle ---
    all_periods = sorted(set(paid["period"].tolist()), key=int)
    all_ages = sorted(set(paid["age"].tolist()), key=int)

    # Combine all data
    all_data = pd.concat([paid, incurred, count, exposure_df], ignore_index=True)

    # Apply ordered categoricals
    all_data["period"] = pd.Categorical(all_data["period"], categories=all_periods, ordered=True)
    all_data["age"] = pd.Categorical(all_data["age"], categories=all_ages, ordered=True)
    all_data["measure"] = all_data["measure"].astype("category")
    all_data["unit_type"] = all_data["unit_type"].astype("category")
    all_data["source"] = all_data["source"].astype("category")

    # Validate
    print("  Running validation...")
    validate_combined_data(all_data)
    print("  ✓ Validation passed")

    # Save
    import os
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    all_data.to_parquet(OUTPUT_PATH + "1_triangles.parquet", index=False)
    all_data.to_csv(OUTPUT_PATH + "1_triangles.csv", index=False)
    print(f"  Saved: {OUTPUT_PATH}1_triangles.parquet / .csv")


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
