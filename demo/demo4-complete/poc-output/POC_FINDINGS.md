# POC — Formula-Driven Workbook Findings

**Branch:** `poc/formula-driven-workbook`
**Status:** Full Chain Ladder + summary pipeline formula-driven, end-to-end validated.

## What's formula-driven now

Every derived cell downstream of actuary inputs (selected LDFs + selected ultimates) is a live Excel formula:

- **4 measure sheets** (Incurred Loss, Paid Loss, Reported Count, Closed Count):
  age-to-age, averages (simple / weighted / exclude-hi-lo × all/3yr/5yr/10yr), CDF chain, Projected Ultimates.
- **4 Sel Ults sheets** (one per measure): Actual, CL, Selected Ultimate, IBNR — cross-sheet refs into the measure sheets.
- **Ult Severity**: Incurred Ultimate / Reported Ultimate per period.
- **4 X-to-Ult ratio triangles** (one per measure): triangle cell / selected ultimate per period.
- **Avg IBNR triangle**: Incurred Ultimate − Incurred at each age.
- **Avg Unpaid triangle**: Incurred Ultimate − Paid at each age.

What's **NOT** formula-driven:
- Exposure-dependent diagnostics (Loss Rate, Frequency). Exposure lives in the triangles parquet, not the CL workbook. Trivially addable by either injecting an Exposure sheet or accepting hard-coded values.
- Initial Expected / BF ultimates (intermediate columns in Sel Ults). Those come from scripts 3 and 4 and would require replicating their logic in formulas. The Selected Ultimate column defaults to CL, which the actuary can override.
- Diag-* and CV & Slopes sheets: pure diagnostic read-outs, no actuary inputs — left hard-coded.

## The real `6-create-complete-analysis.py` is patched

`rewrite_formula_sheet_refs` added as a module-level helper in the skill's `6-create-complete-analysis.py:75-105`. The copy loop at `:567-596` now builds a `{old_sheet_name: prefixed_name}` map per source workbook and runs every formula string through the rewriter before assigning to the destination cell. Quoted refs (`'Sheet Name'!`) and unquoted refs (`Sheet!`) both handled. Same patch applied to `demo/demo4-complete/scripts/6-create-complete-analysis.py`.

**Smoke test (`scripts/poc_smoke_test_script6.py`)**: runs the patched script 6 against the formula template. Output at `poc-output/complete-analysis-poc.xlsx`. **2,070/2,070 cross-sheet refs resolve.** Spot-checks show formulas survived the copy + prefix intact.

## Scripts (in `claude-code/scripts/`)

| Script | Purpose |
|---|---|
| `poc_inject_formulas.py` | Reseeds template from demo4 source, injects formulas into all 4 measure sheets |
| `poc_add_selected_sheet.py` | Adds 4 `Sel Ults - <measure>` cross-sheet summary sheets |
| `poc_add_post_method_sheets.py` | Adds Ult Severity, 4 X-to-Ult triangles, Avg IBNR, Avg Unpaid |
| `poc_sim_script6_fixed.py` | Pre-script-6 POC version of the sheet-ref rewriter |
| `poc_smoke_test_script6.py` | Runs patched script 6 end-to-end, verifies refs resolve |

Run order for a full rebuild:
```
python poc_inject_formulas.py          # 4 measure sheets
python poc_add_selected_sheet.py       # + 4 Sel Ults sheets
python poc_add_post_method_sheets.py   # + 7 post-method sheets
python poc_smoke_test_script6.py       # aggregate into complete-analysis-poc.xlsx
```

## Validation

- **CL ultimate values** — 0.0 diff across all 4 measures vs `projected-ultimates.parquet`. Formulas compute exactly what the Python pipeline computes.
- **Cross-sheet refs** — 2,070/2,070 resolve after script 6's prefix rename. No `#REF!` errors.
- **Formula integrity** — openpyxl's `cell.value = cell.value` copy preserves formula strings verbatim, and the rewriter catches every sheet ref.

## Still to do

1. **Exposure-dependent diagnostics** — inject Exposure into the template (from triangles parquet) and add Loss Rate / Frequency formulas in the Ult Severity sheet or a sibling.
2. **Recalc policy for `data_only=True` readers** — `7-tech-review.py` and peer-review read `complete-analysis.xlsx` expecting cached values. Options:
   - Actuary opens the master in Excel and saves (human step) before review scripts run.
   - LibreOffice headless recalc (`soffice --headless --calc --convert-to xlsx` round-trip) before review.
   - Migrate review scripts to read source parquets directly.
3. **Decide what to do with the three legacy intermediate workbooks** (`selected-ultimates.xlsx`, `post-method-series.xlsx`, `post-method-triangles.xlsx`). Today script 6 still writes them as hard-coded value outputs before aggregating. Options:
   - Leave them — they stay as backward-compatible standalone value-based outputs for consumers outside this flow.
   - Delete them — the formula-driven sheets in the template supersede.
4. **Merge back to `main`** — before landing, run the full skill flow on a fresh project to confirm no regression on the actuary-facing workflow.

## Recommendation

**GO for merge.** Full Chain Ladder + key summary recalc works live. The `7-tech-review` recalc question is the main unresolved decision — handle before landing or document as a known operational step.

## Manual verification checklist

1. Open `demo/demo4-complete/poc-output/complete-analysis-poc.xlsx` in Excel.
2. Confirm 30 sheets including CL measures, Diag, Sel Ults, Ult Severity, X-to-Ult triangles, Avg IBNR, Avg Unpaid.
3. Edit a Selection LDF on any `CL - <measure>` sheet. Walk through the sheets that depend on it:
   - Same sheet: CDF row, Projected Ultimates, IBNR
   - `CL - Sel Ults - <measure>`: Chain Ladder Ult, Selected Ultimate, IBNR
   - `CL - X-to-Ult <short>`: ratio cells
   - `CL - Avg IBNR` / `CL - Avg Unpaid`: only if you edited Incurred/Paid Loss selection
   - `CL - Ult Severity`: if you edited Incurred Loss or Reported Count
4. Save. Cached values persist for downstream `data_only=True` readers.
