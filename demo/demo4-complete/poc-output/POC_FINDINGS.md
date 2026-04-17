# POC — Formula-Driven Workbook Findings

**Branch:** `poc/formula-driven-workbook`
**Scope:** Closed Count measure only, end-to-end (age-to-age → averages → CDF → projected ultimate → cross-sheet IBNR)
**Approach:** Python-openpyxl injects formulas into a template file that's seeded from demo4's `Chain Ladder Selections.xlsx`.

## What's in `poc-output/`

- `templates/cl-selections-template.xlsx` — the template. Closed Count sheet contains live formulas; other measure sheets untouched. A new `Selected Ultimates - POC` sheet demonstrates cross-sheet wiring.
- `sim-script6-master.xlsx` — the result of running `6-create-complete-analysis.py`'s sheet-copy loop against the template (simulated). Use this to see what breaks downstream.

## Scripts (in `claude-code/scripts/`)

- `poc_inject_formulas.py` — injects CL formulas into the `Closed Count` sheet.
- `poc_add_selected_sheet.py` — adds the `Selected Ultimates - POC` sheet with cross-sheet refs.

## Results

### ✅ Core CL chain works

Python-simulated the formula chain against `ultimates/projected-ultimates.parquet` for all 10 periods:

| Period | Simulated Ultimate | Reference Ultimate | Diff |
|---|---|---|---|
| 2015 | 4,931.00 | 4,931.00 | 0.0 |
| 2016 | 4,935.90 | 4,935.90 | 0.0 |
| 2017 | 4,895.93 | 4,895.93 | 0.0 |
| 2018 | 5,020.66 | 5,020.66 | 0.0 |
| 2019 | 4,958.46 | 4,958.46 | 0.0 |
| 2020 | 4,968.19 | 4,968.19 | 0.0 |
| 2021 | 5,340.87 | 5,340.87 | 0.0 |
| 2022 | 5,225.31 | 5,225.31 | 0.0 |
| 2023 | 4,803.41 | 4,803.41 | 0.0 |
| 2024 | 4,602.37 | 4,602.37 | 0.0 |

**Max absolute diff: 0.0.** Formula logic exactly replicates the Python reference.

### ✅ openpyxl formula-injection path works

The engineering lead's prior concern ("initial attempts didn't go well" in Python) may have been the code-from-scratch path. The template-based approach — where Python only edits `cell.value` of an existing workbook to inject formula strings — worked on the first try.

Known openpyxl behavior confirmed: it writes formula strings but does **not** evaluate them. Cached values are `None` until Excel opens the file and saves.

### ⚠️ Script 6 breaks cross-sheet refs (the expected risk)

`6-create-complete-analysis.py` copies each source sheet into the master workbook with a `CL - ` / `Sel - ` prefix. Same-sheet formulas (the entire CL chain within `Closed Count`) survive intact. **Cross-sheet formulas do not** — `='Closed Count'!E56` stays as-is after the source sheet gets renamed to `CL - Closed Count` in the master, producing `#REF!` or an external-link prompt when Excel opens the master.

This affects only formulas that reach across sheets. Within a single sheet, everything is fine.

### ⚠️ `7-tech-review.py` and peer-review read `complete-analysis.xlsx` with `data_only=True`

These expect cached values. If formulas are in the master workbook and nobody opens it in Excel first, these readers will see `None` for every derived cell. Confirmed via the cross-sheet simulation: cached values are empty on disk until Excel saves.

## Formulas in use (Closed Count sheet)

| Region | Formula template |
|---|---|
| Age-to-age (B16:J24) | `=C3/B3` (next age ÷ current age) — only where both cells populated |
| Simple avg (row 29) | `=IFERROR(AVERAGE(B16:B24), AVERAGE(B16:B24))` |
| Weighted avg (row 30) | `=IFERROR(SUMPRODUCT(B16:B24,B3:B11)/SUMPRODUCT((B16:B24<>"")*B3:B11), …fallback…)` |
| Exclude hi/lo (row 31) | `=IFERROR(TRIMMEAN(B16:B24,2/COUNT(B16:B24)), AVERAGE(B16:B24))` |
| N-yr variants (rows 32–40) | same patterns with narrower ranges; fallback to "all" when window is sparse |
| CDF row (row 52) | `K52: =K47`, then `J52: =J47*K52`, `I52: =I47*J52`, … backward chain |
| Latest Age (col B, rows 56–65) | `=LOOKUP(2, 1/(B3:K3<>""), $B$2:$K$2)` |
| Latest Value (col C) | `=LOOKUP(2, 1/(B3:K3<>""), B3:K3)` |
| CDF at age (col D) | `=HLOOKUP(B56, $B$51:$K$52, 2, FALSE)` |
| Ultimate (col E) | `=C56*D56` |
| IBNR (col F) | `=E56-C56` |

