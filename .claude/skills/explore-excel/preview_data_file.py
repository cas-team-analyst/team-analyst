from typing import Union
import pandas as pd

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
        df = pd.read_csv(file_path)
        sheets_info = "File type: CSV (single sheet)"
    elif ext in SUPPORTED_EXCEL:
        import openpyxl
        excel_file = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        all_sheets = excel_file.sheetnames
        sheets_info = f"Available sheets ({len(all_sheets)}): {', '.join(all_sheets)}"
        
        # Handle sheet_name parameter - convert string '0' to int 0
        if isinstance(sheet_name, str) and sheet_name.isdigit():
            sheet_name = int(sheet_name)
        
        # Close and reopen with pandas
        excel_file.close()
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Determine which sheet was read
        if isinstance(sheet_name, int):
            current_sheet = all_sheets[sheet_name] if sheet_name < len(all_sheets) else f"Sheet{sheet_name}"
        else:
            current_sheet = sheet_name
        sheets_info += f"\nReading sheet: {current_sheet}"
    else:
        return f"Error: Unsupported file type: {ext}"
    
    total_rows = len(df)
    total_cols = len(df.columns)
    
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
        non_null = df[col].notna().sum()
        null_pct = (df[col].isna().sum() / total_rows * 100) if total_rows > 0 else 0
        result.append(f"  {col:30s} | {str(dtype):12s} | {non_null:,}/{total_rows:,} non-null ({100-null_pct:.1f}%)")
    result.append("")
    
    # 3. First 3 rows
    result.append("⬆️  FIRST 3 ROWS:")
    result.append("-" * 60)
    result.append(df.head(3).to_string(index=True, max_cols=10))
    result.append("")
    
    # 4. Last 3 rows
    result.append("⬇️  LAST 3 ROWS:")
    result.append("-" * 60)
    result.append(df.tail(3).to_string(index=True, max_cols=10))
    result.append("")
    
    # 5. Random sample
    if total_rows > sample_size:
        sample_df = df.sample(n=min(sample_size, total_rows), random_state=42).sort_index()
        result.append(f"🎲 RANDOM SAMPLE ({sample_size} rows):")
        result.append("-" * 60)
        result.append(sample_df.to_string(index=True, max_cols=10))
    else:  # pragma: no cover
        result.append(f"ℹ️  File has only {total_rows} rows (no additional random sample needed)")
    result.append("")
    
    # 6. Basic statistics for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:  # pragma: no cover
        result.append("📈 NUMERIC COLUMN SUMMARY:")
        result.append("-" * 60)
        stats_df = df[numeric_cols].describe().loc[['count', 'mean', 'min', 'max']]
        result.append(stats_df.to_string(float_format=lambda x: f"{x:,.2f}"))
    
    return "\n".join(result)

