---
name: excel-formulas
description: Guidelines for creating formula-driven Excel workbooks with xlsxwriter. Inject live Excel formulas with cached values so workbooks display immediately and recalculate when actuaries change selections. Covers formula patterns, cross-workbook references, and shared formatting modules.
---

# Formula-Driven Excel Workbooks

## Quick Reference

**Core principle:** Inject live Excel formulas (not hard-coded values) with cached values so workbooks recalculate when actuaries change selections.

**Tool:** Use **xlsxwriter** for creating new workbooks - formulas display immediately with cached values. *(Historical note: We previously used openpyxl, but it creates formulas without cached values, causing blanks.)*

**Critical pattern:** Generate formula-driven Excel + JSON replica (xlsxwriter doesn't evaluate formulas, so JSON stores evaluated data for downstream scripts).

**Key utilities:** 
- `create_xlsxwriter_formats()` from `modules/xl_styles.py` for consistent formatting
- `col_letter()` helper to convert 0-based column index to Excel letters (A, B, C...)

---

## xlsxwriter Approach

### Basic Setup
```python
import xlsxwriter
from modules.xl_styles import create_xlsxwriter_formats

# Enable future functions to avoid compatibility warnings for STDEV.S, etc.
wb = xlsxwriter.Workbook('output.xlsx', {'use_future_functions': True})
fmt = create_xlsxwriter_formats(wb)
fmt['wb'] = wb  # Store reference for dynamic format creation

# Get first worksheet
ws = wb.add_worksheet('Sheet1')
```

### Key Features
- ✓ **Cached formula values:** Formulas display immediately (no blanks)
- ✓ **0-based indexing:** `ws.write_formula(row, col, formula, format, cached_value)`
- ✓ **use_future_functions:** Handles Excel 2010+ functions without compatibility warnings
- ✓ **Faster:** More efficient than openpyxl for creating new files

### Writing Formulas with Cached Values
```python
# Simple formula with cached value
ws.write_formula(2, 1, '=SUM(A1:A10)', fmt['data_num'], 55)

# CV formula with cached value from dataframe
cv_value = df4.loc[df4['metric'] == 'cv_3yr', measure].iloc[0]
ws.write_formula(row, col, '=IFERROR(STDEV.S(B49:B51)/AVERAGE(B49:B51),"")', fmt['data_ldf'], cv_value)

# ATA formula with cached value from lookup dict
cached_ldf = ldf_dict.get((str(period), interval))
ws.write_formula(row, col, f"={col_letter(col-1)}{row-1}/{col_letter(col-1)}{row}", fmt['data_ldf'], cached_ldf)
```

### Column Letter Helper
xlsxwriter uses 0-based indexing, but formulas need Excel column letters:
```python
def col_letter(col_idx):
    """Convert 0-based column index to Excel column letter (A, B, C, etc.)"""
    result = ''
    while col_idx >= 0:
        result = chr(col_idx % 26 + ord('A')) + result
        col_idx = col_idx // 26 - 1
    return result

# Usage:
formula = f"={col_letter(col-1)}{row-1}/{col_letter(col-1)}{row}"  # e.g., =B49/B48
```

---

## Overview

This codebase relies heavily on Excel workbooks not just for displaying outputs, but as live, interactive dashboards. Generated workbooks inject live Excel formulas so actuaries can interactively modify selections and see all downstream calculations update instantly without re-running Python scripts.

**Key pattern:** Generate formula-driven Excel + JSON replica (xlsxwriter doesn't evaluate formulas, so JSON stores evaluated data for downstream scripts).

**Use this approach when:**
- Actuaries need to modify selections and see results update in real-time
- The workbook serves as an interactive dashboard
- Downstream calculations depend on user-editable inputs
- Example: Chain Ladder Selections LDFs, Tail Factors, Ultimates

---

## Key Concepts

1. **Live Recalculation:** When an actuary changes a selection (e.g. an Age-to-Age factor or an Ultimate loss), all downstream cells (Cumulative Development Factors, Projected Ultimates, Summaries, Diagnostics) should instantly recalculate in Excel without needing to run a Python script.

2. **Cached Formula Values:** xlsxwriter allows you to provide cached values when writing formulas. This ensures formulas display immediately when the file is opened, without waiting for Excel to recalculate.

3. **JSON Replicas:** Since xlsxwriter doesn't evaluate formulas, Python scripts (and AI subagents) cannot read evaluated data from generated workbooks. Therefore, whenever a script generates a formula-driven Excel file, it MUST also serialize the fully-evaluated data into a corresponding JSON file (e.g. `selections/chainladder-incurred_loss.json`) for downstream consumption.

4. **0-Based Indexing:** xlsxwriter uses 0-based row/column indexing (`ws.write_formula(0, 0, ...)` writes to A1), but Excel formulas use 1-based references (`=A1`). Use the `col_letter()` helper to convert.

## Best Practices

- **Cache All Formulas:** Always provide cached values when writing formulas. Retrieve cached values from source dataframes (parquet files).
- **use_future_functions:** Always enable `{'use_future_functions': True}` when creating workbooks to avoid Excel compatibility warnings for STDEV.S, AVERAGE, etc.
- **Shared Formatting:** Use `create_xlsxwriter_formats()` from `modules/xl_styles.py` for consistent formatting across all workbooks.
- **Dynamic Format Creation:** For formulas needing custom number formats, use `fmt['wb'].add_format({...})` to create formats on-the-fly.
- **Formula Injection:** Keep formula strings simple. Abstract complex string-building into helper functions.
- **Downstream Safety:** Any script that reads data MUST read from source parquet files or the generated JSON replicas, NEVER from Excel files, unless it is specifically reading hard-coded input cells (like a "User Selection").
- **Write Numbers as Numbers:** Detect numeric values and use `.write_number()` instead of `.write()` to avoid "number formatted as text" warnings in Excel. Critical for period, age, and year columns.

### Avoiding "Number Formatted as Text" Warnings

Excel shows green warning triangles when numeric values are stored as text. Always detect and write actual numbers using the correct method:

```python
# ✓ CORRECT: Detect numeric type and write accordingly
def write_value(ws, row, col, value, fmt):
    """Write value using appropriate method based on type"""
    if pd.notna(value) and isinstance(value, (int, float, np.integer, np.floating)):
        ws.write_number(row, col, value, fmt)
    elif value is not None:
        ws.write(row, col, str(value), fmt)
    else:
        ws.write_blank(row, col, None, fmt)

# ✓ CORRECT: Check for numeric-like strings from dataframes
if pd.api.types.is_numeric_dtype(df[column]):
    ws.write_number(row, col, float(value), fmt)
else:
    ws.write(row, col, value, fmt)

# ❌ WRONG: Always writing with .write() when value might be numeric
ws.write(row, col, value, fmt)  # Will store numbers as text!

# ✓ CORRECT: For period/age columns specifically
period_val = row_data['period']
if isinstance(period_val, (int, float, np.integer, np.floating)):
    ws.write_number(r, col_map['period'], period_val, fmt['label'])
else:
    ws.write(r, col_map['period'], str(period_val), fmt['label'])
```

**When to use each method:**
- `ws.write_number(row, col, number, fmt)` - For int/float values
- `ws.write(row, col, text, fmt)` - For string values (auto-detects type, but less reliable)
- `ws.write_blank(row, col, None, fmt)` - For None/NaN values
- `ws.write_formula(row, col, formula, fmt, cached_value)` - For formulas with cached values

---

## Common Formula Patterns

### Statistical Formulas with Cached Values
```python
# CV (Coefficient of Variation) - retrieve cached value from dataframe
cv_value = df4.loc[df4['metric'] == 'cv_3yr', measure].iloc[0]
formula = f"=IFERROR(STDEV.S('{measure}'!B49:B51)/AVERAGE('{measure}'!B49:B51),\"\")"
ws.write_formula(row, col, formula, fmt['data_ldf'], cv_value)

# Slope - retrieve cached value from dataframe
slope_value = df4.loc[df4['metric'] == 'slope_3yr', measure].iloc[0]
formula = f"=IFERROR(SLOPE('{measure}'!B49:B51,{{1,2,3}}),\"\")"
ws.write_formula(row, col, formula, fmt['data_ldf'], slope_value)
```

### Age-to-Age (ATA) Formulas with Cached Values
```python
# Build lookup dict from source dataframe
ldf_dict = {}
for _, row in df2.iterrows():
    key = (str(row['period']), row['interval'])
    ldf_dict[key] = row['ldf']

# Write ATA formula with cached value
cached_ldf = ldf_dict.get((str(period), interval))
if cached_ldf is not None:
    formula = f"={col_letter(col-1)}{row-1}/{col_letter(col-1)}{row}"
    ws.write_formula(row, col, formula, fmt['data_ldf'], cached_ldf)
```

### Cross-Sheet References
Reference cells in other sheets within the same workbook:
```python
formula = f"='{sheet_name}'!{col_letter(col)}{row+1}"
formula = f"='Incurred Loss'!E{r}"
formula = f"='Diagnostics'!D{r}"
```

### Defensive Formulas
Prevent errors when cells might be blank or non-numeric:
```python
# Check both operands before calculation
formula = f'=IF(AND(ISNUMBER(C{r}),ISNUMBER(D{r})),C{r}*D{r},"")'

# Silent error handling
formula = f'=IFERROR(C{r}*D{r},"")'
```

### Simple Calculations
```python
formula = f"=SUM(C2:C{last_row})"
formula = f"=E{r}-C{r}"  # IBNR = Ultimate - Actual
formula = f"=1-(1/D{r})"  # % Unreported from CDF
```

---

## Complete Workflow Example

**Scenario:** Generate Chain Ladder Selections workbook with formulas that display immediately.

```python
import xlsxwriter
import pandas as pd
from modules.xl_styles import create_xlsxwriter_formats

def col_letter(col_idx):
    """Convert 0-based column index to Excel column letter"""
    result = ''
    while col_idx >= 0:
        result = chr(col_idx % 26 + ord('A')) + result
        col_idx = col_idx // 26 - 1
    return result

def build_main_sheet(ws, measure, df2, df4, fmt):
    """
    Build main LDF sheet with ATA formulas that have cached values.
    df2 contains LDF values, df4 contains diagnostic metrics.
    """
    # Write header
    ws.write(0, 0, "Chain Ladder Analysis", fmt['subheader'])
    
    # Build LDF lookup dict from source data
    ldf_dict = {}
    for _, row in df2[(df2['measure'] == measure)].iterrows():
        key = (str(row['period']), row['interval'])
        ldf_dict[key] = row['ldf']
    
    # Write triangle data with ATA formulas
    row = 5
    for period in periods:
        ws.write(row, 0, period, fmt['label'])
        
        for col_idx, age in enumerate(ages, start=1):
            # Get cached LDF value
            cached_ldf = ldf_dict.get((str(period), age))
            
            if cached_ldf is not None:
                # Write formula with cached value
                formula = f"={col_letter(col_idx-1)}{row-1}/{col_letter(col_idx-1)}{row}"
                ws.write_formula(row, col_idx, formula, fmt['data_ldf'], cached_ldf)
            
            row += 1

def build_cv_slopes_sheet(ws, measures, df4, fmt):
    """
    Build CV & Slopes sheet with statistical formulas that have cached values.
    df4 contains pre-calculated CV and slope values.
    """
    ws.write(0, 0, "CV & Slopes", fmt['subheader'])
    
    row = 2
    for measure in measures:
        # CV 3yr
        cv_value = df4.loc[(df4['metric'] == 'cv_3yr') & (df4['measure'] == measure), 'value'].iloc[0]
        formula = f"=IFERROR(STDEV.S('{measure}'!B49:B51)/AVERAGE('{measure}'!B49:B51),\"\")"
        ws.write_formula(row, 1, formula, fmt['data_ldf'], cv_value)
        
        # Slope 3yr
        slope_value = df4.loc[(df4['metric'] == 'slope_3yr') & (df4['measure'] == measure), 'value'].iloc[0]
        formula = f"=IFERROR(SLOPE('{measure}'!B49:B51,{{1,2,3}}),\"\")"
        ws.write_formula(row, 2, formula, fmt['data_ldf'], slope_value)
        
        row += 1

# Main execution
def main():
    output_file = '../selections/Chain Ladder Selections - LDFs.xlsx'
    
    # Load source data
    df2 = pd.read_parquet('processed-data/2_enhanced.parquet')
    df4 = pd.read_parquet('processed-data/4_ldf_averages.parquet')
    
    # Create workbook with future functions support
    wb = xlsxwriter.Workbook(output_file, {'use_future_functions': True})
    fmt = create_xlsxwriter_formats(wb)
    fmt['wb'] = wb  # Store reference for dynamic format creation
    
    # Build sheets
    for measure in ['Incurred Loss', 'Paid Loss', 'Reported Count']:
        ws = wb.add_worksheet(measure)
        build_main_sheet(ws, measure, df2, df4, fmt)
    
    ws_cv = wb.add_worksheet('CV & Slopes')
    build_cv_slopes_sheet(ws_cv, measures, df4, fmt)
    
    wb.close()
    print(f"Saved: {output_file}")
    print("  Formulas display immediately (cached values included)")

if __name__ == '__main__':
    main()
```

**Result:** 
- Workbook opens in Excel with all formulas displaying immediately (no blanks)
- No Excel compatibility warnings due to `use_future_functions`
- CV values show: 0.1604, 0.3284, etc.
- ATA values show: 1.2261, 1.6941, etc.
- When actuary changes base triangle values, all formulas recalculate automatically

---

## Working with Dynamic Formats

Some formulas need custom number formats based on data type. Use the stored workbook reference:

```python
def write_triangle(ws, start_row, title, data_dict, fmt, number_format="#,##0"):
    """Write a triangular data array with custom number format"""
    ws.write(start_row, 0, title, fmt['section'])
    
    # Create format with custom number format
    data_fmt = fmt['wb'].add_format({
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': number_format
    })
    
    row = start_row + 1
    for period, values in data_dict.items():
        ws.write(row, 0, period, fmt['label'])
        for col_idx, val in enumerate(values, start=1):
            if val is not None:
                ws.write(row, col_idx, val, data_fmt)
        row += 1
```

---

## JSON Replica Pattern

Always generate a JSON file alongside the Excel file for downstream consumption:

```python
import json

def export_selections_json(df, output_path):
    """Export selected LDF values to JSON for downstream scripts"""
    # Convert dataframe to dict structure
    data = {}
    for _, row in df.iterrows():
        measure = row['measure']
        if measure not in data:
            data[measure] = {}
        data[measure][row['interval']] = {
            'ldf': float(row['ldf']),
            'reasoning': row['reasoning'],
            'source': row['source']  # 'user' or 'rules-based-ai'
        }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

# Usage in main():
export_selections_json(
    selected_df, 
    '../selections/chainladder-incurred_loss.json'
)
```