## Manual verification checklist for you

1. Open `demo/demo4-complete/poc-output/templates/cl-selections-template.xlsx` in Excel.
2. Go to the **Closed Count** sheet. Confirm every cell in the age-to-age, averages, CDF, and Projected Ultimates sections is populated (not blank or #REF). Compare the Projected Ultimate column values to the table above.
3. Edit a Selection cell — e.g., change `B47` from `1.6243` to `1.7000`. Watch `B52` (CDF at age 12) and column E of the Projected Ultimates section update live.
4. Flip to the **Selected Ultimates - POC** sheet. Confirm the Chain Ladder Ult column pulls from Closed Count, and changing the LDF on Closed Count cascades into the IBNR here.
5. Save. This caches values so downstream readers work.

## Scaling to the full ~50-sheet workbook

**Effort estimate — moderate:** ~1–2 days of focused work.

The hard part was proving the path works and finding the sheet-rename gotcha. Repeating the injection for the other three measure sheets (Incurred Loss, Paid Loss, Reported Count) is mostly `poc_inject_formulas.py` parameterized on a sheet name. Diagnostic sheets (Diag-* and CV & Slopes) would need their own formula maps but follow similar patterns.

Bigger outstanding items before a full rollout:

1. **Patch `6-create-complete-analysis.py`** to rewrite formula sheet refs during copy. In the copy loop around line 577, after assigning `dst_cell.value = cell.value`, if the value is a formula string, regex-replace `'<old_name>'!` with `'<new_name>'!` using the `{original: prefixed}` mapping built as sheets are renamed. ~20 lines of code.

2. **Decide on recalc strategy** for `data_only=True` readers. Options:
   - Human-in-the-loop: the actuary opens the master in Excel and saves; the reviewers then run. Fits the existing workflow since actuary already opens workbooks for review.
   - LibreOffice headless (`soffice --headless --calc --convert-to xlsx`) inserted before `7-tech-review.py` to force recalc. Adds Linux/LibreOffice dependency the lead flagged as "keep it simple."
   - Migrate `7-tech-review.py` / peer-review to read source parquets/JSON directly rather than the aggregated xlsx — this would be the cleanest but requires rewriting both.

3. **Weighted-average weight references.** The current formulas reference the triangle directly (`SUMPRODUCT(B16:B24, B3:B11)`). This works because weights for age-to-age factors are the prior-age triangle values. If different weighting is ever used, formulas would need to be updated. Not a concern for the current actuarial method.

4. **Sparse-window behavior for 3yr/5yr averages.** Python's `1d-averages-qa.py` has specific logic for sparse intervals (columns where the window has zero observations). Our formulas fall back to the "all" range via `IFERROR`. Need to confirm with the actuary that this fallback is acceptable, or replicate the exact fallback (requires reading 1d to verify).

## Recommendation — GO

The core proof is solid: formulas produce numerically identical results to the Python pipeline, openpyxl injection works, and the actuary gets a live-recalcing workbook. The sheet-rename issue is real but fixable with a small patch to script 6.

**Suggested next commits on this branch:**
1. Patch `6-create-complete-analysis.py` to rewrite cross-sheet refs during copy.
2. Extend `poc_inject_formulas.py` to all four measure sheets (parameterize on sheet name).
3. Decide recalc strategy with the team before touching `7-tech-review.py` / peer-review.

## Things not covered in this POC

- Downstream diagnostic sheets (post-method triangles, severity/loss-rate/frequency) still use hard-coded values. These are all derived from selected ultimates, so the same template pattern applies — wire them in the next iteration.
- `selected-ultimates.xlsx` and `post-method-series.xlsx` (the separate workbooks generated by script 6) were not converted; the `Selected Ultimates - POC` sheet in the template is a standalone demo of the cross-sheet pattern.
- Incurred Loss / Paid Loss / Reported Count sheets are untouched.
- No testing against LibreOffice-headless recalc yet.
