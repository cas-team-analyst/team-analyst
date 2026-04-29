"""
Data preparation script for triangle analysis.

Reads raw triangle data, optional prior selections, and optional expected loss rates,
validates them, and saves to standardized format.

Run from scripts/ directory: python 1a-load-and-validate.py
"""

import pandas as pd
import openpyxl
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

# Source Excel file
EXCEL_FILE = DATA_FILE_PATH + "Triangle Examples 1.xlsx"


def read_triangle_sheet(wb, sheet_name: str, measure: str, unit_type: str,
                         has_age_header_row: bool = True) -> pd.DataFrame:
    """
    Read a triangle sheet from the workbook and return long-format DataFrame.
    
    Args:
        wb: openpyxl workbook (data_only=True)
        sheet_name: name of the sheet
        measure: one of "Paid Loss", "Incurred Loss", "Reported Count", "Closed Count"
        unit_type: "Dollars" or "Count"
        has_age_header_row: True if the sheet has an extra "Age of Evaluation" header row
                            (Paid 1 and Inc 1 have this; Ct 1 does not)
    Returns:
        DataFrame with columns: period, age, value, measure, unit_type, source, details
    """
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))

    if has_age_header_row:
        # Row 0: "Age of Evaluation", None, None, ...
        # Row 1: "Accident Year", 11, 23, 35, ...
        # Row 2+: data
        age_row = rows[1]
        data_rows = rows[2:]
    else:
        # Row 0: "Accident Year", 11, 23, 35, ...
        # Row 1+: data
        age_row = rows[0]
        data_rows = rows[1:]

    # Extract development ages from row header (skip column 0 = "Accident Year")
    ages = [int(a) for a in age_row[1:] if a is not None]

    records = []
    for row in data_rows:
        if row[0] is None:
            continue
        ay = str(int(row[0]))
        for i, age in enumerate(ages):
            col_idx = i + 1  # offset for Accident Year column
            if col_idx >= len(row):
                break
            val = row[col_idx]
            if val is None:
                continue  # upper-right empty cells — skip
            records.append({
                'period': ay,
                'age': str(age),
                'value': float(val),
                'measure': measure,
                'unit_type': unit_type,
                'source': f'{sheet_name} / {EXCEL_FILE}',
                'details': ''
            })

    return pd.DataFrame(records)


def read_exposure_sheet(wb, periods: list) -> pd.DataFrame:
    """
    Read the Exposure sheet. Handles formula cells by computing 2% annual growth.
    Returns long-format exposure DataFrame (age=None, one row per period).
    """
    ws = wb['Exposure']
    rows = list(ws.iter_rows(values_only=True))
    # Row 0: "Accident Year", "Payroll"
    # Row 1+: data (some cells may be formulas → None when data_only=True)

    exp_dict = {}
    base_val = None
    base_ay = None

    for row in rows[1:]:
        if row[0] is None:
            continue
        ay = int(row[0])
        val = row[1]
        if val is not None and not isinstance(val, str):
            # Real numeric value
            exp_dict[ay] = float(val)
            if base_val is None:
                base_val = float(val)
                base_ay = ay
        else:
            # Formula cell or missing — compute from base
            if base_val is not None:
                exp_dict[ay] = base_val * (1.02 ** (ay - base_ay))

    records = []
    for p in periods:
        ay_int = int(p)
        val = exp_dict.get(ay_int)
        if val is not None:
            records.append({
                'period': p,
                'age': None,
                'value': val,
                'measure': 'Exposure',
                'unit_type': 'Count',
                'source': f'Exposure / {EXCEL_FILE}',
                'details': 'Payroll (2% annual growth from 2001 base)'
            })
    return pd.DataFrame(records)


