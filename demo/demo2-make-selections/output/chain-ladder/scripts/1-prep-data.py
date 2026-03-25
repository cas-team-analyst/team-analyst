"""
goal: Get data in standard format to simplify downstream operations.
contents:
    read_and_process_triangles(): Reads Inc, Pd, Count sheets from the demo Excel file.
    read_and_process_prior_selections(): Reads prior LDF selections from the last row of each sheet.
    validate_data(): Validates the output format (do not modify).

usage: Run from project root:
    .venv/Scripts/Activate.ps1; python demo/demo2-make-selections/output/chain-ladder/scripts/1-prep-data.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
DATA_FILE_PATH = str(SCRIPT_DIR / "../../../data/Claude Agent Triangles 5 Demo Data.xlsx")
OUTPUT_PATH = str(SCRIPT_DIR / "../data/") + "/"
METHOD_ID = "chainladder"

# Map sheet name -> (measure label, unit_type)
SHEET_CONFIG = [
    ("Inc",   "Incurred Loss",   "Dollars"),
    ("Pd",    "Paid Loss",       "Dollars"),
    ("Count", "Reported Count",  "Count"),
]

PRIOR_LABEL_SUBSTRING = "prior"  # case-insensitive match for prior selections row


def read_and_process_triangles():
    """
    Read triangle sheets from the Excel file, convert to long format, and save output.
    Filters out the Prior Age-to-Age Selections row from triangle data.
    """

    def read_triangle_data(file_path, sheet_name, header_row, period_column,
                           first_data_column, data_type, unit_type, details=None):
        """
        Read a single triangle sheet and convert to long format.

        Args:
            file_path: Path to the Excel file
            header_row: Row number (1-indexed) containing the age headers
            period_column: Column number (1-indexed) containing the period values
            first_data_column: Column number (1-indexed) of the first age data column
            data_type: Type of data ('Paid Loss', 'Incurred Loss', 'Reported Count', etc.)
            unit_type: 'Count' or 'Dollars'
            sheet_name: Sheet name in the Excel file
            details: Optional extra info about this data

        Returns:
            DataFrame with columns: period, age, value, measure, unit_type, source, details
        """
        header_row_idx = header_row - 1     # 0-indexed
        period_col_idx = period_column - 1  # 0-indexed
        first_data_col_idx = first_data_column - 1  # 0-indexed

        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, dtype=str, engine='openpyxl')
        source = f"{file_path} - Sheet: {sheet_name}"

        # Extract age headers from the header row
        age_columns = range(first_data_col_idx, df.shape[1])
        ages = []
        for col in age_columns:
            val = df.iloc[header_row_idx, col]
            if pd.notna(val) and str(val).strip() not in ('', 'nan'):
                ages.append(str(val).strip())
            else:
                break

        data_start_row = header_row_idx + 1
        data_rows = []
        periods = []

        for row_idx in range(data_start_row, len(df)):
            period_val = df.iloc[row_idx, period_col_idx]
            if pd.isna(period_val) or str(period_val).strip() in ('', 'nan'):
                continue

            period = str(period_val).strip()

            # Skip the prior selections row
            if PRIOR_LABEL_SUBSTRING in period.lower():
                continue

            if period not in periods:
                periods.append(period)

            for age_idx, age in enumerate(ages):
                data_col_idx = first_data_col_idx + age_idx
                value = df.iloc[row_idx, data_col_idx]
                if pd.notna(value) and str(value).strip() not in ('', 'nan'):
                    data_rows.append({
                        'period': period,
                        'age': age,
                        'value': float(value),
                        'measure': data_type,
                        'unit_type': unit_type,
                        'source': source,
                        'details': details,
                    })

        if not data_rows:
            return pd.DataFrame({
                'period': pd.Series(dtype='category'),
                'age': pd.Series(dtype='category'),
                'value': pd.Series(dtype='float64'),
                'measure': pd.Series(dtype='category'),
                'unit_type': pd.Series(dtype='category'),
                'source': pd.Series(dtype='category'),
                'details': pd.Series(dtype='object'),
            })

        result_df = pd.DataFrame(data_rows)
        result_df['period'] = pd.Categorical(result_df['period'], categories=periods, ordered=True)
        result_df['age'] = pd.Categorical(result_df['age'], categories=ages, ordered=True)
        result_df['measure'] = result_df['measure'].astype('category')
        result_df['unit_type'] = result_df['unit_type'].astype('category')
        result_df['source'] = result_df['source'].astype('category')
        result_df['details'] = result_df['details'].astype('object')
        return result_df

    dfs = []
    for sheet_name, measure, unit_type in SHEET_CONFIG:
        df = read_triangle_data(
            file_path=DATA_FILE_PATH,
            sheet_name=sheet_name,
            header_row=2,          # Row 2 (1-indexed): "Fiscal Accident Year", 15, 27, ...
            period_column=1,       # Col A: accident year labels
            first_data_column=2,   # Col B: first development age
            data_type=measure,
            unit_type=unit_type,
            details=f"Demo data - {sheet_name} sheet"
        )
        print(f"  {sheet_name}: {len(df)} rows, {df['period'].nunique()} periods, {df['age'].nunique()} ages")
        dfs.append(df)

    all_data = pd.concat(dfs, ignore_index=True)

    # Preserve categorical ordering from first triangle (they should all match)
    age_categories = dfs[0]['age'].cat.categories.tolist()
    period_categories = dfs[0]['period'].cat.categories.tolist()
    all_data['period'] = pd.Categorical(all_data['period'], categories=period_categories, ordered=True)
    all_data['age'] = pd.Categorical(all_data['age'], categories=age_categories, ordered=True)
    all_data['measure'] = all_data['measure'].astype('category')
    all_data['unit_type'] = all_data['unit_type'].astype('category')
    all_data['source'] = all_data['source'].astype('category')

    validate_data(all_data)

    all_data.to_parquet(OUTPUT_PATH + f"1_{METHOD_ID}_prepped.parquet", index=False)
    all_data.to_csv(OUTPUT_PATH + f"1_{METHOD_ID}_prepped.csv", index=False)


def read_and_process_prior_selections(triangle_data: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Read prior LDF selections from the last row of each Excel sheet.

    The prior selections row is labeled "Prior Age-to-Age Selections" (or similar).
    The LDF at column position for age[i] represents the interval age[i]-age[i+1].

    Args:
        triangle_data: DataFrame with processed triangle data (used for validation)

    Returns:
        DataFrame with columns: measure, interval, selection, reasoning
    """
    all_prior = []

    for sheet_name, measure, _ in SHEET_CONFIG:
        df_raw = pd.read_excel(
            DATA_FILE_PATH, sheet_name=sheet_name, header=None, dtype=str, engine='openpyxl'
        )

        # Ages are in row 1 (0-indexed), columns 1+ (skip col A which is the period label)
        ages_raw = df_raw.iloc[1, 1:].values
        ages = [str(v).strip() for v in ages_raw if pd.notna(v) and str(v).strip() not in ('', 'nan')]

        # Find the prior selections row
        prior_row_values = None
        for row_idx in range(len(df_raw)):
            cell_val = str(df_raw.iloc[row_idx, 0]).strip()
            if PRIOR_LABEL_SUBSTRING in cell_val.lower():
                prior_row_values = df_raw.iloc[row_idx, 1:].values
                break

        if prior_row_values is None:
            print(f"  WARNING: No prior selections row found in sheet '{sheet_name}'")
            continue

        # The LDF at position i (age[i]) is the factor for interval age[i]-age[i+1]
        for i in range(len(ages) - 1):
            val = prior_row_values[i] if i < len(prior_row_values) else None
            if val is not None and pd.notna(val) and str(val).strip() not in ('', 'nan'):
                interval = f"{ages[i]}-{ages[i+1]}"
                all_prior.append({
                    'measure': measure,
                    'interval': interval,
                    'selection': float(val),
                    'reasoning': 'Prior selection from previous analysis',
                })

        print(f"  {sheet_name}: found {sum(1 for r in all_prior if r['measure'] == measure)} prior selections")

    if not all_prior:
        print("  No prior selections found")
        return None

    df_prior = pd.DataFrame(all_prior)

    # Validation
    errors = []
    required_columns = ['measure', 'interval', 'selection']
    for col in required_columns:
        null_count = df_prior[col].isna().sum()
        if null_count > 0:
            errors.append(f"'{col}' contains {null_count} null value(s)")

    if not errors:
        valid_measures = triangle_data['measure'].cat.categories.tolist()
        invalid_measures = df_prior[~df_prior['measure'].isin(valid_measures)]['measure'].unique()
        if len(invalid_measures) > 0:
            errors.append(f"Invalid measures: {', '.join(invalid_measures)}")

        age_categories = triangle_data['age'].cat.categories.tolist()
        valid_intervals = [f"{age_categories[i]}-{age_categories[i+1]}" for i in range(len(age_categories) - 1)]
        invalid_intervals = df_prior[~df_prior['interval'].isin(valid_intervals)]['interval'].unique()
        if len(invalid_intervals) > 0:
            errors.append(f"Invalid intervals: {', '.join(invalid_intervals)}")

    if errors:
        raise ValueError("Prior selections validation failed!\n" + "\n".join(f"  - {e}" for e in errors))

    df_prior = df_prior[['measure', 'interval', 'selection', 'reasoning']].copy()
    df_prior['selection'] = df_prior['selection'].astype(float)
    df_prior['reasoning'] = df_prior['reasoning'].fillna('').astype(str)
    print(f"  Total: {len(df_prior)} prior selections validated")
    return df_prior


