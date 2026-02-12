---
name: create-excel
description: Guide for creating Excel workbooks to facilitate actuarial user interactions and parameter selections. Use this when asked to create Excel outputs for actuarial analysis, export results for user review, create workbooks for parameter selection, or prepare actuarial data for manual review and adjustments. Includes formulas, formatting, auto-fit columns, rounding decimals to 4 digits, adding cell notes, and other features to help actuaries make informed decisions. IMPORTANT: Always check if an Excel template is available in the skill directory - if so, copy, review, and carefully modify it rather than creating from scratch.
---

# Create Excel Workbooks for Actuarial Analysis

Guide for creating Excel workbooks that help actuarial users interact with analysis results, make parameter selections, and understand model outputs.

**Core Principle:** Excel workbooks should be self-documenting, interactive, and provide sufficient context for actuaries to make informed decisions about parameters and selections.

---

## 🎯 CRITICAL: Check for Templates First

**Before creating any Excel workbook from scratch:**

1. **Check if a template exists** in the skill directory (e.g., `.claude/skills/<method-name>/template.xlsx`)
2. **If template exists:**
   - Copy the template to your output location
   - Review its structure, formatting, and formulas
   - Carefully modify the template by updating data references, adding/removing rows/columns as needed
   - Preserve existing formatting, formulas, and structure where appropriate
   - **DO NOT recreate from scratch** - templates contain carefully designed layouts and formulas
3. **If no template exists:**
   - Create the workbook from scratch using the patterns below
   - Consider if this workbook should become a template for future use

**Why use templates?**
- Templates contain pre-built formulas, formatting, and structure
- Ensures consistency across analyses
- Saves time and reduces errors
- Incorporates actuarial best practices

**Some skills that may have Excel templates:**
- Chain Ladder method
- Bornhuetter-Ferguson method
- Other actuarial reserving methods
- Standard parameter selection workbooks

**Using openpyxl to work with templates:**
```python
from openpyxl import load_workbook
import shutil
from pathlib import Path

def use_template(template_path: str, output_path: str) -> Workbook:
    """
    Copy and load template for modification.
    
    Parameters:
    -----------
    template_path : str
        Path to template file (e.g., '.claude/skills/chain-ladder/template.xlsx')
    output_path : str
        Destination path for the new workbook
    
    Returns:
    --------
    Workbook : Loaded workbook ready for modification
    """
    # Check if template exists
    if not Path(template_path).exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    # Copy template to output location
    shutil.copy2(template_path, output_path)
    print(f"Template copied from {template_path} to {output_path}")
    
    # Load and return the workbook for modification
    wb = load_workbook(output_path)
    print(f"Template loaded for modification. Sheets: {wb.sheetnames}")
    
    return wb

# Example usage:
template = ".claude/skills/chain-ladder/template.xlsx"
if Path(template).exists():
    wb = use_template(template, "output/chain_ladder_results.xlsx")
    # Now modify the workbook as needed
    ws = wb['Results']
    ws['A1'] = "Updated Analysis Date"
    # ... make other modifications ...
    wb.save("output/chain_ladder_results.xlsx")
else:
    # No template - create from scratch
    wb = create_workbook_from_scratch()
```

## Quick Reference