def read_and_process_triangles():
    """Read and combine all triangle measures into standardized long format."""
    print(f"  Reading from: {EXCEL_FILE}")
    wb = openpyxl.load_workbook(EXCEL_FILE, data_only=True)

    # Read triangles
    paid = read_triangle_sheet(wb, 'Paid 1', 'Paid Loss', 'Dollars', has_age_header_row=True)
    incurred = read_triangle_sheet(wb, 'Inc 1', 'Incurred Loss', 'Dollars', has_age_header_row=True)
    count = read_triangle_sheet(wb, 'Ct 1', 'Reported Count', 'Count', has_age_header_row=False)

    wb.close()

    print(f"  Paid Loss:      {len(paid)} observations, {paid['period'].nunique()} AYs")
    print(f"  Incurred Loss:  {len(incurred)} observations, {incurred['period'].nunique()} AYs")
    print(f"  Reported Count: {len(count)} observations, {count['period'].nunique()} AYs")

    # Derive ordered age categories from the paid triangle (most complete)
    age_cats = sorted(paid['age'].unique(), key=lambda x: int(x))
    period_cats = sorted(paid['period'].unique(), key=lambda x: int(x))

    # Read exposure (using paid triangle periods)
    wb = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
    exposure = read_exposure_sheet(wb, period_cats)
    wb.close()
    print(f"  Exposure:       {len(exposure)} periods")

    # Combine all
    all_data = pd.concat([paid, incurred, count, exposure], ignore_index=True)

    # Apply ordered categorical types
    all_data['period'] = pd.Categorical(
        all_data['period'],
        categories=period_cats,
        ordered=True
    )
    all_data['age'] = pd.Categorical(
        all_data['age'],
        categories=age_cats,
        ordered=True
    )
    all_data['measure'] = all_data['measure'].astype('category')
    all_data['unit_type'] = all_data['unit_type'].astype('category')
    all_data['source'] = all_data['source'].astype('category')

    # Validate
    validate_combined_data(all_data)

    # Save
    out_parquet = OUTPUT_PATH + "1_triangles.parquet"
    out_csv = OUTPUT_PATH + "1_triangles.csv"
    all_data.to_parquet(out_parquet, index=False)
    all_data.to_csv(out_csv, index=False)

    print(f"  Saved {len(all_data)} total rows → {out_parquet}")


def read_and_process_prior_selections(triangle_data: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Read and validate prior selections if they exist."""
    prior_file = OUTPUT_PATH + "../prior-selections.csv"

    if not Path(prior_file).exists():
        print("  No prior selections file found (optional)")
        return None

    print(f"  Found prior selections file: {prior_file}")
    df_prior = pd.read_csv(prior_file)

    required = ['measure', 'interval', 'selection']
    if not all(col in df_prior.columns for col in required):
        raise ValueError(f"Prior selections must have columns: {', '.join(required)}")

    if 'reasoning' not in df_prior.columns:
        df_prior['reasoning'] = ''

    if df_prior.empty:
        print("  Prior selections file is empty")
        return None

    validate_prior_selections(df_prior, triangle_data)

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

    if file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.lower().endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path, engine='openpyxl', engine_kwargs={'data_only': True})
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

    df = df.dropna(subset=['period', 'expected_loss_rate', 'expected_freq'], how='all')
    df = df.dropna(subset=['period'])
    df['period'] = df['period'].astype(str).str.strip()
    df = df.dropna(subset=['expected_loss_rate', 'expected_freq'], how='all')
    return df


if __name__ == "__main__":
    """Run the data preparation process."""
    print("="*70)
    print("TRIANGLE DATA PREPARATION SCRIPT")
    print("="*70)

    try:
        print("\n[1/3] Processing triangle data...")
        read_and_process_triangles()
        print(f"  Triangle data complete: {OUTPUT_PATH}1_triangles.parquet/.csv")

        print("  Validating combined data...")
        df_triangles = pd.read_parquet(OUTPUT_PATH + "1_triangles.parquet")
        validate_combined_data(df_triangles)
        print(f"  Validation passed: {len(df_triangles)} rows")

        print("\n[2/3] Processing prior selections (if available)...")
        df_prior = read_and_process_prior_selections(df_triangles)
        if df_prior is not None:
            validate_prior_selections(df_prior, df_triangles)
            output_file = OUTPUT_PATH + "../prior-selections.csv"
            df_prior.to_csv(output_file, index=False)
            print(f"  Prior selections validated and saved to: {output_file}")

        print("\n[3/3] Processing expected loss rates (if available)...")
        df_expected = read_and_process_expected_loss_rates(df_triangles)
        if df_expected is not None:
            validate_expected_loss_rates(df_expected, df_triangles)
            print(f"  Expected loss rates validated")

        print("\n" + "="*70)
        print("DATA PREPARATION COMPLETE!")
        print("="*70)

    except Exception as e:
        import traceback
        print(f"\nERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        print("="*70)
        exit(1)