def validate_data(df: pd.DataFrame) -> None:
    """
    Validate the prepped data format. Do not modify - other assets depend on this format.
    """
    errors = []
    if df.empty:
        raise ValueError("Data validation failed!\n\nERRORS:\n  - DataFrame is empty")

    required_columns = ['period', 'age', 'value', 'measure', 'unit_type']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")

    if 'period' in df.columns and df['period'].dtype.name != 'category':
        errors.append("'period' column should be categorical type")
    if 'age' in df.columns and df['age'].dtype.name != 'category':
        errors.append("'age' column should be categorical type")
    if 'period' in df.columns and df['period'].dtype.name == 'category':
        if not df['period'].cat.ordered:
            errors.append("'period' categorical must be ordered (ordered=True)")
    if 'age' in df.columns and df['age'].dtype.name == 'category':
        if not df['age'].cat.ordered:
            errors.append("'age' categorical must be ordered (ordered=True)")
    if 'value' in df.columns and not pd.api.types.is_numeric_dtype(df['value']):
        errors.append("'value' column must be numeric")
    if 'measure' in df.columns and df['measure'].dtype.name != 'category':
        errors.append("'measure' column should be categorical type")
    if 'unit_type' in df.columns and df['unit_type'].dtype.name != 'category':
        errors.append("'unit_type' column should be categorical type")

    for col in ['period', 'age', 'value', 'measure']:
        if col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                errors.append(f"Column '{col}' contains {null_count} null value(s)")

    if 'unit_type' in df.columns:
        valid_unit_types = ['Count', 'Dollars']
        invalid_units = df[~df['unit_type'].isin(valid_unit_types)]['unit_type'].unique()
        if len(invalid_units) > 0:
            errors.append(f"Unexpected unit_type value(s): {', '.join(map(str, invalid_units))}")

    if 'measure' in df.columns:
        valid_measures = ['Incurred Loss', 'Paid Loss', 'Reported Count', 'Closed Count']
        invalid_measures = df[~df['measure'].isin(valid_measures)]['measure'].unique()
        if len(invalid_measures) > 0:
            errors.append(f"Unexpected measure value(s): {', '.join(map(str, invalid_measures))}")

    if all(col in df.columns for col in ['source', 'period', 'age', 'measure']):
        duplicates = df.duplicated(subset=['source', 'period', 'age', 'measure'], keep=False)
        if duplicates.any():
            errors.append(f"Found {duplicates.sum()} duplicate source/period/age/measure combinations")

    if errors:
        raise ValueError("Data validation failed!\n\nERRORS:\n" + "\n".join(f"  - {e}" for e in errors))


if __name__ == "__main__":
    print("Starting data preparation for Chain Ladder...")

    print("\nReading triangle data...")
    read_and_process_triangles()
    print(f"\nTriangle data saved:")
    print(f"  Parquet: {OUTPUT_PATH}1_{METHOD_ID}_prepped.parquet")
    print(f"  CSV:     {OUTPUT_PATH}1_{METHOD_ID}_prepped.csv")

    df_triangles = pd.read_parquet(OUTPUT_PATH + f"1_{METHOD_ID}_prepped.parquet")
    print(f"\nLoaded {len(df_triangles)} rows, measures: {df_triangles['measure'].unique().tolist()}")
    print(f"Periods: {df_triangles['period'].cat.categories.tolist()}")
    print(f"Ages: {df_triangles['age'].cat.categories.tolist()}")

    print("\nReading prior selections...")
    df_prior = read_and_process_prior_selections(df_triangles)

    if df_prior is not None:
        output_file = OUTPUT_PATH + "../prior-selections.csv"
        df_prior.to_csv(output_file, index=False)
        print(f"  Saved prior selections: {output_file}")
        print(df_prior.groupby('measure')['selection'].describe().round(4))

    print("\nData preparation complete!")
