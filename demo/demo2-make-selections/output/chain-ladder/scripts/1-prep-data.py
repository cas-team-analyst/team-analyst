"""
goal: Get data in standard format to simplify downstream operations. 
contents: 
    read_and_process_data(): Example function for reading, processing, validating, and saving the data necessary for Chain Ladder. This function can be replaced with one that works with your raw data.
    validate_data(): Validate the data format. You should not typically modify this, as other assets depend on this format.

run-note: This script must be run from its own directory for relative paths to work correctly.
    cd .claude/skills/reserving-methods/assets/chain-ladder
    python 1-prep-data.py
"""

import pandas as pd
from typing import Optional

# Replace then when using this file in an actual project:
DATA_FILE_PATH = "../../../data/"
OUTPUT_PATH = "../data/"
METHOD_ID = "chainladder"
DATA_FILE = "Triangle Examples 1.xlsx"

def read_and_process_data():
    """
    Read raw data, process it into a standardized analytical format, and save to output.
    """    

    # Here is a common implementation for reading and processing triangle data.
    # However, data may come in a different format so you may need to replace this code.

    # Define a reusable function for reading each file/sheet.
    def read_triangle_data(
        file_path: str,
        header_row: int,
        period_column: int,
        first_data_column: int,
        data_type: str,
        unit_type: str,
        sheet_name: Optional[str]= None, 
        details: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Read a single triangle sheet and convert to long format.
        
        Args:
            file_path: Path to the Excel file
            header_row: Row number (1-indexed) containing the age headers
            period_column: Column number (1-indexed) containing the period values
            first_data_column: Column number (1-indexed) of the first age data column (in case there are empty columns before the data starts)
            data_type: Type of data (e.g., 'Paid', 'Incurred', 'Reported Claims')
            unit_type: Unit type for the data ('Count' or 'Dollars')
            sheet_name: Name of the sheet to read. Leave as None if not an Excel file.
            details: Additional details about the data like if the triangle represents a specific business segment, etc.
        
        Returns:
            DataFrame with columns: 
                period (ordinal category): the time period the row of the triangle represents (2001, 2022 Q1, 7/1/2023-6/30/2024, etc.)
                age (ordinal category): the maturity of the period that the column of the triangle represents (2, 12, etc.)
                value (numeric): numeric value from the triangle
                measure (category): type of measure the value represents (Incurred Loss, Paid Loss, Reported Claims, Closed Claims, Exposure, etc.)
                unit_type (category): Count or Dollars
                source: Source of the data for auditing purposes. 
                details: Additional details about the data like if the triangle represents a specific business segment, etc.
        """
        header_row = header_row - 1  # Convert to 0-indexed
        period_col = period_column - 1  # Convert to 0-indexed
        first_data_col = first_data_column - 1  # Convert to 0-indexed
        
        # Read the entire sheet/file as a DataFrame
        # Read all columns as strings to prevent date conversion
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(
                file_path,
                header=None,
                dtype=str
            )
            source = file_path
        else:
            # Assume Excel format (.xlsx, .xls)
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=None,
                dtype=str,
                engine='openpyxl'
            )
            source = f'{file_path} - Sheet: {sheet_name}'
        
        # Extract age headers from header row in their original order
        age_columns = df.columns[first_data_col:]
        ages = []
        for col in age_columns:
            # Get the value from the header row
            val = df.iloc[header_row, col]
            if pd.notna(val) and str(val).strip():
                age_str = str(val).strip()
                # Store age in original order from the data source
                ages.append(age_str)
            else:
                break  # Stop at first empty column
        
        # Get period column index
        period_col_idx = period_col
        
        # Read data starting after header row
        data_start_row = header_row + 1
        data_rows = []
        periods = []  # Track periods in order of appearance
        
        for row_idx in range(data_start_row, len(df)):
            period_val = df.iloc[row_idx, period_col_idx]
            
            # Skip if period is null or empty
            if pd.isna(period_val) or str(period_val).strip() == '':
                continue
            
            period = str(period_val).strip()
            
            # Track period order (only add if not already seen)
            if period not in periods:
                periods.append(period)
            
            # Extract values for each age
            for age_idx, age in enumerate(ages):
                data_col_idx = first_data_col + age_idx
                value = df.iloc[row_idx, data_col_idx]
                
                # Only include non-null values
                if pd.notna(value) and str(value).strip() != '':
                    value_float = float(value)
                    
                    data_rows.append({
                        'period': period,
                        'age': age,  # Categorical will preserve order of first appearance
                        'value': value_float,
                        'measure': data_type,
                        'unit_type': unit_type,
                        'source': source,
                        'details': details
                    })
        
        if not data_rows:
            return pd.DataFrame({
                'period': pd.Series(dtype='category'), 
                'age': pd.Series(dtype='category'),
                'value': pd.Series(dtype='float64'), 
                'measure': pd.Series(dtype='category'), 
                'unit_type': pd.Series(dtype='category'),
                'source': pd.Series(dtype='category'),
                'details': pd.Series(dtype='object')
            })
        
        result_df = pd.DataFrame(data_rows)
        result_df['period'] = pd.Categorical(result_df['period'], categories=periods, ordered=True)
        result_df['age'] = pd.Categorical(result_df['age'], categories=ages, ordered=True)
        result_df['measure'] = result_df['measure'].astype('category')
        result_df['unit_type'] = result_df['unit_type'].astype('category')
        result_df['source'] = result_df['source'].astype('category')
        result_df['details'] = result_df['details'].astype('object')

        return result_df

    # Read each sheet.
    # Inc 1 and Paid 1 have a merged "Age of Evaluation" title in row 1,
    # with actual ages (11, 23, 35...) in row 2 — so header_row=2.
    # Ct 1 has ages directly in row 1 — so header_row=1.
    incurred = read_triangle_data(
        file_path=DATA_FILE_PATH + DATA_FILE,
        sheet_name="Inc 1",
        header_row=2,
        period_column=1,
        first_data_column=2,
        data_type="Incurred Loss",
        unit_type="Dollars",
        details="WC incurred losses"
    )

    paid = read_triangle_data(
        file_path=DATA_FILE_PATH + DATA_FILE,
        sheet_name="Paid 1",
        header_row=2,
        period_column=1,
        first_data_column=2,
        data_type="Paid Loss",
        unit_type="Dollars",
        details="WC paid losses"
    )

    reported = read_triangle_data(
        file_path=DATA_FILE_PATH + DATA_FILE,
        sheet_name="Ct 1",
        header_row=1,
        period_column=1,
        first_data_column=2,
        data_type="Reported Count",
        unit_type="Count",
        details="WC claim counts"
    )

    # Concatenate all dataframes
    all_data = pd.concat([incurred, paid, reported], ignore_index=True)

    # Get unique age and period categories in the order they first appear (should be consistent across all triangles)
    age_categories = incurred['age'].cat.categories.tolist()
    period_categories = incurred['period'].cat.categories.tolist()
    
    # Ensure categorical dtypes are preserved after concat with correct ordering
    all_data['period'] = pd.Categorical(all_data['period'], categories=period_categories, ordered=True)
    all_data['age'] = pd.Categorical(all_data['age'], categories=age_categories, ordered=True)
    all_data['measure'] = pd.Categorical(all_data['measure'], categories=['Incurred Loss', 'Paid Loss', 'Reported Count'], ordered=False)
    all_data['unit_type'] = all_data['unit_type'].astype('category')
    all_data['source'] = all_data['source'].astype('category')

    # Validate the format is correct. 
    #! AVOID CHANGING THIS, OUTPUT DATA FORMAT DOES NOT TYPICALLY CHANGE.
    validate_data(all_data)

    # Save to output - parquet preserves categorical ordering, CSV for inspection
    #! AVOID CHANGING THIS, OUTPUT DATA FORMAT DOES NOT TYPICALLY CHANGE.
    all_data.to_parquet(OUTPUT_PATH + f"1_{METHOD_ID}_prepped.parquet", index=False)
    all_data.to_csv(OUTPUT_PATH + f"1_{METHOD_ID}_prepped.csv", index=False)


def validate_data(df: pd.DataFrame) -> None:
    """
    Validate the prepped data to ensure it meets expected format and quality standards.
    Raises ValueError if validation fails with detailed error information.
    
    Args:
        df: DataFrame to validate
    
    Raises:
        ValueError: If validation fails, with detailed error, warning, and summary information
    """

    #! AVOID CHANGING THIS, OUTPUT DATA FORMAT DOES NOT TYPICALLY CHANGE.

    errors = []
    
    # Check if DataFrame is empty
    if df.empty:
        raise ValueError("Data validation failed!\n\nERRORS:\n  - DataFrame is empty")
    
    # Check required columns
    required_columns = ['period', 'age', 'value', 'measure', 'unit_type']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Check data types
    if 'period' in df.columns and df['period'].dtype.name != 'category':
        errors.append("'period' column should be categorical type")
    
    if 'age' in df.columns and df['age'].dtype.name != 'category':
        errors.append("'age' column should be categorical type")
    
    # Check that categorical columns are ordered (critical for downstream operations)
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
    
    # Check for null values in critical columns
    for col in ['period', 'age', 'value', 'measure']:
        if col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                errors.append(f"Column '{col}' contains {null_count} null value(s)")
    
    # Check unit_type values
    if 'unit_type' in df.columns:
        valid_unit_types = ['Count', 'Dollars']
        invalid_units = df[~df['unit_type'].isin(valid_unit_types)]['unit_type'].unique()
        if len(invalid_units) > 0:
            errors.append(f"Unexpected unit_type value(s): {', '.join(map(str, invalid_units))}")
    
    # Check measure values
    if 'measure' in df.columns:
        valid_measures = ['Incurred Loss', 'Paid Loss', 'Reported Count', 'Closed Count']
        invalid_measures = df[~df['measure'].isin(valid_measures)]['measure'].unique()
        if len(invalid_measures) > 0:
            errors.append(f"Unexpected measure value(s): {', '.join(map(str, invalid_measures))}")
    
    # Check for duplicate combinations
    if all(col in df.columns for col in ['source', 'period', 'age', 'measure']):
        duplicates = df.duplicated(subset=['source', 'period', 'age', 'measure'], keep=False)
        if duplicates.any():
            dup_count = duplicates.sum()
            errors.append(f"Found {dup_count} duplicate source/period/age/measure combinations")
    
    # Raise error if validation fails
    if len(errors) > 0:
        error_msg = "Data validation failed!\n\n"
        
        if errors:
            error_msg += "ERRORS:\n"
            for error in errors:
                error_msg += f"  - {error}\n"
        
        raise ValueError(error_msg)


if __name__ == "__main__":
    """
    Run the data preparation process.
    """
    print("Starting data preparation for Chain Ladder...")
    read_and_process_data()
    print(f"\nData preparation complete!")
    print(f"Parquet (to keep category types): {OUTPUT_PATH}1_{METHOD_ID}_prepped.parquet")
    print(f"CSV (for user inspection): {OUTPUT_PATH}1_{METHOD_ID}_prepped.csv")
