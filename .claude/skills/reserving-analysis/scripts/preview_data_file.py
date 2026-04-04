from typing import Union
import polars as pl
from pathlib import Path

# Supported Excel formats
SUPPORTED_EXCEL = {'.xlsx', '.xls', '.xlsm'}

def preview_data_file(file_path: str, sheet_name: Union[str, int] = 0, sample_size: int = 5) -> str:
    """
    Get a comprehensive preview/summary of a data file (CSV or Excel) without reading the full file.
    Shows structure, data types, first/last rows, and a random sample.
    
    Robust to files without headers and various unexpected formats.
    
    Args:
        file_path: path to file.
        sheet_name: For Excel files, sheet name (str) or index (int, default: 0)
        sample_size: Number of random rows to sample (default: 5)
    
    Returns:
        A comprehensive preview including sheets, columns/types, first/last rows, and random sample.
    """
    
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    
    try:
        # Read the data based on file type
        if ext == '.csv':
            try:
                df = pl.read_csv(file_path, infer_schema_length=1000)
                sheets_info = "File type: CSV (single sheet) - headers detected"
            except Exception:
                try:
                    # If that fails, try without headers
                    df = pl.read_csv(file_path, has_header=False, infer_schema_length=1000)
                    # Generate column names like column_0, column_1, etc.
                    new_names = [f"column_{i}" for i in range(df.width)]
                    df = df.rename(dict(zip(df.columns, new_names)))
                    sheets_info = "File type: CSV (single sheet) - no headers detected, using generated column names"
                except Exception:
                    # Last resort: read as strings
                    df = pl.read_csv(file_path, has_header=False, schema_overrides=pl.Utf8, infer_schema_length=0)
                    new_names = [f"column_{i}" for i in range(df.width)]
                    df = df.rename(dict(zip(df.columns, new_names)))
                    sheets_info = "File type: CSV (single sheet) - read as text only due to parsing issues"
        elif ext in SUPPORTED_EXCEL:
            import openpyxl
            excel_file = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            all_sheets = excel_file.sheetnames
            sheets_info = f"Available sheets ({len(all_sheets)}): {', '.join(all_sheets)}"
            
            # Handle sheet_name parameter - convert string '0' to int 0
            if isinstance(sheet_name, str) and sheet_name.isdigit():
                sheet_name = int(sheet_name)
            
            # Get the worksheet
            if isinstance(sheet_name, int):
                current_sheet = all_sheets[sheet_name] if sheet_name < len(all_sheets) else all_sheets[0]
                if sheet_name >= len(all_sheets):
                    sheets_info += f"\nWarning: Sheet index {sheet_name} not found, using first sheet"
                ws = excel_file[current_sheet]
            else:
                current_sheet = sheet_name if sheet_name in all_sheets else all_sheets[0]
                if sheet_name not in all_sheets:
                    sheets_info += f"\nWarning: Sheet '{sheet_name}' not found, using first sheet"
                ws = excel_file[current_sheet]
            
            sheets_info += f"\nReading sheet: {current_sheet}"
            
            # Read data from openpyxl worksheet into polars DataFrame
            data = list(ws.values)
            
            # Filter out completely empty rows
            data = [row for row in data if row and any(cell is not None for cell in row)]
            
            if not data:
                return f"Error: Sheet '{current_sheet}' appears to be empty"
            
            # Check if first row looks like headers (all strings, minimal numbers)
            first_row = data[0]
            looks_like_headers = (
                len(data) > 1 and 
                all(isinstance(cell, str) and cell.strip() for cell in first_row if cell is not None) and
                any(isinstance(cell, (int, float)) for row in data[1:2] for cell in row if cell is not None)
            )
            
            try:
                if looks_like_headers:
                    # Use first row as headers
                    cols = [str(cell) if cell is not None else f"column_{i}" for i, cell in enumerate(first_row)]
                    df_data = data[1:]
                    sheets_info += " - headers detected"
                else:
                    # No headers detected, generate column names
                    max_cols = max(len(row) for row in data) if data else 0
                    cols = [f"column_{i}" for i in range(max_cols)]
                    df_data = data
                    sheets_info += " - no headers detected, using generated column names"
                
                # Ensure all rows have the same number of columns
                max_cols = len(cols)
                normalized_data = []
                for row in df_data:
                    if len(row) < max_cols:
                        row = list(row) + [None] * (max_cols - len(row))
                    else:
                        row = list(row[:max_cols])
                    normalized_data.append(row)
                
                df = pl.DataFrame(normalized_data, schema=cols, orient='row')
            except Exception as e:
                # If that fails, try reading everything as strings
                max_cols = max(len(row) for row in data) if data else 0
                cols = [f"column_{i}" for i in range(max_cols)]
                
                normalized_data = []
                for row in data:
                    str_row = [str(cell) if cell is not None else "" for cell in row]
                    if len(str_row) < max_cols:
                        str_row.extend([""] * (max_cols - len(str_row)))
                    normalized_data.append(str_row)
                
                df = pl.DataFrame(normalized_data, schema=cols, orient='row')
                sheets_info += f" - read as text due to parsing issues: {str(e)}"
            
            excel_file.close()
        else:
            return f"Error: Unsupported file type: {ext}. Supported: CSV, {', '.join(SUPPORTED_EXCEL)}"
    
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"
    
    total_rows = df.height
    total_cols = df.width
    
    # Build preview output
    result = [f"DATA FILE PREVIEW: {file_path}"]
    result.append("=" * 60)
    result.append("")
    
    # 1. File/Sheet info
    result.append(f"FILE INFO: {sheets_info}")
    result.append(f"SHAPE: {total_rows:,} rows x {total_cols} columns")
    result.append("")
    
    # 2. Column info with data types and non-null counts
    result.append("COLUMNS & DATA TYPES:")
    result.append("-" * 60)
    for col in df.columns:
        dtype = df[col].dtype
        non_null = df[col].is_not_null().sum()
        null_pct = (df[col].is_null().sum() / total_rows * 100) if total_rows > 0 else 0
        result.append(f"  {col:30s} | {str(dtype):12s} | {non_null:,}/{total_rows:,} non-null ({100-null_pct:.1f}%)")
    result.append("")
    
    # 3. First 3 rows
    result.append("FIRST 3 ROWS:")
    result.append("-" * 60)
    result.append(str(df.head(3)))
    result.append("")
    
    # 4. Last 3 rows
    result.append("LAST 3 ROWS:")
    result.append("-" * 60)
    result.append(str(df.tail(3)))
    result.append("")
    
    # 5. Random sample
    if total_rows > sample_size:
        # Add row index, sample, then sort by index to maintain order
        sample_df = df.with_row_count('__row__').sample(n=min(sample_size, total_rows), seed=42).sort('__row__').drop('__row__')
        result.append(f"RANDOM SAMPLE ({sample_size} rows):")
        result.append("-" * 60)
        result.append(str(sample_df))
    else:  # pragma: no cover
        result.append(f"INFO: File has only {total_rows} rows (no additional random sample needed)")
    result.append("")
    
    # 6. Basic statistics for numeric columns
    numeric_cols = [col for col in df.columns if df[col].dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64, pl.Float32, pl.Float64]]
    if len(numeric_cols) > 0:  # pragma: no cover
        result.append("NUMERIC COLUMN SUMMARY:")
        result.append("-" * 60)
        try:
            stats_df = df.select(numeric_cols).describe()
            result.append(str(stats_df))
        except Exception as e:
            result.append(f"Could not generate numeric summary: {str(e)}")
    
    preview_text = "\n".join(result)
    
    # Print the preview to console
    print(preview_text)
    
    return preview_text

