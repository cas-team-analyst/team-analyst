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

- **Formula Injection:** Keep formula strings simple. Abstract complex string-building into helper functions. Keep formula injection logic adjacent to where it's used unless it's genuinely shared across scripts.
- **Cross-Sheet References:** When aggregating multiple sheets into a master workbook, cross-sheet formula references (e.g. `='Incurred Loss'!B2`) must be dynamically rewritten if the sheet names change (e.g. `='CL - Incurred Loss'!B2`). Use the `rewrite_formula_sheet_refs` utility in `modules/formulas.py`.
- **Downstream Safety:** Any script that reads data MUST read from source parquet files or the generated JSON replicas, NEVER from Excel files, unless it is specifically reading hard-coded input cells (like a "User Selection").

---

## Common Formula Patterns

### Cross-Workbook References
Link to cells in external workbooks using absolute paths:
```python
_ULT_WB = os.path.abspath(config.SELECTIONS) + "\\[Ultimates.xlsx]"
formula = f"='{_ULT_WB}{sheet_name}'!{col}{row}"
```

### Cross-Sheet References
Reference cells in other sheets within the same workbook:
```python
formula = f"='{sheet_name}'!{col}{row}"
formula = f"='Inc Loss CL'!E{r}"
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
