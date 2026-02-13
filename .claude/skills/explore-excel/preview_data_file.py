from typing import Union
import polars as pl

def preview_data_file(file_path: str, sheet_name: Union[str, int] = 0, sample_size: int = 5) -> str:
    """
    Get a comprehensive preview/summary of a data file (CSV or Excel) without reading the full file.
    Shows structure, data types, first/last rows, and a random sample.
    
    Args:
        file_path: path to file.
        sheet_name: For Excel files, sheet name (str) or index (int, default: 0)
        sample_size: Number of random rows to sample (default: 5)
    
    Returns:
        A comprehensive preview including sheets, columns/types, first/last rows, and random sample.
    """
    
    ext = file_path.suffix.lower()
    
    # Read the data based on file type
    if ext == '.csv':
        df = pl.read_csv(file_path)
        sheets_info = "File type: CSV (single sheet)"
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
            current_sheet = all_sheets[sheet_name] if sheet_name < len(all_sheets) else f"Sheet{sheet_name}"
            ws = excel_file[current_sheet]
        else:
            current_sheet = sheet_name
            ws = excel_file[sheet_name]
        
        sheets_info += f"\nReading sheet: {current_sheet}"
        
        # Read data from openpyxl worksheet into polars DataFrame
        data = list(ws.values)
        cols = data[0]  # First row is headers
        df = pl.DataFrame(data[1:], schema=cols, orient='row')
        
        excel_file.close()
    else:
        return f"Error: Unsupported file type: {ext}"
    
    total_rows = df.height
    total_cols = df.width
    
    # Build preview output
    result = [f"📊 DATA FILE PREVIEW: {file_path}"]
    result.append("=" * 60)
    result.append("")
    
    # 1. File/Sheet info
    result.append(f"📁 {sheets_info}")
    result.append(f"📐 Shape: {total_rows:,} rows × {total_cols} columns")
    result.append("")
    
    # 2. Column info with data types and non-null counts
    result.append("🔤 COLUMNS & DATA TYPES:")
    result.append("-" * 60)
    for col in df.columns:
        dtype = df[col].dtype
        non_null = df[col].is_not_null().sum()
        null_pct = (df[col].is_null().sum() / total_rows * 100) if total_rows > 0 else 0
        result.append(f"  {col:30s} | {str(dtype):12s} | {non_null:,}/{total_rows:,} non-null ({100-null_pct:.1f}%)")
    result.append("")
    
    # 3. First 3 rows
    result.append("⬆️  FIRST 3 ROWS:")
    result.append("-" * 60)
    result.append(str(df.head(3)))
    result.append("")
    
    # 4. Last 3 rows
    result.append("⬇️  LAST 3 ROWS:")
    result.append("-" * 60)
    result.append(str(df.tail(3)))
    result.append("")
    
    # 5. Random sample
    if total_rows > sample_size:
        # Add row index, sample, then sort by index to maintain order
        sample_df = df.with_row_count('__row__').sample(n=min(sample_size, total_rows), seed=42).sort('__row__').drop('__row__')
        result.append(f"🎲 RANDOM SAMPLE ({sample_size} rows):")
        result.append("-" * 60)
        result.append(str(sample_df))
    else:  # pragma: no cover
        result.append(f"ℹ️  File has only {total_rows} rows (no additional random sample needed)")
    result.append("")
    
    # 6. Basic statistics for numeric columns
    numeric_cols = [col for col in df.columns if df[col].dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64, pl.Float32, pl.Float64]]
    if len(numeric_cols) > 0:  # pragma: no cover
        result.append("📈 NUMERIC COLUMN SUMMARY:")
        result.append("-" * 60)
        stats_df = df.select(numeric_cols).describe()
        result.append(str(stats_df))
    
    return "\n".join(result)

