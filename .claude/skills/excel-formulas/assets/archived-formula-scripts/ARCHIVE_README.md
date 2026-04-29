# Archived Formula-Based Excel Scripts

**Archive Date:** April 29, 2026  
**Reason:** Simplifying Excel workbook generation by removing formula-based approach in favor of hard-coded values

---

## What's Archived Here

This directory contains the original formula-based versions of the TeamAnalyst Excel generation scripts and supporting modules, preserved for potential future restoration.

### Scripts (from `skills/reserving-analysis/scripts/`)

1. **2a-chainladder-create-excel.py** (~600 lines)
   - Original: Generated Chain Ladder LDF selections workbook with formulas
   - Had: `atoa_formula()`, `simple_avg_formula()`, `weighted_avg_formula()`, `excl_hl_formula()`
   - Formula features: Age-to-age factors as formulas, average calculations as formulas, diagnostic triangles with cross-sheet formulas

2. **2d-tail-create-excel.py**
   - Original: Generated tail factor selections workbook with cross-workbook formula references
   - Had: External references to `[Chain Ladder Selections - LDFs.xlsx]` for selected LDFs
   - Formula features: Cross-workbook formulas, tail factor lookups via formulas

3. **5a-ultimates-create-excel.py**
   - Original: Generated ultimates selections workbook
   - Formula features: Minimal (mostly static values with some formula references)

4. **6-analysis-create-excel.py** (~1,826 lines - the "main offender")
   - Original: Generated complete analysis workbook with extensive formula-based logic
   - Had: `_formula_cell()`, `_ult_ref()`, `_exp_ref()`, `_add_cdf_formulas_to_triangle()`
   - Formula features:
     - Cross-workbook references to Ultimates.xlsx, Chain Ladder Selections - LDFs.xlsx, Chain Ladder Selections - Tail.xlsx
     - IF-formula selection logic: `=IF(UserCell<>"",UserCell,RulesBasedCell)`
     - CDF (cumulative development factor) formulas
     - External workbook absolute path references

### Modules (from `skills/reserving-analysis/scripts/modules/`)

1. **formulas.py** (100% unused dead code)
   - Function: `rewrite_formula_sheet_refs()` - rewrites sheet references in Excel formulas
   - Used for: Renaming sheets while preserving formula references

2. **verify_formulas.py** (Windows-only, Excel COM-based)
   - Function: `run_verify()` - opens Complete Analysis.xlsx in Excel via win32com, force-recalculates, compares formula results against Values Only workbook
   - Dependencies: pywin32, Excel desktop application
   - Used by: 6b-create-values-only.py (if it existed)

3. **xl_values.py** (full copy - has mixed content)
   - Formula-related functions (unused):
     - `_fill_method_cl_values()`, `_fill_method_bf_values()`, `_fill_method_ie_values()`
     - `_fill_selection_values()`, `_fill_cdf_row_values()`, `_fill_cl_main_values()`, `_fill_tail_values()`
     - `_strip_formulas()`
   - Active functions (kept in working version):
     - `UNPAID_PROXY` constant
     - `_has_method()` function

---

## Why Formulas Were Removed

1. **Maintenance complexity:** Formula generation required extensive Excel row/column reference tracking, 0-based vs 1-based indexing conversions, and cross-workbook path management
2. **Script size:** Script 6 was ~1,826 lines, largely due to formula generation logic
3. **Compatibility issues:** Cross-workbook formulas with absolute paths caused issues when files were moved
4. **Limited value:** Actuaries review these workbooks but don't recalculate formulas - they make selections and move on to the next step
5. **Better approach:** Hard-coded values from source data (parquet files, Excel selections) are simpler, more reliable, and sufficient for the workflow

---

## How to Restore (If Needed)

If formula-based Excel generation needs to be restored:

### For Individual Scripts

1. **Copy archived script back to active location:**
   ```powershell
   Copy-Item ".claude\skills\excel-formulas\assets\archived-formula-scripts\2a-chainladder-create-excel.py" `
             "skills\reserving-analysis\scripts\2a-chainladder-create-excel.py" -Force
   ```

2. **Copy archived modules back to active location:**
   ```powershell
   Copy-Item ".claude\skills\excel-formulas\assets\archived-formula-scripts\modules\formulas.py" `
             "skills\reserving-analysis\scripts\modules\formulas.py" -Force
   Copy-Item ".claude\skills\excel-formulas\assets\archived-formula-scripts\modules\verify_formulas.py" `
             "skills\reserving-analysis\scripts\modules\verify_formulas.py" -Force
   Copy-Item ".claude\skills\excel-formulas\assets\archived-formula-scripts\modules\xl_values.py" `
             "skills\reserving-analysis\scripts\modules\xl_values.py" -Force
   ```

### For Full Restoration

```powershell
# Restore all scripts
Copy-Item ".claude\skills\excel-formulas\assets\archived-formula-scripts\*.py" `
          "skills\reserving-analysis\scripts\" -Force

# Restore all modules
Copy-Item ".claude\skills\excel-formulas\assets\archived-formula-scripts\modules\*.py" `
          "skills\reserving-analysis\scripts\modules\" -Force
```

### Notes on Restoration

- **Verify dependencies:** Ensure xlsxwriter supports the formula patterns used
- **Test thoroughly:** Run against sample-data to ensure formulas generate correctly
- **Check paths:** Update any hardcoded absolute paths in script 6 (`_ULT_WB`, `_CL_LDF_WB`, `_CL_TAIL_WB`)
- **Windows requirement:** verify_formulas.py requires Windows + pywin32 + Excel desktop

---

## Archive Contents

```
archived-formula-scripts/
├── ARCHIVE_README.md (this file)
├── 2a-chainladder-create-excel.py
├── 2d-tail-create-excel.py
├── 5a-ultimates-create-excel.py
├── 6-analysis-create-excel.py
└── modules/
    ├── formulas.py
    ├── verify_formulas.py
    └── xl_values.py
```

---

## Related Documentation

- [skills/excel-formulas/SKILL.md](../../SKILL.md) - Updated skill documentation noting formula archival
- Original implementation date: Before April 2026
- Simplified (values-only) implementation date: April 29, 2026
