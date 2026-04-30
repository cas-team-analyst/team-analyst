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
    Reads a triangle from 'Triangle Examples 1.xlsx'.

    Sheet layout (Paid 1 / Inc 1):
      Row 1: "Age of Evaluation" label row (skipped)
      Row 2: "Accident Year", 11, 23, 35, ... (age headers)
      Row 3+: AY, values...

    Sheet layout (Ct 1):
      Row 1: "Accident Year", 11, 23, 35, ... (age headers, no extra label row)
      Row 2+: AY, values...
    """
    measure   = kwargs.get("measure", "Paid Loss")
    unit_type = kwargs.get("unit_type", "Dollars")
    source    = kwargs.get("source", sheet_name or "unknown")

    wb = pd.ExcelFile(file_path, engine="openpyxl")
    raw = pd.read_excel(wb, sheet_name=sheet_name, header=None)

    # Find the header row: the row whose first cell contains "Accident Year"
    header_row = None
    for i, row in raw.iterrows():
        if str(row.iloc[0]).strip().lower() == "accident year":
            header_row = i
            break
    if header_row is None:
        raise ValueError(f"Could not find 'Accident Year' row in sheet '{sheet_name}'")

    # Ages are columns 1+ in the header row
    age_row  = raw.iloc[header_row]
    ages     = [str(int(a)) for a in age_row.iloc[1:] if pd.notna(a) and isinstance(a, (int, float))]

    # Data rows follow the header
    data_rows = raw.iloc[header_row + 1:].reset_index(drop=True)

    records = []
    for _, row in data_rows.iterrows():
        ay = row.iloc[0]
        if pd.isna(ay) or not isinstance(ay, (int, float)):
            continue
        period = str(int(ay))
        for j, age_label in enumerate(ages):
            val = row.iloc[j + 1]
            if pd.notna(val) and isinstance(val, (int, float)):
                records.append({
                    "period":    period,
                    "age":       age_label,
                    "value":     float(val),
                    "measure":   measure,
                    "unit_type": unit_type,
                    "source":    source,
                    "details":   "",
                })

    df = pd.DataFrame(records)

    periods_ordered = sorted(df["period"].unique(), key=lambda x: int(x))
    ages_ordered    = sorted(df["age"].unique(), key=lambda x: int(x))

    df["period"]    = pd.Categorical(df["period"],    categories=periods_ordered, ordered=True)
    df["age"]       = pd.Categorical(df["age"],       categories=ages_ordered,    ordered=True)
    df["measure"]   = df["measure"].astype("category")
    df["unit_type"] = df["unit_type"].astype("category")
    df["source"]    = df["source"].astype("category")

    return df


def read_and_process_triangles():
    """
    Reads Paid Loss, Incurred Loss, Reported Count, and Payroll Exposure
    from 'Triangle Examples 1.xlsx' and writes combined parquet/csv.

    Data file: raw-data/Triangle Examples 1.xlsx
      Sheet 'Paid 1'    -> Paid Loss (Dollars)
      Sheet 'Inc 1'     -> Incurred Loss (Dollars)
      Sheet 'Ct 1'      -> Reported Count (Count) - generic count header, assumed reported
      Sheet 'Exposure'  -> Payroll exposure per AY (Dollars)

    Ages are in months: 11, 23, 35, ... 287 (annual development, non-standard start at 11).
    Accident years: 2001-2024.
    """
    data_file = DATA_FILE_PATH + "Triangle Examples 1.xlsx"

    print(f"  Reading Paid Loss from 'Paid 1'...")
    paid = read_triangle_data(data_file, sheet_name="Paid 1",
                              measure="Paid Loss", unit_type="Dollars", source="Paid 1")

    print(f"  Reading Incurred Loss from 'Inc 1'...")
    incurred = read_triangle_data(data_file, sheet_name="Inc 1",
                                  measure="Incurred Loss", unit_type="Dollars", source="Inc 1")

    print(f"  Reading Reported Count from 'Ct 1'...")
    rpt_count = read_triangle_data(data_file, sheet_name="Ct 1",
                                   measure="Reported Count", unit_type="Count", source="Ct 1")

    print(f"  Reading Payroll Exposure from 'Exposure'...")
    # Use data_only=True so Excel formulas return cached values
    exp_raw = pd.read_excel(data_file, sheet_name="Exposure", header=0,
                            engine="openpyxl", engine_kwargs={"data_only": True})
    exp_raw.columns = ["period", "value"]
    exp_raw = exp_raw.dropna(subset=["period", "value"])
    exp_raw["period"] = exp_raw["period"].apply(lambda x: str(int(x)))

    age_categories = paid["age"].cat.categories.tolist()
    period_categories = paid["period"].cat.categories.tolist()

    exposure_records = []
    for _, row in exp_raw.iterrows():
        if row["period"] in period_categories:
            exposure_records.append({
                "period":    row["period"],
                "age":       None,
                "value":     float(row["value"]),
                "measure":   "Exposure",
                "unit_type": "Dollars",
                "source":    "Exposure",
                "details":   "Payroll",
            })
    exposure = pd.DataFrame(exposure_records)

    # Combine all measures
    all_data = pd.concat([paid, incurred, rpt_count, exposure], ignore_index=True)

    # Re-apply ordered categoricals after concat
    all_data["period"] = pd.Categorical(
        all_data["period"], categories=period_categories, ordered=True
    )
    all_data["age"] = pd.Categorical(
        all_data["age"], categories=age_categories, ordered=True
    )
    all_data["measure"]   = all_data["measure"].astype("category")
    all_data["unit_type"] = all_data["unit_type"].astype("category")
    all_data["source"]    = all_data["source"].astype("category")

    validate_combined_data(all_data)

    all_data.to_parquet(OUTPUT_PATH + "1_triangles.parquet", index=False)
    all_data.to_csv(OUTPUT_PATH + "1_triangles.csv", index=False)
    print(f"  Saved {len(all_data)} rows to processed-data/")


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
