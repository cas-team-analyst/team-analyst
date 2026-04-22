---
name: excel-formulas
description: Guidelines and utility knowledge for working with formula-driven Excel workbooks and openpyxl.
---

# Formula-Driven Excel Workbooks

This codebase relies heavily on Excel workbooks not just for displaying outputs, but as live, interactive dashboards. To support this, generated workbooks must inject live Excel formulas rather than hard-coded values wherever a value can be derived. 

## Key Concepts

1. **Live Recalculation:** When an actuary changes a selection (e.g. an Age-to-Age factor or an Ultimate loss), all downstream cells (Cumulative Development Factors, Projected Ultimates, Summaries, Diagnostics) should instantly recalculate in Excel without needing to run a Python script.
2. **Openpyxl Limitation (`data_only=True`):** Openpyxl cannot evaluate Excel formulas. If you read a workbook with `data_only=True` before it has been opened and saved in Excel by a human, all formula-driven cells will return `None`.
3. **JSON Replicas:** Because of the openpyxl limitation, Python scripts (and AI subagents) cannot reliably read evaluated data from the generated workbooks. Therefore, whenever a script generates a formula-driven Excel file, it MUST also serialize the fully-evaluated data into a corresponding JSON file (e.g. `selections/chainladder-incurred_loss.json`) for downstream consumption.

## Best Practices

- **Formula Injection:** Keep formula strings simple. Abstract complex string-building into helper functions. Keep formula injection logic adjacent to where it's used unless it's genuinely shared across scripts.
- **Cross-Sheet References:** When aggregating multiple sheets into a master workbook, cross-sheet formula references (e.g. `='Incurred Loss'!B2`) must be dynamically rewritten if the sheet names change (e.g. `='CL - Incurred Loss'!B2`). Use the `rewrite_formula_sheet_refs` utility in `modules/formulas.py`.
- **Downstream Safety:** Any script that reads data MUST read from source parquet files or the generated JSON replicas, NEVER from Excel files, unless it is specifically reading hard-coded input cells (like a "User Selection").
