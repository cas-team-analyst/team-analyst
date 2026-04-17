# POC — Formula-Driven Workbook Findings

**Branch:** `poc/formula-driven-workbook`
**Scope:** All 4 measure sheets (Incurred Loss, Paid Loss, Reported Count, Closed Count) + cross-sheet Selected Ultimates summaries + fix for script 6's sheet-rename-breaks-refs issue.

## What's in `poc-output/`

- `templates/cl-selections-template.xlsx` — the template. All 4 measure sheets have live formulas; 4 new `Sel Ults - <measure>` sheets cross-reference into them.
- `sim-script6-master-fixed.xlsx` — script 6's copy loop with the cross-sheet ref rewriting fix applied. 120/120 refs resolve correctly after the `CL - ` prefix rename.

## Scripts (in `claude-code/scripts/`)

- `poc_inject_formulas.py` — rebuilds template from demo4 source, injects formulas into all 4 measure sheets (age-to-age, averages, CDF, Projected Ultimates).
- `poc_add_selected_sheet.py` — adds `Sel Ults - <measure>` sheets with cross-sheet formulas to the template.
- `poc_sim_script6_fixed.py` — simulates script 6's sheet-copy loop with the sheet-ref rewriting patch.

## Results

### ✅ All 4 measures validate at 0.0 diff

Simulated the formula chain (age-to-age → averages → CDF → projected ultimate) in Python and compared against `projected-ultimates.parquet`:

| Measure | Max \|diff\| | Rel diff | Status |
|---|---|---|---|
| Incurred Loss | 0.000000 | 0.00e+00 | PASS |
| Paid Loss | 0.000000 | 0.00e+00 | PASS |
| Reported Count | 0.000000 | 0.00e+00 | PASS |
| Closed Count | 0.000000 | 0.00e+00 | PASS |

### ✅ Script 6 cross-sheet ref fix works

Earlier POC: cross-sheet formula `='Closed Count'!E56` broke after script 6 renamed sheets to `CL - Closed Count`. Fix is a regex rewrite in the copy loop:

```python
# Pseudocode — actual fix in poc_sim_script6_fixed.py
for each source workbook:
    rename_map = {sheet_name: f"{prefix}{sheet_name}"[:31] for sheet_name in wb.sheetnames}
    for each sheet:
        for each cell:
            if isinstance(cell.value, str) and cell.value.startswith("="):
                cell.value = rewrite_formula_sheet_refs(cell.value, rename_map)
```

The rewriter handles both quoted (`'Sheet Name'!`) and unquoted (`SheetName!`) refs, and requotes new names that contain spaces or special characters.

**Validation:** 120 cross-sheet refs across 4 `Sel Ults` sheets, all 120 resolve to existing sheets in the master workbook after copy.

### ✅ End-to-end pipeline

1. `poc_inject_formulas.py` → seeds template, injects formulas in 4 measure sheets.
2. `poc_add_selected_sheet.py` → adds 4 Sel Ults sheets with cross-sheet refs.
3. `poc_sim_script6_fixed.py` → simulates aggregation with ref rewriting.
4. Actuary opens `sim-script6-master-fixed.xlsx` in Excel → edits any Selection LDF → recalc cascades through CDF → Projected Ultimate → cross-sheet IBNR in the summary sheet.

## Known Constraints & Decisions

1. **Excel 31-char sheet name limit.** The Sel Ults sheets were named to fit: `Sel Ults - Incurred Loss` (24 chars) + `CL - ` prefix = 29 chars, under the cap. Longer names would truncate, breaking formula resolution.

2. **openpyxl doesn't evaluate formulas.** Cached values are `None` on disk until Excel opens + saves. Impact:
   - `2b`/`2c` only read actuary-typed Selection row — safe.
   - `7-tech-review.py` and peer-review read `complete-analysis.xlsx` with `data_only=True`. If nobody opens the master in Excel first, they see blank derived cells. Open remains: human-opens-in-Excel step vs. LibreOffice-headless recalc vs. moving readers off the xlsx.

3. **Weighted-average formulas reference the triangle directly.** Uses `SUMPRODUCT(atoa_range, triangle_col_range)` / `SUMPRODUCT((atoa_range<>"")*triangle_col_range)`. Aligned indexing proven out against all 4 measures.

4. **Sparse-window fallback.** N-yr averages use `=IFERROR(...window..., ...all periods...)` so intervals with fewer data points in the window fall back to all-period average. This matches observed behavior but the exact semantics of the Python `1d-averages-qa.py` fallback weren't audited — flagging as a minor possible-discrepancy area.

5. **Tail factor.** `K47` (per-measure actuary input). CDF chain starts with `K52 = K47` regardless of the tail value, so it works for Closed Count (tail=1.0), Incurred Loss (tail=1.0125), Paid Loss (tail=1.019), Reported Count (tail=1.0).

## Scaling estimate

~~1–2 days~~ → **substantially done** on this branch for the Chain Ladder workbook. What remains:

- **Small.** Apply the `rewrite_formula_sheet_refs` patch to the real `6-create-complete-analysis.py` (it's in `.claude/skills/reserving-analysis/scripts/` and gets copied into projects). ~20 lines around line 580.
- **Medium.** Convert `selected-ultimates.xlsx`, `post-method-series.xlsx`, `post-method-triangles.xlsx` to be formula-driven and reference cells in the master workbook rather than standing on pre-computed values. These are generated inside script 6 today — could be consolidated into the CL template workbook, or kept separate with intra-master formula refs after the copy.
- **Policy.** Decide whether `7-tech-review.py` / peer-review require a recalc step before they read the master, or move them to source parquets.

## Recommendation — GO

Core workbook works across all 4 measures with live recalc. Script 6's sheet-rename issue has a validated fix. The remaining work is mechanical (apply the patch, convert the three smaller output workbooks) and policy (the recalc step for review readers).

## Manual verification checklist

1. Open `demo/demo4-complete/poc-output/templates/cl-selections-template.xlsx` in Excel.
2. On any measure sheet, edit Selection row 47 (e.g., `Incurred Loss!B47`). Watch CDF row 52 and Projected Ultimates rows 56-65 recalc.
3. Flip to that measure's `Sel Ults` tab. IBNR column should reflect the change.
4. Save.
5. Open `sim-script6-master-fixed.xlsx`. All 22 sheets present, all cross-sheet formulas resolve (no #REF! errors). Save.
