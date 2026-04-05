# Reads raw insurance claims data from Excel files and converts it into a standardized format
# that all the other chain-ladder scripts can work with. Handles different data types (paid
# losses, incurred losses, claim counts) and validates that everything is formatted correctly.

"""
goal: Get data in standard format to simplify downstream operations. 
contents: 
    read_and_process_triangles(): Example function for reading, processing, validating, and saving triangle data necessary for Chain Ladder. This function can be replaced with one that works with your raw data.
    read_and_process_prior_selections(): Example function for reading prior selections from user's source. Modify the dummy code to read from your actual source (Excel, database, etc.).
    validate_triangle_data(): Validate the triangle data format. You should not typically modify this, as other assets depend on this format.

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 1a-prep-data.py
"""

import pandas as pd
from typing import Optional

# Replace these when using this file in an actual project:
DATA_FILE_PATH = "../raw-data/"
OUTPUT_PATH = "../processed-data/"
EXPECTED_LOSS_RATES_FILE = "expected-loss-rates.csv"  # Optional: Set to None if not using expected loss rates

def read_and_process_triangles():
    """
    Read raw triangle data, process it into a standardized analytical format, and save to output.
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
    incurred = read_triangle_data(
        file_path=DATA_FILE_PATH + "canonical-triangles.xlsx",
        sheet_name="Incurred",
        header_row=1,
        period_column=1,
        first_data_column=2,
        data_type="Incurred Loss",
        unit_type="Dollars",
        details="Example incurred data"
    )

    paid = read_triangle_data(
        file_path=DATA_FILE_PATH + "canonical-triangles.xlsx",
        sheet_name="Paid",
        header_row=1,
        period_column=1,
        first_data_column=2,
        data_type="Paid Loss",
        unit_type="Dollars",
        details="Example paid data"
    )

    reported = read_triangle_data(
        file_path=DATA_FILE_PATH + "canonical-triangles.xlsx",
        sheet_name="Reported",
        header_row=1,
        period_column=1,
        first_data_column=2,
        data_type="Reported Count",
        unit_type="Count",
        details="Example reported data"
    )

    closed = read_triangle_data(
        file_path=DATA_FILE_PATH + "canonical-triangles.xlsx",
        sheet_name="Closed",
        header_row=1,
        period_column=1,
        first_data_column=2,
        data_type="Closed Count",
        unit_type="Count",
        details="Example closed data"
    )

    # Concatenate all dataframes
    all_data = pd.concat([incurred, paid, reported, closed], ignore_index=True)
    
    # Get unique age and period categories in the order they first appear (should be consistent across all triangles)
    age_categories = incurred['age'].cat.categories.tolist()
    period_categories = incurred['period'].cat.categories.tolist()
    
    # Ensure categorical dtypes are preserved after concat with correct ordering
    all_data['period'] = pd.Categorical(all_data['period'], categories=period_categories, ordered=True)
    all_data['age'] = pd.Categorical(all_data['age'], categories=age_categories, ordered=True)
    all_data['measure'] = all_data['measure'].astype('category')
    all_data['unit_type'] = all_data['unit_type'].astype('category')
    all_data['source'] = all_data['source'].astype('category')

    # Validate the format is correct. 
    #! AVOID CHANGING THIS, OUTPUT DATA FORMAT DOES NOT TYPICALLY CHANGE.
    validate_triangle_data(all_data)

    # Save to output - parquet preserves categorical ordering, CSV for inspection
    #! AVOID CHANGING THIS, OUTPUT DATA FORMAT DOES NOT TYPICALLY CHANGE.
    all_data.to_parquet(OUTPUT_PATH + f"1_prepped.parquet", index=False)
    all_data.to_csv(OUTPUT_PATH + f"1_prepped.csv", index=False)

def read_and_process_prior_selections(triangle_data: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Read prior selections from user's source, validate, and save to standardized format.
    
    This template function should be customized to read from your specific data source
    (Excel file, database, JSON, etc.).
    
    Args:
        triangle_data: DataFrame with processed triangle data for validation
    
    Returns:
        DataFrame with prior selections if they exist, None otherwise
        Columns: measure, interval, selection, reasoning
    """
    
    # ============================================================================
    # REPLACE THIS SECTION: Read prior selections from your specific source
    # ============================================================================
    # Example: Read from Excel file
    # prior_selections_file = DATA_FILE_PATH + "prior-selections.xlsx"
    # if not Path(prior_selections_file).exists():
    #     print("  No prior selections file found (optional)")
    #     return None
    # 
    # df_prior = pd.read_excel(prior_selections_file, sheet_name="Selections")
    # df_prior = df_prior[['measure', 'interval', 'selection', 'reasoning']]
    
    # Example: Read from CSV file
    prior_selections_file = OUTPUT_PATH + "../prior-selections.csv"
    from pathlib import Path
    if not Path(prior_selections_file).exists():
        print("  No prior selections file found (optional)")
        return None
    
    print(f"  Found prior selections file: {prior_selections_file}")
    df_prior = pd.read_csv(prior_selections_file)
    
    # Ensure required columns exist
    required_columns = ['measure', 'interval', 'selection']
    if not all(col in df_prior.columns for col in required_columns):
        raise ValueError(f"Prior selections must have columns: {', '.join(required_columns)}")
    
    # Add reasoning column if missing (optional field)
    if 'reasoning' not in df_prior.columns:
        df_prior['reasoning'] = ''
    
    # ============================================================================
    # END REPLACE SECTION
    # ============================================================================
    
    # Validation starts here
    errors = []
    
    # Check for empty DataFrame
    if df_prior.empty:
        print("  Prior selections file is empty")
        return None
    
    # Validate required fields exist
    for col in required_columns:
        if col not in df_prior.columns:
            errors.append(f"Missing required column: {col}")
    
    # Check data types and null values
    if 'measure' in df_prior.columns:
        null_count = df_prior['measure'].isna().sum()
        if null_count > 0:
            errors.append(f"'measure' column contains {null_count} null value(s)")
    
    if 'interval' in df_prior.columns:
        null_count = df_prior['interval'].isna().sum()
        if null_count > 0:
            errors.append(f"'interval' column contains {null_count} null value(s)")
    
    if 'selection' in df_prior.columns:
        null_count = df_prior['selection'].isna().sum()
        if null_count > 0:
            errors.append(f"'selection' column contains {null_count} null value(s)")
        if not pd.api.types.is_numeric_dtype(df_prior['selection']):
            errors.append("'selection' column must be numeric")
    
    # Validate against triangle data
    if not errors:
        # Check measures
        valid_measures = triangle_data['measure'].cat.categories.tolist()
        invalid_measures = df_prior[~df_prior['measure'].isin(valid_measures)]['measure'].unique()
        if len(invalid_measures) > 0:
            errors.append(f"Prior selections contain invalid measures: {', '.join(invalid_measures)}")
            errors.append(f"Valid measures are: {', '.join(valid_measures)}")
        
        # Derive valid intervals from triangle age categories
        age_categories = triangle_data['age'].cat.categories.tolist()
        valid_intervals = []
        for i in range(len(age_categories) - 1):
            interval = f"{age_categories[i]}-{age_categories[i+1]}"
            valid_intervals.append(interval)
        
        # Check intervals
        invalid_intervals = df_prior[~df_prior['interval'].isin(valid_intervals)]['interval'].unique()
        if len(invalid_intervals) > 0:
            errors.append(f"Prior selections contain invalid intervals: {', '.join(invalid_intervals)}")
            errors.append(f"Valid intervals are: {', '.join(valid_intervals)}")
        
        # Check for duplicates
        duplicates = df_prior.duplicated(subset=['measure', 'interval'], keep=False)
        if duplicates.any():
            dup_count = duplicates.sum()
            errors.append(f"Prior selections contain {dup_count} duplicate measure/interval combinations")
    
    # Raise error if validation fails
    if errors:
        error_msg = "Prior selections validation failed!\n\nERRORS:\n"
        for error in errors:
            error_msg += f"  - {error}\n"
        raise ValueError(error_msg)
    
    # Ensure consistent data types
    df_prior = df_prior[['measure', 'interval', 'selection', 'reasoning']].copy()
    df_prior['measure'] = df_prior['measure'].astype(str)
    df_prior['interval'] = df_prior['interval'].astype(str)
    df_prior['selection'] = df_prior['selection'].astype(float)
    df_prior['reasoning'] = df_prior['reasoning'].fillna('').astype(str)
    
    print(f"  Validated {len(df_prior)} prior selections")
    return df_prior