**⚠️ ALWAYS CHECK FOR TEMPLATES FIRST:** Before creating Excel workbooks from scratch, check if a template exists in the skill directory (`.claude/skills/<method-name>/template.xlsx`). If found, copy and modify the template rather than starting from scratch. → [Template guide](#-critical-check-for-templates-first)

**Key Features:**
- **Formulas first:** Use Excel formulas instead of hardcoded values whenever possible → [Details](#formulas-over-values)
- **Auto-fit columns:** Ensure all content is visible without manual adjustment (but don't make them too wide either) → [Details](#formatting-standards)
- **Consistent rounding:** Decimals to 4 digits, whole numbers to 0 digits → [Details](#formatting-standards)
- **Helpful notes:** Add cell comments/notes explaining calculations, assumptions, and decision points → [Details](#cell-notes-and-comments)
- **Clear formatting:** Headers, borders, number formats, conditional formatting for readability → [Details](#formatting-standards)
- **User inputs highlighted:** Use colors/formatting to distinguish input cells from calculated cells → [See color scheme below]
- **Multiple sheets:** Organize by purpose (inputs, calculations, outputs, selections, reference) → [Details](#sheet-organization)

**Python Package:** → [Installation guide](#installation-and-setup)
- **`openpyxl`:** Full-featured Excel read/write, formulas, formatting, comments (use this exclusively for all Excel operations)

**Rounding Standards:** → [Details](#formatting-standards)
```python
# Decimals: 4 digits
0.654321 → 0.6543

# Whole numbers: 0 digits (no decimals)
12345.67 → 12,346

# Loss ratios, factors: 4 decimals
1.2345678 → 1.2345

# Dollar amounts: 0 decimals with thousands separator
1234567.89 → 1,234,568
```

**Common Workbook Types:**
1. **Parameter Selection Workbook** → [See guide](#parameter-selection-workbooks)
2. **Results Export Workbook** → [See guide](#results-export-workbooks)
3. **Comparison Workbook** → [See guide](#comparison-workbooks)
4. **Interactive Analysis Workbook** → [See guide](#interactive-analysis-workbooks)

**Important Workflow Guidelines:** → [File safety details](#file-safety-and-user-work-protection)
- **Open workbooks automatically:** Use PowerShell `Start-Process` or `Invoke-Item` to open Excel files when ready for review, don't ask users to open them manually
- **Never overwrite existing workbooks:** Check if file exists first. If it does, archive the existing version before modifying, or prompt for new filename → [Details](#file-safety-and-user-work-protection)
- **Archive before editing:** When modifying existing workbooks, save a dated backup copy first (e.g., `filename_backup_2026-02-12.xlsx`)
- **Modify, don't recreate:** If a workbook already exists with user selections, modify it rather than recreating from scratch

**Additional Resources:**
- **Basic Creation Patterns** → [openpyxl patterns](#basic-excel-creation-patterns), [pandas patterns](#pattern-2-using-pandas-with-openpyxl-engine)
- **Advanced Features** → [Tables](#using-excel-tables-listobjects), [Dropdowns](#adding-dropdown-lists), [Charts](#adding-charts), [Conditional Formatting](#conditional-formatting)
- **Best Practices** → [Complete guide](#best-practices-summary)
- **Troubleshooting** → [Common issues](#troubleshooting)

---

## Installation and Setup

**Install required package:**
```powershell
pip install openpyxl
```

**Note:** Use `openpyxl` exclusively for all Excel operations. It provides comprehensive support for reading, writing, formulas, formatting, comments, and all features needed for actuarial workbooks.

**Opening Excel files automatically:**
```powershell
# After creating/modifying Excel file, open it automatically
Invoke-Item path/to/file.xlsx

# Or use Start-Process for more control
Start-Process excel.exe path/to/file.xlsx
```

Always open workbooks automatically when ready for user review - don't ask the user to open them manually.

**Import pattern:**
```python
import pandas as pd
import numpy as np
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Fill, PatternFill, Border, Side, Alignment, numbers
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.comments import Comment
from openpyxl.formatting.rule import CellIsRule
from datetime import datetime
from pathlib import Path
import os
import shutil
```

---

## File Safety and User Work Protection

### Critical: Never Overwrite Existing User Work

**Always check if file exists before creating/modifying:**

```python
import os
import shutil
from datetime import datetime

def safe_excel_save(wb, output_path: str, auto_open: bool = True):
    """
    Safely save Excel workbook, protecting existing user work.
    
    - If file doesn't exist: Create it
    - If file exists: Archive existing version with timestamp, then save
    - After saving: Automatically open for user review
    
    Parameters:
    -----------
    wb : Workbook
        openpyxl Workbook object to save
    output_path : str
        Desired path for Excel file
    auto_open : bool
        Whether to automatically open the file after saving (default: True)
    """
    if os.path.exists(output_path):
        # File exists - archive it before overwriting
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(output_path)[0]
        archive_path = f"{base_name}_backup_{timestamp}.xlsx"
        
        shutil.copy2(output_path, archive_path)
        print(f"Existing file archived to: {archive_path}")
    
    # Save the workbook
    wb.save(output_path)
    print(f"Workbook saved: {output_path}")
    
    # Automatically open for user review
    if auto_open:
        open_excel_file(output_path)

def open_excel_file(file_path: str):
    """
    Open Excel file automatically for user review.
    Works on Windows, Mac, and Linux.
    """
    import subprocess
    import sys
    
    abs_path = os.path.abspath(file_path)
    
    try:
        if sys.platform == 'win32':
            # Windows: use os.startfile or powershell
            os.startfile(abs_path)
        elif sys.platform == 'darwin':
            # Mac: use 'open' command
            subprocess.run(['open', abs_path])
        else:
            # Linux: use 'xdg-open'
            subprocess.run(['xdg-open', abs_path])
        
        print(f"Opening {file_path} for review...")
    except Exception as e:
        print(f"Saved to {file_path} - please open manually if needed")
        print(f"(Auto-open error: {e})")

def modify_existing_workbook(file_path: str, modification_func):
    """
    Safely modify an existing workbook.
    Archives the original, applies modifications, saves, and opens.
    
    Parameters:
    -----------
    file_path : str
        Path to existing Excel file
    modification_func : callable
        Function that takes a Workbook object and modifies it
        Should be: def modify(wb: Workbook) -> None
    
    Example:
    --------
    def add_sheet(wb):
        ws = wb.create_sheet("New Analysis")
        ws['A1'] = "New data"
    
    modify_existing_workbook("selections.xlsx", add_sheet)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Cannot modify - file does not exist: {file_path}")
    
    # Archive original
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = os.path.splitext(file_path)[0]
    archive_path = f"{base_name}_backup_{timestamp}.xlsx"
    shutil.copy2(file_path, archive_path)
    print(f"Original file archived to: {archive_path}")
    
    # Load, modify, and save
    wb = load_workbook(file_path)
    modification_func(wb)
    wb.save(file_path)
    print(f"Workbook updated: {file_path}")
    
    # Open for review
    open_excel_file(file_path)

def check_and_prompt_if_exists(file_path: str) -> bool:
    """
    Check if file exists and warn about potential user work.
    
    Returns:
    --------
    bool : True if safe to proceed (file doesn't exist or user confirmed)
    
    Note: In automated scripts, prefer safe_excel_save() which
    automatically archives. This function is for interactive scenarios.
    """
    if os.path.exists(file_path):
        print(f"⚠️  WARNING: File already exists: {file_path}")
        print(f"    This file may contain user selections or modifications.")
        print(f"    Consider using modify_existing_workbook() or safe_excel_save()")
        print(f"    which will automatically archive the existing version.")
        return False
    return True
```

**Usage examples:**

```python
# Creating a new workbook (safe - auto-archives if exists)
wb = Workbook()
# ... add sheets, data, formatting ...
safe_excel_save(wb, "output/selections.xlsx")  # Auto-opens after saving

# Modifying an existing workbook
def add_new_method_results(wb):
    ws = wb.create_sheet("Cape Cod Method")
    ws['A1'] = "Cape Cod Results"
    # ... add data ...

if os.path.exists("output/results.xlsx"):
    modify_existing_workbook("output/results.xlsx", add_new_method_results)
else:
    # File doesn't exist - create from scratch
    wb = create_new_results_workbook()
    safe_excel_save(wb, "output/results.xlsx")
```

**Key principles:**
1. **Never recreate a file that already exists** - User may have made selections
2. **Always archive before modifying** - Preserve user work with timestamped backup
3. **Auto-open after saving** - Don't ask user to manually open files
4. **Use timestamps in archives** - Makes it easy to track when backups were made
5. **Check existence before operations** - Use `os.path.exists()` to decide create vs. modify

---

## Basic Excel Creation Patterns

### Pattern 1: Using openpyxl (Recommended for Interactive Workbooks)

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.comments import Comment

def create_actuarial_workbook(output_path: str, data: dict):
    """
    Create a formatted Excel workbook with actuarial best practices.
    
    Parameters:
    -----------
    output_path : str
        Path to save the Excel file
    data : dict
        Dictionary containing DataFrames and metadata
    """
    wb = Workbook()
    
    # Remove default sheet
    if 'Sheet' in wb.sheetnames:
        wb.remove(wb['Sheet'])
    
    # Create sheets
    ws_summary = wb.create_sheet("Summary", 0)
    ws_data = wb.create_sheet("Data", 1)
    ws_selections = wb.create_sheet("Selections", 2)
    
    # Format summary sheet
    format_header_row(ws_summary, 1, ['Metric', 'Value', 'Notes'])
    add_summary_data(ws_summary, data)
    
    # Auto-fit columns
    auto_fit_columns(ws_summary)
    
    # Freeze panes (freeze first row)
    ws_summary.freeze_panes = 'A2'
    
    # Save safely and open for review
    safe_excel_save(wb, output_path)

def format_header_row(ws, row_num: int, headers: list):
    """Apply standard header formatting."""
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=row_num, column=col_idx, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

def auto_fit_columns(ws, min_width=10, max_width=50):
    """Auto-fit column widths based on content."""
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        
        for cell in column:
            try:
                if cell.value:
                    cell_length = len(str(cell.value))
                    max_length = max(max_length, cell_length)
            except:
                pass
        
        adjusted_width = min(max(max_length + 2, min_width), max_width)
        ws.column_dimensions[column_letter].width = adjusted_width

def add_cell_note(cell, note_text: str, author: str = "Claude"):
    """Add a comment/note to a cell."""
    comment = Comment(note_text, author)
    comment.width = 300
    comment.height = 100
    cell.comment = comment

def round_and_format_number(ws, cell, value, decimals: int = 4):
    """Round number and apply Excel number format."""
    if pd.isna(value):
        cell.value = None
        return
    
    # Round the value
    rounded_value = round(float(value), decimals)
    cell.value = rounded_value
    
    # Apply number format
    if decimals == 0:
        cell.number_format = '#,##0'  # Whole number with thousands separator
    elif decimals == 4:
        cell.number_format = '0.0000'  # 4 decimal places
    else:
        cell.number_format = f'0.{"0" * decimals}'
```

### Pattern 2: Using pandas with openpyxl engine

```python
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

def export_dataframe_with_formatting(df: pd.DataFrame, output_path: str, 
                                     sheet_name: str = "Data",
                                     decimal_cols: list = None,
                                     integer_cols: list = None):
    """
    Export DataFrame to Excel with actuarial formatting.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data to export
    output_path : str
        Path to save Excel file
    sheet_name : str
        Name of worksheet
    decimal_cols : list
        Columns to format with 4 decimals
    integer_cols : list
        Columns to format as integers with comma separators
    """
    # Round columns appropriately
    df_formatted = df.copy()
    
    if decimal_cols:
        for col in decimal_cols:
            if col in df_formatted.columns:
                df_formatted[col] = df_formatted[col].round(4)
    
    if integer_cols:
        for col in integer_cols:
            if col in df_formatted.columns:
                df_formatted[col] = df_formatted[col].round(0)
    
    # Write to Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_formatted.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Access workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Format headers
        for cell in worksheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        
        # Apply number formats
        if decimal_cols:
            for col in decimal_cols:
                if col in df.columns:
                    col_idx = df.columns.get_loc(col) + 1
                    col_letter = worksheet.cell(row=1, column=col_idx).column_letter
                    for row in range(2, len(df) + 2):
                        worksheet[f'{col_letter}{row}'].number_format = '0.0000'
        
        if integer_cols:
            for col in integer_cols:
                if col in df.columns:
                    col_idx = df.columns.get_loc(col) + 1
                    col_letter = worksheet.cell(row=1, column=col_idx).column_letter
                    for row in range(2, len(df) + 2):
                        worksheet[f'{col_letter}{row}'].number_format = '#,##0'
        
        # Auto-fit columns
        auto_fit_columns(worksheet)
        
        # Freeze header row
        worksheet.freeze_panes = 'A2'
    
    print(f"DataFrame exported to: {output_path}")
```

---

## Workbook Types and Templates

### Parameter Selection Workbooks

**Purpose:** Help actuaries choose parameters (loss development factors, expected loss ratios, tail factors, etc.)

**Essential elements:**
1. **Options sheet:** Show all available parameter choices with supporting data
2. **Selection sheet:** Input area where user enters their selections
3. **Calculation sheet:** Show how selections impact results
4. **Reference sheet:** Background data, averages, industry benchmarks
5. **Instructions sheet:** Clear guidance on what to select and why

**Example: Loss Development Factor Selection**

```python
def create_ldf_selection_workbook(triangle_data: pd.DataFrame, 
                                   age_to_age_factors: pd.DataFrame,
                                   output_path: str):
    """
    Create workbook for selecting loss development factors.
    
    Shows historical factors, averages, and allows user to input selections.
    """
    wb = Workbook()
    wb.remove(wb['Sheet'])
    
    # Sheet 1: Instructions
    ws_instructions = wb.create_sheet("Instructions", 0)
    add_instructions_content(ws_instructions, 
        title="Loss Development Factor Selection",
        instructions=[
            "1. Review historical age-to-age factors in the 'Historical Factors' sheet",
            "2. Review calculated averages in the 'Averages' sheet",
            "3. Enter your selected factors in the YELLOW cells in the 'Selections' sheet",
            "4. Review the impact on ultimate losses in the 'Results' sheet",
            "5. Document your rationale in the Comments column"
        ]
    )
    
    # Sheet 2: Historical age-to-age factors
    ws_historical = wb.create_sheet("Historical Factors", 1)
    add_triangle_data(ws_historical, age_to_age_factors, 
                     title="Age-to-Age Factors (Link Ratios)",
                     note="Historical loss development factors by accident year")
    
    # Sheet 3: Averages (simple, weighted, volume-weighted, latest N years)
    ws_averages = wb.create_sheet("Averages", 2)
    add_averages_table(ws_averages, age_to_age_factors)
    
    # Sheet 4: Selections (user input)
    ws_selections = wb.create_sheet("Selections", 3)
    create_selection_inputs(ws_selections, age_to_age_factors.columns)
    
    # Sheet 5: Results showing impact
    ws_results = wb.create_sheet("Results", 4)
    create_results_with_formulas(ws_results, triangle_data, ws_selections)
    
    # Save safely and open for review
    safe_excel_save(wb, output_path)

def add_triangle_data(ws, df: pd.DataFrame, title: str, note: str):
    """Add triangle data with formatting."""
    # Title
    ws['A1'] = title
    ws['A1'].font = Font(size=14, bold=True)
    add_cell_note(ws['A1'], note)
    
    # Write data starting at row 3
    start_row = 3
    
    # Headers
    headers = ['Accident Year'] + list(df.columns)
    format_header_row(ws, start_row, headers)
    
    # Data rows
    for idx, (acc_year, row_data) in enumerate(df.iterrows(), start=start_row + 1):
        ws.cell(row=idx, column=1, value=acc_year)
        
        for col_idx, value in enumerate(row_data, start=2):
            cell = ws.cell(row=idx, column=col_idx)
            round_and_format_number(cell, value, decimals=4)
    
    # Auto-fit
    auto_fit_columns(ws)
    ws.freeze_panes = 'B4'  # Freeze headers and accident year column

def add_averages_table(ws, age_to_age_factors: pd.DataFrame):
    """Create table of various averages for each development period."""
    ws['A1'] = "Average Age-to-Age Factors"
    ws['A1'].font = Font(size=14, bold=True)
    add_cell_note(ws['A1'], 
        "Different averaging methods to consider when selecting factors. "
        "Simple average weights all years equally. Volume-weighted gives more "
        "weight to years with larger loss volumes.")
    
    # Calculate averages
    averages_dict = {
        'Development Period': list(age_to_age_factors.columns),
        'Simple Average (All Years)': age_to_age_factors.mean().values,
        'Simple Average (Last 5)': age_to_age_factors.tail(5).mean().values,
        'Simple Average (Last 3)': age_to_age_factors.tail(3).mean().values,
        'Median': age_to_age_factors.median().values,
        'Latest Year': age_to_age_factors.iloc[-1].values,
    }
    
    averages_df = pd.DataFrame(averages_dict)
    
    # Write to worksheet
    start_row = 3
    headers = list(averages_df.columns)
    format_header_row(ws, start_row, headers)
    
    for idx, row in averages_df.iterrows():
        row_num = start_row + idx + 1
        for col_idx, value in enumerate(row, start=1):
            cell = ws.cell(row=row_num, column=col_idx)
            if col_idx == 1:  # Development period column
                cell.value = value
            else:
                round_and_format_number(cell, value, decimals=4)
    
    # Highlight recommended values (example: 5-year average)
    for row in range(start_row + 1, start_row + len(averages_df) + 1):
        cell = ws.cell(row=row, column=3)  # 5-year average column
        cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    
    auto_fit_columns(ws)
    ws.freeze_panes = 'B4'

def create_selection_inputs(ws, development_periods: list):
    """Create user input area for factor selections."""
    ws['A1'] = "Your Selected Loss Development Factors"
    ws['A1'].font = Font(size=14, bold=True)
    add_cell_note(ws['A1'], 
        "Enter your selected loss development factor for each period in the YELLOW cells. "
        "Refer to the Historical Factors and Averages sheets to inform your selections.")
    
    # Headers
    start_row = 3
    headers = ['Development Period', 'Selected Factor', 'Rationale/Comments']
    format_header_row(ws, start_row, headers)
    
    # Input rows
    yellow_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                         top=Side(style='thin'), bottom=Side(style='thin'))
    
    for idx, period in enumerate(development_periods, start=start_row + 1):
        # Development period (read-only)
        ws.cell(row=idx, column=1, value=period)
        
        # Selected factor (user input)
        cell_factor = ws.cell(row=idx, column=2)
        cell_factor.fill = yellow_fill
        cell_factor.border = thin_border
        cell_factor.number_format = '0.0000'
        add_cell_note(cell_factor, f"Enter your selected factor for {period} development")
        
        # Comments (user input)
        cell_comment = ws.cell(row=idx, column=3)
        cell_comment.fill = yellow_fill
        cell_comment.border = thin_border
        add_cell_note(cell_comment, "Document why you selected this factor")
    
    # Add tail factor row
    tail_row = start_row + len(development_periods) + 2
    ws.cell(row=tail_row, column=1, value="Tail Factor")
    cell_tail = ws.cell(row=tail_row, column=2)
    cell_tail.fill = yellow_fill
    cell_tail.border = thin_border
    cell_tail.number_format = '0.0000'
    add_cell_note(cell_tail, 
        "Enter tail factor to develop from last observed age to ultimate. "
        "Common range: 1.000 to 1.050 depending on line of business and maturity.")
    
    ws.cell(row=tail_row, column=3).fill = yellow_fill
    
    auto_fit_columns(ws)
    ws.freeze_panes = 'A4'

def create_results_with_formulas(ws, triangle_data: pd.DataFrame, ws_selections):
    """Create results sheet that references selections using formulas."""
    ws['A1'] = "Ultimate Loss Projections"
    ws['A1'].font = Font(size=14, bold=True)
    add_cell_note(ws['A1'], 
        "Ultimate losses calculated using your selected factors from the Selections sheet. "
        "Values update automatically when you change your selections.")
    
    # This would contain formulas referencing the Selections sheet
    # Example structure (actual implementation would use formulas):
    start_row = 3
    headers = ['Accident Year', 'Latest Loss', 'Age', 'CDF to Ultimate', 
               'Ultimate Loss', 'IBNR']
    format_header_row(ws, start_row, headers)
    
    # Add formula examples in comments
    ws.cell(row=start_row + 1, column=4).value = "=Formula referencing Selections"
    add_cell_note(ws.cell(row=start_row + 1, column=4),
        "This cell would contain a formula multiplying the selected age-to-age "
        "factors from the Selections sheet to calculate cumulative development factor")
    
    auto_fit_columns(ws)
    ws.freeze_panes = 'B4'

def add_instructions_content(ws, title: str, instructions: list):
    """Add formatted instructions to a sheet."""
    ws['A1'] = title
    ws['A1'].font = Font(size=16, bold=True, color="4472C4")
    
    ws['A3'] = "Instructions:"
    ws['A3'].font = Font(size=12, bold=True)
    
    for idx, instruction in enumerate(instructions, start=4):
        cell = ws.cell(row=idx, column=1, value=instruction)
        cell.alignment = Alignment(wrap_text=True, vertical='top')
    
    # Set column width for readability
    ws.column_dimensions['A'].width = 100
```

### Results Export Workbooks

**Purpose:** Export analysis results for review, documentation, and regulatory filing

**Essential elements:**
1. **Executive summary:** Key results, totals, high-level insights
2. **Detailed results:** Full breakdown by accident year, method, etc.
3. **Comparison tables:** Multiple methods side-by-side
4. **Diagnostics:** Residuals, fit statistics, validation metrics
5. **Metadata:** Run date, assumptions, data vintage, version info

**Example: Multi-Method Reserve Export**

```python
def create_reserve_results_workbook(results_dict: dict, output_path: str):
    """
    Export reserve analysis results from multiple methods.
    
    Parameters:
    -----------
    results_dict : dict
        Keys: method names ('ChainLadder', 'BornhuetterFerguson', etc.)
        Values: DataFrames with columns like accident_year, ultimate, ibnr, etc.
    output_path : str
        Path to save Excel file
    """
    wb = Workbook()
    wb.remove(wb['Sheet'])
    
    # Sheet 1: Executive Summary
    ws_summary = wb.create_sheet("Executive Summary", 0)
    create_executive_summary(ws_summary, results_dict)
    
    # Sheet 2: Comparison table
    ws_comparison = wb.create_sheet("Method Comparison", 1)
    create_method_comparison(ws_comparison, results_dict)
    
    # Sheets 3+: Detailed results for each method
    for idx, (method_name, df) in enumerate(results_dict.items(), start=2):
        ws = wb.create_sheet(method_name, idx)
        export_method_details(ws, method_name, df)
    
    # Last sheet: Metadata
    ws_metadata = wb.create_sheet("Metadata", len(results_dict) + 2)
    add_metadata(ws_metadata)
    
    # Save safely and open for review
    safe_excel_save(wb, output_path)
    print(f"Reserve results workbook created and opened: {output_path}")

def create_executive_summary(ws, results_dict: dict):
    """Create executive summary with key metrics."""
    ws['A1'] = "Reserve Analysis - Executive Summary"
    ws['A1'].font = Font(size=16, bold=True)
    
    ws['A2'] = f"As of: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ws['A2'].font = Font(italic=True)
    
    # Summary table
    start_row = 4
    headers = ['Method', 'Total Ultimate', 'Total IBNR', 'IBNR / Ultimate']
    format_header_row(ws, start_row, headers)
    
    for idx, (method_name, df) in enumerate(results_dict.items(), start=start_row + 1):
        ws.cell(row=idx, column=1, value=method_name)
        
        total_ultimate = df['ultimate'].sum()
        total_ibnr = df['ibnr'].sum()
        ibnr_pct = total_ibnr / total_ultimate if total_ultimate > 0 else 0
        
        cell_ult = ws.cell(row=idx, column=2)
        round_and_format_number(cell_ult, total_ultimate, decimals=0)
        
        cell_ibnr = ws.cell(row=idx, column=3)
        round_and_format_number(cell_ibnr, total_ibnr, decimals=0)
        
        cell_pct = ws.cell(row=idx, column=4)
        round_and_format_number(cell_pct, ibnr_pct, decimals=4)
    
    # Add average row
    avg_row = start_row + len(results_dict) + 2
    ws.cell(row=avg_row, column=1, value="Average")
    ws.cell(row=avg_row, column=1).font = Font(bold=True)
    
    # Formulas for averages
    for col in range(2, 5):
        cell = ws.cell(row=avg_row, column=col)
        start_data_row = start_row + 1
        end_data_row = start_row + len(results_dict)
        col_letter = cell.column_letter
        cell.value = f"=AVERAGE({col_letter}{start_data_row}:{col_letter}{end_data_row})"
        cell.font = Font(bold=True)
        if col < 4:
            cell.number_format = '#,##0'
        else:
            cell.number_format = '0.0000'
    
    auto_fit_columns(ws)

def create_method_comparison(ws, results_dict: dict):
    """Create side-by-side comparison of methods."""
    ws['A1'] = "Method Comparison by Accident Year"
    ws['A1'].font = Font(size=14, bold=True)
    
    # Get all accident years (assuming same across methods)
    first_method = list(results_dict.values())[0]
    accident_years = first_method['accident_year'].tolist()
    
    start_row = 3
    
    # Build headers dynamically
    headers = ['Accident Year']
    for method in results_dict.keys():
        headers.extend([f'{method} - Ultimate', f'{method} - IBNR'])
    
    format_header_row(ws, start_row, headers)
    
    # Data rows
    for idx, acc_year in enumerate(accident_years, start=start_row + 1):
        ws.cell(row=idx, column=1, value=acc_year)
        
        col = 2
        for method_name, df in results_dict.items():
            row_data = df[df['accident_year'] == acc_year].iloc[0]
            
            # Ultimate
            cell_ult = ws.cell(row=idx, column=col)
            round_and_format_number(cell_ult, row_data['ultimate'], decimals=0)
            
            # IBNR
            cell_ibnr = ws.cell(row=idx, column=col + 1)
            round_and_format_number(cell_ibnr, row_data['ibnr'], decimals=0)
            
            col += 2
    
    # Add totals row
    total_row = start_row + len(accident_years) + 1
    ws.cell(row=total_row, column=1, value="Total")
    ws.cell(row=total_row, column=1).font = Font(bold=True)
    
    for col in range(2, len(headers) + 1):
        cell = ws.cell(row=total_row, column=col)
        col_letter = cell.column_letter
        start_data = start_row + 1
        end_data = total_row - 1
        cell.value = f"=SUM({col_letter}{start_data}:{col_letter}{end_data})"
        cell.font = Font(bold=True)
        cell.number_format = '#,##0'
    
    # Conditional formatting: highlight largest/smallest IBNRs
    # (Implementation would add conditional formatting rules)
    
    auto_fit_columns(ws)
    ws.freeze_panes = 'B4'

def export_method_details(ws, method_name: str, df: pd.DataFrame):
    """Export detailed results for one method."""
    ws['A1'] = f"{method_name} - Detailed Results"
    ws['A1'].font = Font(size=14, bold=True)
    
    start_row = 3
    headers = list(df.columns)
    format_header_row(ws, start_row, headers)
    
    # Determine which columns get which formatting
    decimal_cols = ['ldf', 'cdf', 'percent_reported', 'loss_ratio']
    integer_cols = ['latest_loss', 'ultimate', 'ibnr', 'earned_premium']
    
    for idx, row in df.iterrows():
        row_num = start_row + idx + 1
        
        for col_idx, (col_name, value) in enumerate(row.items(), start=1):
            cell = ws.cell(row=row_num, column=col_idx)
            
            if col_name in decimal_cols:
                round_and_format_number(cell, value, decimals=4)
            elif col_name in integer_cols:
                round_and_format_number(cell, value, decimals=0)
            else:
                cell.value = value
    
    # Add total row for numeric columns
    total_row = start_row + len(df) + 1
    ws.cell(row=total_row, column=1, value="Total")
    ws.cell(row=total_row, column=1).font = Font(bold=True)
    
    for col_idx, col_name in enumerate(df.columns, start=1):
        if col_name in integer_cols:
            cell = ws.cell(row=total_row, column=col_idx)
            col_letter = cell.column_letter
            cell.value = f"=SUM({col_letter}{start_row + 1}:{col_letter}{total_row - 1})"
            cell.font = Font(bold=True)
            cell.number_format = '#,##0'
    
    auto_fit_columns(ws)
    ws.freeze_panes = 'B4'

def add_metadata(ws):
    """Add analysis metadata and documentation."""
    ws['A1'] = "Analysis Metadata"
    ws['A1'].font = Font(size=14, bold=True)
    
    metadata = [
        ('Run Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Python Version', '3.11'),
        ('Key Packages', 'pandas 2.0, numpy 1.24, chainladder 0.8'),
        ('Data Vintage', '2024-Q4'),
        ('Valuation Date', '2024-12-31'),
        ('Triangle Type', 'Incurred Loss'),
        ('Development Period', '12 months'),
        ('Notes', 'All amounts in USD'),
    ]
    
    start_row = 3
    for idx, (label, value) in enumerate(metadata, start=start_row):
        ws.cell(row=idx, column=1, value=label).font = Font(bold=True)
        ws.cell(row=idx, column=2, value=value)
    
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 50
```

### Comparison Workbooks

**Purpose:** Compare multiple scenarios, methods, or time periods side-by-side

**Example: before/after comparison, method A vs method B**

```python
def create_comparison_workbook(scenario_a: dict, scenario_b: dict, 
                                scenario_a_name: str, scenario_b_name: str,
                                output_path: str):
    """
    Create workbook comparing two scenarios with variance analysis.
    
    Parameters:
    -----------
    scenario_a, scenario_b : dict
        Results dictionaries with accident year level data
    scenario_a_name, scenario_b_name : str
        Labels for the scenarios
    output_path : str
        Path to save workbook
    """
    wb = Workbook()
    wb.remove(wb['Sheet'])
    
    ws = wb.create_sheet("Comparison", 0)
    
    ws['A1'] = f"Comparison: {scenario_a_name} vs {scenario_b_name}"
    ws['A1'].font = Font(size=14, bold=True)
    
    start_row = 3
    headers = [
        'Accident Year',
        f'{scenario_a_name} - Ultimate',
        f'{scenario_b_name} - Ultimate',
        'Difference ($)',
        'Difference (%)',
        'Status'
    ]
    format_header_row(ws, start_row, headers)
    
    # Assuming both scenarios have same accident years
    accident_years = scenario_a['accident_years']
    
    for idx, acc_year in enumerate(accident_years, start=start_row + 1):
        ws.cell(row=idx, column=1, value=acc_year)
        
        ult_a = scenario_a['ultimate'][idx - start_row - 1]
        ult_b = scenario_b['ultimate'][idx - start_row - 1]
        
        # Scenario A ultimate
        cell_a = ws.cell(row=idx, column=2)
        round_and_format_number(cell_a, ult_a, decimals=0)
        
        # Scenario B ultimate  
        cell_b = ws.cell(row=idx, column=3)
        round_and_format_number(cell_b, ult_b, decimals=0)
        
        # Difference ($) - use formula
        cell_diff = ws.cell(row=idx, column=4)
        cell_diff.value = f"=C{idx}-B{idx}"
        cell_diff.number_format = '#,##0'
        
        # Difference (%) - use formula
        cell_pct = ws.cell(row=idx, column=5)
        cell_pct.value = f"=(C{idx}-B{idx})/B{idx}"
        cell_pct.number_format = '0.00%'
        
        # Status - use formula with IF
        cell_status = ws.cell(row=idx, column=6)
        cell_status.value = f'=IF(ABS(E{idx})<0.05,"Similar",IF(E{idx}>0,"Higher","Lower"))'
    
    # Conditional formatting for differences
    from openpyxl.formatting.rule import CellIsRule
    
    red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    
    # Highlight large positive differences in green
    ws.conditional_formatting.add(
        f'D{start_row + 1}:D{start_row + len(accident_years)}',
        CellIsRule(operator='greaterThan', formula=['100000'], fill=green_fill)
    )
    
    # Highlight large negative differences in red
    ws.conditional_formatting.add(
        f'D{start_row + 1}:D{start_row + len(accident_years)}',
        CellIsRule(operator='lessThan', formula=['-100000'], fill=red_fill)
    )
    
    auto_fit_columns(ws)
    ws.freeze_panes = 'B4'
    
    # Save safely and open for review
    safe_excel_save(wb, output_path)
```

### Interactive Analysis Workbooks

**Purpose:** Allow actuaries to test sensitivities and see immediate impact

**Features:**
- User input cells for key assumptions
- Formulas that reference input cells
- Charts that update dynamically
- Scenario tables with drop-downs

```python
from openpyxl.chart import LineChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation

def create_sensitivity_workbook(base_case: dict, output_path: str):
    """
    Create interactive workbook for sensitivity testing.
    
    User can adjust key parameters and see impact on results.
    """
    wb = Workbook()
    wb.remove(wb['Sheet'])
    
    # Sheet 1: Inputs
    ws_inputs = wb.create_sheet("Inputs", 0)
    create_input_controls(ws_inputs)
    
    # Sheet 2: Results (with formulas referencing inputs)
    ws_results = wb.create_sheet("Results", 1)
    create_results_with_formulas_linked(ws_results, ws_inputs)
    
    # Sheet 3: Charts
    ws_charts = wb.create_sheet("Charts", 2)
    create_dynamic_charts(ws_charts, ws_results)
    
    # Save safely and open for review
    safe_excel_save(wb, output_path)
    print(f"Interactive sensitivity workbook created and opened: {output_path}")

def create_input_controls(ws):
    """Create user input area with validation."""
    ws['A1'] = "Sensitivity Analysis - Input Parameters"
    ws['A1'].font = Font(size=14, bold=True)
    
    yellow_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    
    # Define input parameters
    inputs = [
        ('Expected Loss Ratio', 0.65, 0.50, 0.80, '0.0000'),
        ('Tail Factor', 1.025, 1.000, 1.100, '0.0000'),
        ('Development Age Adjustment', 1.00, 0.90, 1.10, '0.0000'),
    ]
    
    start_row = 3
    headers = ['Parameter', 'Value', 'Min', 'Max', 'Description']
    format_header_row(ws, start_row, headers)
    
    for idx, (param_name, default_val, min_val, max_val, num_fmt) in enumerate(inputs, start=start_row + 1):
        # Parameter name
        ws.cell(row=idx, column=1, value=param_name).font = Font(bold=True)
        
        # Value (user input)
        cell_value = ws.cell(row=idx, column=2, value=default_val)
        cell_value.fill = yellow_fill
        cell_value.number_format = num_fmt
        
        # Min/max (read-only, for reference)
        ws.cell(row=idx, column=3, value=min_val).number_format = num_fmt
        ws.cell(row=idx, column=4, value=max_val).number_format = num_fmt
        
        # Description
        descriptions = [
            'A priori expected ultimate loss ratio',
            'Factor to develop from last age to ultimate',
            'Multiplicative adjustment to all LDFs'
        ]
        ws.cell(row=idx, column=5, value=descriptions[idx - start_row - 1])
        
        # Add data validation
        dv = DataValidation(type="decimal", operator="between", 
                           formula1=min_val, formula2=max_val)
        dv.error = f'Value must be between {min_val} and {max_val}'
        dv.errorTitle = 'Invalid Input'
        ws.add_data_validation(dv)
        dv.add(cell_value)
    
    auto_fit_columns(ws)
    ws.freeze_panes = 'A4'

def create_results_with_formulas_linked(ws, ws_inputs):
    """Create results that link to input sheet via formulas."""
    ws['A1'] = "Results (Updates Automatically)"
    ws['A1'].font = Font(size=14, bold=True)
    add_cell_note(ws['A1'], 
        "These results update automatically when you change inputs in the Inputs sheet")
    
    # Example structure - actual implementation would have full formulas
    start_row = 3
    headers = ['Accident Year', 'Ultimate Loss', 'IBNR', 'Notes']
    format_header_row(ws, start_row, headers)
    
    # Example formula in cell
    cell = ws.cell(row=start_row + 1, column=2)
    cell.value = "=Inputs!B4 * 1000000"  # Example: ELR * exposure
    cell.number_format = '#,##0'
    add_cell_note(cell, "Formula references Expected Loss Ratio from Inputs sheet")
    
    auto_fit_columns(ws)

def create_dynamic_charts(ws, ws_results):
    """Add charts that update with data."""
    # This is a simplified example
    # Full implementation would create actual charts
    
    ws['A1'] = "Visual Analysis"
    ws['A1'].font = Font(size=14, bold=True)
    
    # Would add LineChart, BarChart, etc. here
    # referencing data from ws_results
    
    pass  # Placeholder
```

---

## Advanced Features

### Using Excel Tables (ListObjects)

Excel tables provide filtering, sorting, and structured references:

```python
from openpyxl.worksheet.table import Table, TableStyleInfo

def create_excel_table(ws, start_row: int, end_row: int, 
                        start_col: int, end_col: int, table_name: str):
    """Create an Excel table (ListObject) from a range."""
    # Define table range
    start_cell = ws.cell(row=start_row, column=start_col).coordinate
    end_cell = ws.cell(row=end_row, column=end_col).coordinate
    table_range = f"{start_cell}:{end_cell}"
    
    # Create table
    table = Table(displayName=table_name, ref=table_range)
    
    # Add style
    style = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False
    )
    table.tableStyleInfo = style
    
    ws.add_table(table)
```

### Adding Dropdown Lists

```python
from openpyxl.worksheet.datavalidation import DataValidation

def add_dropdown(ws, cell_range: str, options: list):
    """Add dropdown list to cells."""
    # Create validation object
    dv = DataValidation(type="list", formula1=f'"{",".join(options)}"')
    dv.error = 'Please select from the dropdown'
    dv.errorTitle = 'Invalid Selection'
    dv.prompt = 'Select an option'
    dv.promptTitle = 'Choose'
    
    ws.add_data_validation(dv)
    dv.add(cell_range)

# Example usage:
# add_dropdown(ws, 'B4:B10', ['Chain Ladder', 'Bornhuetter-Ferguson', 'Cape Cod'])
```

### Adding Charts

```python
from openpyxl.chart import LineChart, BarChart, Reference

def add_line_chart(ws, data_range: str, title: str, position: str = 'E2'):
    """Add a line chart to the worksheet."""
    chart = LineChart()
    chart.title = title
    chart.style = 13
    chart.y_axis.title = 'Loss ($)'
    chart.x_axis.title = 'Accident Year'
    
    # Define data range
    data = Reference(ws, range_string=data_range)
    chart.add_data(data, titles_from_data=True)
    
    # Place chart
    ws.add_chart(chart, position)

# Example usage:
# add_line_chart(ws, 'B3:E13', 'Ultimate Loss by Accident Year', 'G3')
```

### Conditional Formatting

```python
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule
from openpyxl.styles import PatternFill, Font

def add_color_scale(ws, cell_range: str):
    """Add color scale formatting (red-yellow-green)."""
    rule = ColorScaleRule(
        start_type='min', start_color='F8696B',  # Red
        mid_type='percentile', mid_value=50, mid_color='FFEB84',  # Yellow
        end_type='max', end_color='63BE7B'  # Green
    )
    ws.conditional_formatting.add(cell_range, rule)

def highlight_outliers(ws, cell_range: str, threshold: float):
    """Highlight cells that exceed threshold."""
    red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    red_font = Font(color="9C0006")
    
    rule = CellIsRule(
        operator='greaterThan',
        formula=[threshold],
        fill=red_fill,
        font=red_font
    )
    ws.conditional_formatting.add(cell_range, rule)

def highlight_formula_errors(ws, cell_range: str):
    """Highlight cells with formula errors."""
    red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    
    rule = FormulaRule(
        formula=['ISERROR(' + cell_range.split(':')[0] + ')'],
        fill=red_fill
    )
    ws.conditional_formatting.add(cell_range, rule)
```

---

## Best Practices Summary

### File Safety First

**Critical: Protect user work from being overwritten**

- **Always check if file exists** before creating - use `os.path.exists(file_path)`
- **Archive existing files** with timestamps before any modifications
- **Never recreate files** that may contain user selections or modifications
- **Use `safe_excel_save()`** to handle archiving automatically and open for review
- **Modify existing workbooks** using `modify_existing_workbook()` or load with `load_workbook()`
- **Timestamp archives** as `filename_backup_YYYYMMDD_HHMMSS.xlsx` for traceability

**Examples:**
```python
# WRONG - Will destroy user's selections if file exists
wb = Workbook()
create_all_sheets(wb)
wb.save("selections.xlsx")  # Overwrites existing file!

# RIGHT - Safely saves and archives if exists
wb = Workbook()
create_all_sheets(wb)
safe_excel_save(wb, "selections.xlsx")  # Archives old version, saves, opens

# RIGHT - Modify existing file safely
if os.path.exists("selections.xlsx"):
    modify_existing_workbook("selections.xlsx", add_new_sheet_func)
else:
    wb = Workbook()
    create_from_scratch(wb)
    safe_excel_save(wb, "selections.xlsx")
```

### Automatically Open Files

**Always open workbooks for review - never ask users to open manually**

- **Use `safe_excel_save()`** which automatically opens after saving
- **Use `open_excel_file()`** to open files cross-platform
- **Never print "Please open file.xlsx"** - open it automatically instead
- **Handle errors gracefully** if auto-open fails, inform user of location

**Examples:**
```python
# WRONG - Makes user do extra work
wb.save("results.xlsx")
print("Please open results.xlsx to review")

# RIGHT - Opens automatically
safe_excel_save(wb, "results.xlsx")  # Auto-opens for review

# Alternative: Open existing file
open_excel_file("results.xlsx")
```

**PowerShell alternative (if not using Python):**
```powershell
# After creating file
Invoke-Item results.xlsx
```

### Formulas Over Values
- Use Excel formulas instead of hardcoded values wherever practical
- This allows users to see calculation logic and modify inputs
- Example: `=B4*C4` instead of storing the product directly
- Name cells/ranges for easier formula readability
- Use absolute references ($A$1) for parameters, relative (A1) for row-specific calculations

### Formatting Standards

**Column widths:**
- Auto-fit all columns after populating data
- Set minimum width (e.g., 10) and maximum (e.g., 50) to avoid extremes
- Manually adjust columns with long text descriptions

**Number formats:**
```python
# Loss amounts, premiums, exposures
cell.number_format = '#,##0'  # No decimals, thousands separator

# Ratios, factors, percentages (4 decimals)
cell.number_format = '0.0000'

# Percentages (2 decimals)
cell.number_format = '0.00%'

# Dates
cell.number_format = 'yyyy-mm-dd'
```

**Borders and gridlines:**
- Use thin borders for table edges
- Use medium/thick borders to separate major sections
- Header rows should have bottom borders

**Font:**
- Headers: Bold, size 11-12, white text on blue background
- Body: Regular, size 10-11
- Important notes: Bold or italic
- User inputs: Bold with colored background

### Cell Notes and Comments

Add notes to:
- User input cells (what to enter, valid range, examples)
- Complex formulas (explain calculation logic)
- Key assumptions (source, rationale, sensitivity)
- Unusual values (outliers, adjustments)
- Decision points (guidance on selection)

```python
add_cell_note(cell, 
    "Enter expected ultimate loss ratio based on pricing assumptions. "
    "Typical range: 0.60 to 0.70 for this line of business.")
```

### Sheet Organization

**Recommended sheet order:**
1. **Instructions/Overview:** Always first - explains purpose and how to use
2. **User Inputs/Selections:** Where user makes changes
3. **Summary/Results:** High-level outputs
4. **Detailed Calculations:** Supporting detail
5. **Reference Data:** Source data, historical information
6. **Metadata/Documentation:** Technical details, version info

**Sheet naming:**
- Use clear, descriptive names (max ~31 characters)
- Front-to-back workflow order
- Consider numbering: "1-Instructions", "2-Inputs", "3-Results"

### Freeze Panes

Always freeze panes to keep headers visible:
```python
# Freeze top row only
ws.freeze_panes = 'A2'

# Freeze top row and left column
ws.freeze_panes = 'B2'

# Freeze specific cell (freezes everything above and left)
ws.freeze_panes = 'C4'  # Freezes rows 1-3 and columns A-B
```

### Protection (Optional)

Protect sheets to prevent accidental changes, but allow input cells:
```python
from openpyxl.styles import Protection

# Protect the sheet
ws.protection.sheet = True
ws.protection.password = 'optional_password'

# Allow specific cells to be edited (user inputs)
for row in range(4, 10):
    cell = ws.cell(row=row, column=2)
    cell.protection = Protection(locked=False)
```

### Error Checking

Add validation and error indicators:
```python
# Data validation for numeric inputs
dv = DataValidation(type="decimal", operator="between", formula1=0, formula2=1)
dv.error = 'Loss ratio must be between 0 and 1'
dv.errorTitle = 'Invalid Input'
ws.add_data_validation(dv)
dv.add('B4:B10')

# Formula to check for errors
ws['E1'] = '=IF(COUNTIF(B:B,"#N/A")>0,"ERROR: Check for #N/A values","")'

# Conditional formatting to highlight errors
highlight_formula_errors(ws, 'B4:F20')
```

---

## Complete Working Example

Here's a complete example combining all best practices:

```python
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.worksheet.datavalidation import DataValidation
from datetime import datetime

def create_comprehensive_actuarial_workbook(output_path: str):
    """
    Complete example: Create actuarial workbook with all best practices.
    """
    # Sample data
    accident_years = [2020, 2021, 2022, 2023, 2024]
    latest_losses = [1_500_000, 1_750_000, 2_000_000, 1_800_000, 500_000]
    earned_premium = [2_500_000, 2_750_000, 3_000_000, 2_900_000, 2_600_000]
    
    wb = Workbook()
    wb.remove(wb['Sheet'])
    
    # === SHEET 1: INSTRUCTIONS ===
    ws_instructions = wb.create_sheet("Instructions", 0)
    ws_instructions['A1'] = "Reserve Analysis Workbook - Instructions"
    ws_instructions['A1'].font = Font(size=16, bold=True, color="4472C4")
    
    instructions_text = [
        "",
        "Purpose:",
        "This workbook helps you select loss development factors and expected loss ratios for reserve analysis.",
        "",
        "Workflow:",
        "1. Review the 'Reference Data' sheet to see historical loss data",
        "2. Go to the 'Selections' sheet and enter your selected parameters in YELLOW cells",
        "3. Review the 'Results' sheet to see ultimate loss projections (updates automatically)",
        "4. Compare results in the 'Summary' sheet",
        "",
        "Data as of: 2024-12-31",
        "Analysis date: " + datetime.now().strftime('%Y-%m-%d'),
    ]
    
    for idx, text in enumerate(instructions_text, start=1):
        cell = ws_instructions.cell(row=idx, column=1, value=text)
        cell.alignment = Alignment(wrap_text=True, vertical='top')
        if "Purpose:" in text or "Workflow:" in text:
            cell.font = Font(bold=True, size=12)
    
    ws_instructions.column_dimensions['A'].width = 100
    
    # === SHEET 2: REFERENCE DATA ===
    ws_reference = wb.create_sheet("Reference Data", 1)
    ws_reference['A1'] = "Historical Loss Data"
    ws_reference['A1'].font = Font(size=14, bold=True)
    
    ref_df = pd.DataFrame({
        'Accident Year': accident_years,
        'Latest Loss': latest_losses,
        'Earned Premium': earned_premium,
        'Loss Ratio': [l/p for l, p in zip(latest_losses, earned_premium)]
    })
    
    # Headers
    headers = list(ref_df.columns)
    for col_idx, header in enumerate(headers, start=1):
        cell = ws_reference.cell(row=3, column=col_idx, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")
    
    # Data
    for row_idx, row in ref_df.iterrows():
        for col_idx, value in enumerate(row, start=1):
            cell = ws_reference.cell(row=row_idx + 4, column=col_idx, value=value)
            
            if col_idx in [2, 3]:  # Loss, Premium
                cell.number_format = '#,##0'
            elif col_idx == 4:  # Loss Ratio
                cell.number_format = '0.0000'
    
    auto_fit_columns(ws_reference)
    ws_reference.freeze_panes = 'A4'
    
    # === SHEET 3: SELECTIONS ===
    ws_selections = wb.create_sheet("Selections", 2)
    ws_selections['A1'] = "Your Parameter Selections"
    ws_selections['A1'].font = Font(size=14, bold=True)
    add_cell_note(ws_selections['A1'], 
        "Enter your selected parameters in the YELLOW cells. "
        "These will be used to calculate ultimate losses in the Results sheet.")
    
    yellow_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                         top=Side(style='thin'), bottom=Side(style='thin'))
    
    # Parameter section
    ws_selections['A3'] = "Parameter"
    ws_selections['B3'] = "Your Selection"
    ws_selections['C3'] = "Notes/Rationale"
    format_header_row(ws_selections, 3, ['Parameter', 'Your Selection', 'Notes/Rationale'])
    
    parameters = [
        ('Loss Development Factor', 1.15, 'Factor to develop latest losses to ultimate'),
        ('Expected Loss Ratio', 0.65, 'A priori expected ultimate loss ratio'),
        ('Tail Factor', 1.02, 'Factor to develop from mature age to ultimate'),
    ]
    
    for idx, (param, default, note) in enumerate(parameters, start=4):
        ws_selections.cell(row=idx, column=1, value=param).font = Font(bold=True)
        
        cell_value = ws_selections.cell(row=idx, column=2, value=default)
        cell_value.fill = yellow_fill
        cell_value.border = thin_border
        cell_value.number_format = '0.0000'
        add_cell_note(cell_value, note)
        
        cell_notes = ws_selections.cell(row=idx, column=3)
        cell_notes.fill = yellow_fill
        cell_notes.border = thin_border
    
    # Add data validation
    dv_ldf = DataValidation(type="decimal", operator="between", formula1=1.0, formula2=5.0)
    dv_ldf.error = 'LDF must be between 1.0 and 5.0'
    ws_selections.add_data_validation(dv_ldf)
    dv_ldf.add('B4')
    
    dv_elr = DataValidation(type="decimal", operator="between", formula1=0.3, formula2=1.0)
    dv_elr.error = 'Loss ratio must be between 0.3 and 1.0'
    ws_selections.add_data_validation(dv_elr)
    dv_elr.add('B5')
    
    auto_fit_columns(ws_selections)
    ws_selections.freeze_panes = 'A4'
    
    # === SHEET 4: RESULTS ===
    ws_results = wb.create_sheet("Results", 3)
    ws_results['A1'] = "Ultimate Loss Projections"
    ws_results['A1'].font = Font(size=14, bold=True)
    add_cell_note(ws_results['A1'], 
        "Results calculated using your selections from the Selections sheet. "
        "Values update automatically when you change selections.")
    
    # Headers
    result_headers = ['Accident Year', 'Latest Loss', 'LDF', 'Ultimate Loss', 'IBNR']
    format_header_row(ws_results, 3, result_headers)
    
    # Data with formulas
    for idx, (acc_year, latest_loss) in enumerate(zip(accident_years, latest_losses), start=4):
        ws_results.cell(row=idx, column=1, value=acc_year)
        
        cell_latest = ws_results.cell(row=idx, column=2, value=latest_loss)
        cell_latest.number_format = '#,##0'
        
        # LDF (reference to Selections sheet)
        cell_ldf = ws_results.cell(row=idx, column=3)
        cell_ldf.value = "=Selections!$B$4"
        cell_ldf.number_format = '0.0000'
        
        # Ultimate (formula)
        cell_ult = ws_results.cell(row=idx, column=4)
        cell_ult.value = f"=B{idx}*C{idx}"
        cell_ult.number_format = '#,##0'
        add_cell_note(cell_ult, "Ultimate = Latest Loss × LDF")
        
        # IBNR (formula)
        cell_ibnr = ws_results.cell(row=idx, column=5)
        cell_ibnr.value = f"=D{idx}-B{idx}"
        cell_ibnr.number_format = '#,##0'
        add_cell_note(cell_ibnr, "IBNR = Ultimate - Latest Loss")
    
    # Total row
    total_row = 4 + len(accident_years)
    ws_results.cell(row=total_row, column=1, value="Total").font = Font(bold=True)
    
    for col in [2, 4, 5]:  # Latest, Ultimate, IBNR
        cell = ws_results.cell(row=total_row, column=col)
        col_letter = cell.column_letter
        cell.value = f"=SUM({col_letter}4:{col_letter}{total_row-1})"
        cell.number_format = '#,##0'
        cell.font = Font(bold=True)
    
    auto_fit_columns(ws_results)
    ws_results.freeze_panes = 'B4'
    
    # === SHEET 5: SUMMARY ===
    ws_summary = wb.create_sheet("Summary", 4)
    ws_summary['A1'] = "Executive Summary"
    ws_summary['A1'].font = Font(size=16, bold=True)
    
    ws_summary['A3'] = "Key Results:"
    ws_summary['A3'].font = Font(size=12, bold=True)
    
    summary_items = [
        ('Total Latest Losses', f"=Results!B{total_row}"),
        ('Total Ultimate Losses', f"=Results!D{total_row}"),
        ('Total IBNR', f"=Results!E{total_row}"),
        ('IBNR / Ultimate Ratio', f"=B6/B5"),
    ]
    
    for idx, (label, formula) in enumerate(summary_items, start=4):
        ws_summary.cell(row=idx, column=1, value=label).font = Font(bold=True)
        
        cell_value = ws_summary.cell(row=idx, column=2, value=formula)
        if 'Ratio' in label:
            cell_value.number_format = '0.00%'
        else:
            cell_value.number_format = '#,##0'
    
    auto_fit_columns(ws_summary)
    
    # === SAVE SAFELY AND OPEN ===
    safe_excel_save(wb, output_path)
    print(f"Comprehensive actuarial workbook created and opened: {output_path}")
    print(f"  - {len(wb.sheetnames)} sheets")
    print(f"  - Auto-fitted columns")
    print(f"  - Formulas linking Selections → Results")
    print(f"  - Cell notes on key parameters")
    print(f"  - Data validation on inputs")

# Helper functions (already defined above, included here for completeness)

def format_header_row(ws, row_num: int, headers: list):
    """Apply standard header formatting."""
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=row_num, column=col_idx, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

def auto_fit_columns(ws, min_width=10, max_width=50):
    """Auto-fit column widths based on content."""
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        
        for cell in column:
            try:
                if cell.value:
                    cell_length = len(str(cell.value))
                    max_length = max(max_length, cell_length)
            except:
                pass
        
        adjusted_width = min(max(max_length + 2, min_width), max_width)
        ws.column_dimensions[column_letter].width = adjusted_width

def add_cell_note(cell, note_text: str, author: str = "Claude"):
    """Add a comment/note to a cell."""
    comment = Comment(note_text, author)
    comment.width = 300
    comment.height = 100
    cell.comment = comment

# Example usage:
if __name__ == "__main__":
    create_comprehensive_actuarial_workbook("output/actuarial_workbook_example.xlsx")
```

---

## Troubleshooting

**Issue:** Formulas showing as text instead of calculating
- **Solution:** Ensure cell value starts with `=` and is a string when assigned
- **Example:** `cell.value = "=A1+B1"` not `cell.value = "A1+B1"`

**Issue:** Number formatting not applying
- **Solution:** Check that cell contains numeric value, not string
- **Solution:** Use `cell.number_format` not `cell.style.number_format`

**Issue:** Auto-fit makes columns too narrow/wide
- **Solution:** Set min_width and max_width parameters in `auto_fit_columns()`
- **Solution:** Manually adjust specific columns after auto-fit

**Issue:** Comments/notes not showing
- **Solution:** Ensure openpyxl version ≥ 3.0
- **Solution:** Comments only appear when hovering over cell (Excel feature)

**Issue:** Excel file is very large
- **Solution:** Avoid storing full DataFrames in memory, write row-by-row using openpyxl
- **Solution:** Use `openpyxl.worksheet._write_only.WriteOnlyWorksheet` for write-only operations with large datasets
- **Solution:** Compress using ZIP or 7-zip after creation

**Issue:** Conditional formatting not working
- **Solution:** Ensure cell range format is correct: 'A1:D10' not 'A1-D10'
- **Solution:** Formula rules need cell references relative to top-left of range

**Issue:** Data validation not preventing invalid input
- **Solution:** Sheet protection must be on for validation to be enforced
- **Solution:** Unlock specific cells before protecting sheet

---

## Additional Tips for Actuarial Users

1. **File Safety:** Always use `safe_excel_save()` to protect existing user work
   - Automatically archives existing files with timestamps before saving
   - Prevents accidental loss of user selections and modifications
   - Use `modify_existing_workbook()` when updating existing files

2. **Auto-Open Files:** Always open workbooks automatically for user review
   - Use `safe_excel_save(wb, path)` which opens automatically after saving
   - Never print "Please open file.xlsx" - open it programmatically
   - Saves time and improves user experience

3. **Named Ranges:** Use named ranges for key parameters so formulas are readable
   - Example: `=EarnedPremium * ExpectedLR` instead of `=B4*B5`

4. **Scenario Manager:** Consider adding Excel Table Scenarios for sensitivity analysis

5. **Pivot Tables:** For large data sets, consider pivot tables for user exploration

6. **Sparklines:** Add mini-charts in cells to show trends

7. **Slicers:** Add slicers to Excel tables for interactive filtering

8. **Version Control:** Include version number and date in filename
   - Example: `Reserve_Analysis_v1.2_2024-12-31.xlsx`
   - Archive backups are automatically timestamped: `Reserve_Analysis_backup_20260212_143022.xlsx`

9. **Documentation Sheet:** Always include a sheet with:
   - Purpose of workbook
   - Data sources and vintage
   - Key assumptions
   - Contact information
   - Revision history

10. **Audit Trail:** Consider adding a log sheet that records parameter changes

11. **Export Considerations:** If users need to import back to Python:
    - Keep structure simple and consistent
    - Use first row as headers
    - Avoid merged cells in data areas
    - Use separate sheets for inputs vs outputs

12. **Accessibility:** Use good color contrast, clear fonts, and descriptive text for accessibility

---

## Package References

**openpyxl Documentation:** https://openpyxl.readthedocs.io/

**pandas Excel I/O:** https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html

---

**Remember:** The goal is to create Excel workbooks that are self-documenting, interactive, and provide actuarial users with sufficient context to make informed decisions. Always prioritize clarity, usability, and reproducibility.

**Critical reminders:**
- ✅ **Check for templates FIRST:** Always look for Excel templates in the skill directory before creating from scratch
- ✅ **Use templates when available:** Copy, review, and carefully modify templates rather than recreating
- ✅ **Use openpyxl exclusively:** All Excel operations should use openpyxl (reading, writing, formatting, formulas)
- ✅ **Protect user work:** Use `safe_excel_save()` to archive existing files automatically
- ✅ **Auto-open files:** Never ask users to open files manually - open them programmatically
- ✅ **Check if exists:** Always check `os.path.exists()` before creating/modifying files
- ✅ **Modify, don't recreate:** Load existing workbooks to preserve user selections
