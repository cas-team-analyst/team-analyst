---
name: excel-formulas
description: Guidelines for creating formula-driven Excel workbooks with openpyxl. Inject live Excel formulas so workbooks recalculate when actuaries change selections. Covers formula patterns, cross-workbook references, and the openpyxl evaluation limitation that requires JSON replicas.
---

# Formula-Driven Excel Workbooks

## Quick Reference

**Core principle:** Inject live Excel formulas (not hard-coded values) so workbooks recalculate when actuaries change selections.

**Critical pattern:** Generate formula-driven Excel + JSON replica (openpyxl can't evaluate formulas, so JSON stores evaluated data for downstream scripts).

**Key utilities:** Use `rewrite_formula_sheet_refs()` from `modules/formulas.py` when aggregating sheets → [Best Practices](#best-practices)

---

## Overview

This codebase relies heavily on Excel workbooks not just for displaying outputs, but as live, interactive dashboards. Generated workbooks inject live Excel formulas so actuaries can interactively modify selections and see all downstream calculations update instantly without re-running Python scripts.

**Key pattern:** Generate formula-driven Excel + JSON replica (openpyxl can't evaluate formulas, so JSON stores evaluated data for downstream scripts).

**Use this approach when:**
- Actuaries need to modify selections and see results update in real-time
- The workbook serves as an interactive dashboard
- Downstream calculations depend on user-editable inputs
- Cross-workbook references are needed (linking multiple files together)
- Example: Chain Ladder Selections LDFs, Ultimates, Analysis

---

## Key Concepts

1. **Live Recalculation:** When an actuary changes a selection (e.g. an Age-to-Age factor or an Ultimate loss), all downstream cells (Cumulative Development Factors, Projected Ultimates, Summaries, Diagnostics) should instantly recalculate in Excel without needing to run a Python script.
2. **Openpyxl Limitation (`data_only=True`):** Openpyxl cannot evaluate Excel formulas. If you read a workbook with `data_only=True` before it has been opened and saved in Excel by a human, all formula-driven cells will return `None`.
3. **JSON Replicas:** Because of the openpyxl limitation, Python scripts (and AI subagents) cannot reliably read evaluated data from the generated workbooks. Therefore, whenever a script generates a formula-driven Excel file, it MUST also serialize the fully-evaluated data into a corresponding JSON file (e.g. `selections/chainladder-incurred_loss.json`) for downstream consumption.

## Best Practices

- **Use Relative Paths:** Always use relative paths for cross-workbook references (e.g., `"selections\\[Ultimates.xlsx]"`) so formulas work when folders are moved or shared. Avoid `os.path.abspath()` unless absolutely required.
- **Dynamic Discovery:** Never hard-code row/column numbers. Build discovery functions that search for labels like "User Selection", "Rules-Based AI Selection", "Tail Factor Selection", etc. Different runs may have different row structures.
- **Formula Injection:** Keep formula strings simple. Abstract complex string-building into helper functions. Keep formula injection logic adjacent to where it's used unless it's genuinely shared across scripts.
- **User Selection Priority:** Standard pattern is `=IF(UserCol<>"", UserCol, RulesBasedCol)`. Check User Selection first, fall back to Rules-Based AI Selection if blank.
- **Cross-Sheet References:** When aggregating multiple sheets into a master workbook, cross-sheet formula references (e.g. `='Incurred Loss'!B2`) must be dynamically rewritten if the sheet names change (e.g. `='CL - Incurred Loss'!B2`). Use the `rewrite_formula_sheet_refs` utility in `modules/formulas.py`.
- **Downstream Safety:** Any script that reads data MUST read from source parquet files or the generated JSON replicas, NEVER from Excel files, unless it is specifically reading hard-coded input cells (like a "User Selection").

---

## Common Formula Patterns

### Cross-Workbook References (Relative Paths - PREFERRED)
**Use relative paths so formulas work regardless of folder location:**
```python
# Relative paths - Excel updates links without prompting
_ULT_WB = "selections\\[Ultimates.xlsx]"
_CL_LDF_WB = "selections\\[Chain Ladder Selections - LDFs.xlsx]"
_CL_TAIL_WB = "selections\\[Chain Ladder Selections - Tail.xlsx]"

formula = f"='{_ULT_WB}{sheet_name}'!{col}{row}"
formula = f"='{_CL_LDF_WB}{measure}'!B{row}"
```

**Avoid absolute paths unless required:**
```python
# Absolute paths - brittle, breaks when folder moves
_ULT_WB = os.path.abspath(config.SELECTIONS) + "\\[Ultimates.xlsx]"  # ❌ Avoid
```

### Dynamic Structure Discovery
**Never hard-code row/column numbers** - workbook structure may vary between runs. Build utilities to dynamically discover positions:

```python
def _build_cl_ldfs_col_row_maps(wb_cl, measure_sheet_name):
    """
    Discover row/column positions in Chain Ladder Selections - LDFs.xlsx.
    Returns (col_map, user_row, rb_row, user_reason_row, rb_reason_row).
    """
    if measure_sheet_name not in wb_cl.sheetnames:
        return {}, None, None, None, None
    
    ws = wb_cl[measure_sheet_name]
    col_map = {}
    user_row = rb_row = user_reason_row = rb_reason_row = None
    
    for row_idx, row_cells in enumerate(ws.iter_rows(), start=1):
        col1 = row_cells[0].value if row_cells else None
        
        # Find column headers (usually None in col A)
        if col1 is None and row_idx <= 10:
            for cell in row_cells[1:]:
                if cell.value is not None:
                    col_map[str(cell.value)] = get_column_letter(cell.column)
        
        # Find selection rows by label
        if col1 == "User Selection":
            user_row = row_idx
        elif col1 == "Rules-Based AI Selection":
            rb_row = row_idx
        elif col1 == "User Reasoning":
            user_reason_row = row_idx
        elif col1 == "Rules-Based AI Reasoning":
            rb_reason_row = row_idx
    
    return col_map, user_row, rb_row, user_reason_row, rb_reason_row

def _build_tail_workbook_maps(tail_wb_path, measure_sheet_name):
    """
    Discover structure in Tail Factor Selection workbook.
    Returns (cutoff_col, tail_col, reason_col, user_row, rb_row).
    """
    if not pathlib.Path(tail_wb_path).exists():
        return None, None, None, None, None
    
    try:
        wb = load_workbook(tail_wb_path, data_only=False)
        if measure_sheet_name not in wb.sheetnames:
            wb.close()
            return None, None, None, None, None
        
        ws = wb[measure_sheet_name]
        in_tail_section = False
        cutoff_col = tail_col = reason_col = None
        user_row = rb_row = None
        
        for row_idx, row_cells in enumerate(ws.iter_rows(), start=1):
            col1 = row_cells[0].value if row_cells else None
            
            # Find section boundary
            if col1 == "Tail Factor Selection":
                in_tail_section = True
                continue
            
            if not in_tail_section:
                continue
            
            # Find column headers
            if col1 == "Label":
                for cell in row_cells:
                    if cell.value == "Cutoff Age":
                        cutoff_col = get_column_letter(cell.column)
                    elif cell.value == "Tail Factor":
                        tail_col = get_column_letter(cell.column)
                    elif cell.value == "Reasoning":
                        reason_col = get_column_letter(cell.column)
                continue
            
            # Find selection rows
            if col1 == "User Selection":
                user_row = row_idx
            elif col1 == "Rules-Based AI Selection":
                rb_row = row_idx
        
        wb.close()
        return cutoff_col, tail_col, reason_col, user_row, rb_row
    except Exception:
        return None, None, None, None, None
```

### User Selection Priority Pattern
**Standard pattern:** IF User Selection is not blank, use it; otherwise fall back to Rules-Based AI Selection:

```python
# For LDF selections (discovered row numbers)
ext_ref = f"'{_CL_LDF_WB}{measure}'"
col_letter = get_column_letter(src_cell.column)
formula = f'=IF({ext_ref}!{col_letter}{user_row}<>"",{ext_ref}!{col_letter}{user_row},{ext_ref}!{col_letter}{rb_row})'

# For tail factor selections (discovered row numbers)
tail_ref = f"'{_CL_TAIL_WB}{measure}'"
formula = f'=IF({tail_ref}!{tail_col}{user_row}<>"",{tail_ref}!{tail_col}{user_row},{tail_ref}!{tail_col}{rb_row})'

# For reasoning (check selection column, pull from reasoning column)
formula = f'=IF({tail_ref}!{tail_col}{user_row}<>"",{tail_ref}!{reason_col}{user_row},{tail_ref}!{reason_col}{rb_row})'
```

**Key insight:** Check if User Selection column is populated, then pull from the appropriate row. Don't hard-code row numbers - use dynamic discovery.

### Cross-Sheet References
Reference cells in other sheets within the same workbook:
```python
formula = f"='{sheet_name}'!{col}{row}"
formula = f"='Inc Loss CL'!E{r}"
formula = f"='IE'!D{r}"  # Reference the IE sheet
```

### Defensive Formulas
Prevent errors when cells might be blank or non-numeric:
```python
# Check both operands before multiplication
formula = f'=IF(AND(ISNUMBER(C{r}),ISNUMBER(D{r})),C{r}*D{r},"")'

# Fallback when primary reference fails
formula = f'=IF({ext_ref}!{user_col}{r}<>"",{ext_ref}!{user_col}{r},{ext_ref}!{rb_col}{r})'

# Silent error handling
formula = f'=IFERROR({sel_ref}*{next_ref},"")'
```

### Simple Calculations
```python
formula = f"=SUM(C2:C{last_row})"
formula = f"=E{r}-C{r}"  # IBNR = Ultimate - Actual
formula = f"=1-(1/D{r})"  # % Unreported from CDF
```

---

## Complete Workflow Example

**Scenario:** Copy triangle worksheet from Chain Ladder Selections - LDFs.xlsx with formulas that link back to the source workbook.

```python
def _copy_ws_with_ldfs_formulas(ws_src, ws_dst, measure_short_name, cl_ldfs_path):
    """
    Copy worksheet writing formulas that link to Chain Ladder Selections - LDFs.xlsx.
    Selection rows use IF formula: User Selection if not blank, else Rules-Based AI.
    Data rows reference the source workbook.
    """
    # 1. Load source workbook and discover structure
    if not pathlib.Path(cl_ldfs_path).exists():
        _copy_ws_filtered(ws_src, ws_dst, None, None)  # Fallback to value copy
        return
    
    wb_cl = load_workbook(cl_ldfs_path, data_only=False)
    col_map, user_row, rb_row, user_reason_row, rb_reason_row = _build_cl_ldfs_col_row_maps(wb_cl, measure_short_name)
    wb_cl.close()
    
    if not col_map or user_row is None or rb_row is None:
        # Fallback if structure not found
        sel_vals = _find_selected_values(ws_src)
        sel_reason = _find_selected_reasoning(ws_src)
        _copy_ws_filtered(ws_src, ws_dst, sel_vals, sel_reason)
        return
    
    # 2. Set up relative reference
    ext_ref = f"'{_CL_LDF_WB}{measure_short_name}'"  # e.g., 'selections\[..LDFs.xlsx]Incurred Loss'
    
    # 3. Copy rows with formulas
    selection_done = False
    dst_row = 1
    
    for src_cells in ws_src.iter_rows():
        col1 = src_cells[0].value if src_cells else None
        
        # Skip AI option/reasoning rows
        if col1 in SKIP_ROW_LABELS:
            continue
        
        # Handle selection rows - write IF formula
        if col1 in SELECTION_LABELS:
            if selection_done:
                continue
            selection_done = True
            
            # Write "Selected" row with IF formulas checking User > RB-AI
            for src_cell in src_cells:
                dst_cell = ws_dst.cell(dst_row, src_cell.column)
                if src_cell.column == 1:
                    dst_cell.value = "Selected"
                else:
                    col_letter = get_column_letter(src_cell.column)
                    # IF User not blank, use User, else use RB-AI
                    formula = f'=IF({ext_ref}!{col_letter}{user_row}<>"",{ext_ref}!{col_letter}{user_row},{ext_ref}!{col_letter}{rb_row})'
                    dst_cell.value = formula
                
                # Copy styling
                if src_cell.has_style:
                    dst_cell.font = copy.copy(src_cell.font)
                    dst_cell.border = copy.copy(src_cell.border)
                    dst_cell.fill = copy.copy(src_cell.fill)
                    dst_cell.number_format = src_cell.number_format
                    dst_cell.alignment = copy.copy(src_cell.alignment)
            dst_row += 1
            
            # Write "Selected Reasoning" row with IF formula
            if user_reason_row and rb_reason_row:
                for src_cell in src_cells:
                    dst_cell = ws_dst.cell(dst_row, src_cell.column)
                    if src_cell.column == 1:
                        dst_cell.value = "Selected Reasoning"
                    else:
                        col_letter = get_column_letter(src_cell.column)
                        formula = f'=IF({ext_ref}!{col_letter}{user_row}<>"",{ext_ref}!{col_letter}{user_reason_row},{ext_ref}!{col_letter}{rb_reason_row})'
                        dst_cell.value = formula
                    
                    if src_cell.has_style:
                        dst_cell.font = copy.copy(src_cell.font)
                        dst_cell.border = copy.copy(src_cell.border)
                        dst_cell.fill = copy.copy(src_cell.fill)
                    dst_cell.number_format = ""
                    dst_cell.alignment = Alignment(wrap_text=True, horizontal="left", vertical="top")
                dst_row += 1
            continue
        
        # Copy all other rows with formulas linking to source
        for src_cell in src_cells:
            dst_cell = ws_dst.cell(dst_row, src_cell.column)
            
            # For data cells (not labels), write formula; for labels, copy value
            if src_cell.column == 1 or src_cell.value is None or isinstance(src_cell.value, str):
                dst_cell.value = src_cell.value
            else:
                # Reference the source workbook
                col_letter = get_column_letter(src_cell.column)
                row_num = src_cells[0].row
                dst_cell.value = f"={ext_ref}!{col_letter}{row_num}"
            
            if src_cell.has_style:
                dst_cell.font = copy.copy(src_cell.font)
                dst_cell.border = copy.copy(src_cell.border)
                dst_cell.fill = copy.copy(src_cell.fill)
                dst_cell.number_format = src_cell.number_format
                dst_cell.alignment = copy.copy(src_cell.alignment)
        
        dst_row += 1

# Usage:
for measure in measures:
    ws = gen_wb.create_sheet(title=measure_short_name(measure)[:31])
    _copy_ws_with_ldfs_formulas(wb_cl_form[measure], ws, measure, INPUT_CL_EXCEL)
```

**Result:** Triangle worksheet in Analysis.xlsx contains formulas like:
- Data cells: `='selections\[Chain Ladder Selections - LDFs.xlsx]Incurred Loss'!B3`
- Selection cells: `=IF('selections\[..LDFs.xlsx]Incurred Loss'!B78<>"", ..B78, ..B72)`
- When actuary changes selections in the source workbook, Analysis.xlsx updates automatically