def read_and_process_expected_loss_rates(triangle_data: pd.DataFrame, file_path: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Read expected loss rate data from file, validate, and save to standardized format.
    
    Args:
        triangle_data: DataFrame with processed triangle data for validation
        file_path: Path to the expected loss rates file. If None, uses DATA_FILE_PATH + EXPECTED_LOSS_RATES_FILE.
    
    Returns:
        DataFrame with expected loss rates if they exist, None otherwise
        Columns: period, expected_loss_rate, expected_freq
    """
    
    # Default file path if none provided
    if file_path is None:
        # If constant is None, skip expected loss rates processing
        if EXPECTED_LOSS_RATES_FILE is None:
            print("  Expected loss rates not configured (EXPECTED_LOSS_RATES_FILE is None)")
            return None
        file_path = DATA_FILE_PATH + EXPECTED_LOSS_RATES_FILE
    
    from pathlib import Path
    if not Path(file_path).exists():
        print("  No expected loss rates file found (optional)")
        return None
    
    print(f"  Found expected loss rates file: {file_path}")
    
    # This is a simple implementation for reading expected loss rate data.
    # However, data may come in a different format so you may need to replace this code.
    
    # Read the data
    if file_path.lower().endswith('.csv'):
        df_expected = pd.read_csv(file_path)
    elif file_path.lower().endswith(('.xlsx', '.xls')):
        df_expected = pd.read_excel(file_path, engine='openpyxl')
    else:
        raise ValueError(f"Unsupported file format: {file_path}. Use .csv, .xlsx, or .xls")
    
    # ============================================================================
    # COLUMN RENAMING STEP
    # If your source file has different column names, rename them here:
    # Example:
    # df_expected = df_expected.rename(columns={
    #     'Period': 'period',
    #     'Expected_Loss_Rate': 'expected_loss_rate',
    #     'Expected_Frequency': 'expected_freq'
    # })
    # ============================================================================
    
    # Validate the data
    validate_expected_loss_rates(df_expected, triangle_data)
    
    # Save to output
    df_expected.to_parquet(OUTPUT_PATH + "1_expected_loss_rates.parquet", index=False)
    df_expected.to_csv(OUTPUT_PATH + "1_expected_loss_rates.csv", index=False)
    
    print(f"  Processed {len(df_expected)} expected loss rate records")
    return df_expected

def validate_expected_loss_rates(df: pd.DataFrame, triangle_data: pd.DataFrame) -> None:
    """
    Validate expected loss rates data to ensure it meets expected format and quality standards.
    Raises ValueError if validation fails with detailed error information.
    
    Args:
        df: DataFrame to validate (expected loss rates)
        triangle_data: DataFrame with triangle data for period validation
    
    Raises:
        ValueError: If validation fails, with detailed error information
    """
    
    errors = []
    
    # Check if DataFrame is empty
    if df.empty:
        raise ValueError("Expected loss rates validation failed!\n\nERRORS:\n  - DataFrame is empty")
    
    # Check required columns
    required_columns = ['period', 'expected_loss_rate', 'expected_freq']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    # If we have the required columns, perform detailed validation
    if not missing_columns:
        # Check data types
        if not pd.api.types.is_numeric_dtype(df['expected_loss_rate']):
            errors.append("'expected_loss_rate' column must be numeric (decimal)")
        
        if not pd.api.types.is_numeric_dtype(df['expected_freq']):
            errors.append("'expected_freq' column must be numeric (decimal)")
        
        # Check for null values
        for col in required_columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                errors.append(f"Column '{col}' contains {null_count} null value(s)")
        
        # Check for duplicate periods (only one value per period)
        if 'period' in df.columns:
            duplicates = df['period'].duplicated(keep=False)
            if duplicates.any():
                dup_count = duplicates.sum()
                dup_periods = df[duplicates]['period'].unique()
                errors.append(f"Found {dup_count} duplicate period(s): {', '.join(map(str, dup_periods))}")
        
        # Validate periods match triangle data
        if 'period' in df.columns and not df.empty:
            triangle_periods = set(triangle_data['period'].cat.categories.tolist())
            expected_periods = set(df['period'].astype(str).unique())
            
            # Check for periods in expected data that don't exist in triangles
            extra_periods = expected_periods - triangle_periods
            if extra_periods:
                errors.append(f"Expected loss rates contain periods not in triangle data: {', '.join(sorted(extra_periods))}")
            
            # Check for missing periods (warning only - not all triangle periods need expected rates)
            missing_periods = triangle_periods - expected_periods
            if missing_periods:
                print(f"  Note: {len(missing_periods)} triangle period(s) have no expected loss rates: {', '.join(sorted(list(missing_periods)[:5]))}{'...' if len(missing_periods) > 5 else ''}")
    
    # Raise error if validation fails
    if errors:
        error_msg = "Expected loss rates validation failed!\n\nERRORS:\n"
        for error in errors:
            error_msg += f"  - {error}\n"
        raise ValueError(error_msg)
    
    # Convert to proper types and create ordered categorical for period
    # Use the same period ordering as triangle data to ensure consistency
    triangle_period_categories = triangle_data['period'].cat.categories.tolist()
    
    # Only include periods that exist in both datasets
    valid_periods = [p for p in triangle_period_categories if p in df['period'].astype(str).values]
    
    df['period'] = pd.Categorical(
        df['period'].astype(str),
        categories=valid_periods,
        ordered=True
    )
    df['expected_loss_rate'] = df['expected_loss_rate'].astype(float)
    df['expected_freq'] = df['expected_freq'].astype(float)
    
    print(f"  Validated {len(df)} expected loss rate records")

def validate_triangle_data(df: pd.DataFrame) -> None:
    """
    Validate the prepped triangle data to ensure it meets expected format and quality standards.
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
    
    # Process triangle data
    read_and_process_triangles()
    print(f"\nTriangle data preparation complete!")
    print(f"  Parquet: {OUTPUT_PATH}1_prepped.parquet")
    print(f"  CSV: {OUTPUT_PATH}1_prepped.csv")
    
    # Read prepped triangle data for validation of prior selections
    df_triangles = pd.read_parquet(OUTPUT_PATH + f"1_prepped.parquet")
    
    # Process prior selections (optional)
    print("\nProcessing prior selections (if available)...")
    df_prior = read_and_process_prior_selections(df_triangles)
    
    if df_prior is not None:
        # Save to output
        output_file = OUTPUT_PATH + "../prior-selections.csv"
        df_prior.to_csv(output_file, index=False)
        print(f"  Saved standardized prior selections to: {output_file}")

    # Process expected loss rates (optional)
    print("\nProcessing expected loss rates (if available)...)")
    df_expected = read_and_process_expected_loss_rates(df_triangles)
    
    if df_expected is not None:
        print(f"  Saved expected loss rates to:")
        print(f"    Parquet: {OUTPUT_PATH}1_expected_loss_rates.parquet")
        print(f"    CSV: {OUTPUT_PATH}1_expected_loss_rates.csv")
        print("\nData preparation complete!")
