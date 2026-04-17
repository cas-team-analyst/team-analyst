Hey Bryce — POC on the formula-driven workbook came together within the hour, wanted to give you a quick rundown.

**TL;DR:** Template + openpyxl formula injection works. Closed Count sheet now recalcs live in Excel when the actuary edits an LDF selection; cross-sheet IBNR cascades too. 0.0 diff vs. the Python reference. One real gotcha in script 6 (cross-sheet refs break when sheets get renamed during aggregation — ~20-line fix). Recommending GO; scaling to ~50 sheets looks like 1–2 days. Branch: `poc/formula-driven-workbook`.

**Approach:** went template-based per your suggestion. Copied demo4's `Chain Ladder Selections.xlsx` into a template file, then wrote a Python/openpyxl script that injects formula strings into the Closed Count sheet (age-to-age, all 12 average variants, CDF chain, projected ultimates). Also added a second sheet with cross-sheet IBNR formulas to prove the downstream wiring.

**Result:** it works. Simulated the formula chain in Python against `projected-ultimates.parquet` — 0.0 diff across all 10 periods. Opened in Excel, edited a selected LDF, watched the CDF, projected ultimate, and cross-sheet IBNR all recalc live.

**Your warnings, confirmed:**
- openpyxl writes formulas but doesn't evaluate them — cached values are empty until Excel opens + saves the file. Handled by making "open in Excel once" an explicit step; LibreOffice headless stays in pocket as fallback.
- Python-from-scratch has failure modes, but template + formula-injection (only editing `cell.value` on an existing workbook) worked first try. I think this is different from whatever hit the wall on the prior attempts — curious what you ran into if you remember.

**One real gotcha found:** `6-create-complete-analysis.py` copies each sheet into the master workbook with a `CL - ` / `Sel - ` prefix. Same-sheet formulas survive fine. Cross-sheet refs (`='Closed Count'!E56`) do NOT get rewritten to `='CL - Closed Count'!E56`, so they break after aggregation. Fix is ~20 lines in the copy loop (regex rewrite sheet refs using the old→new name map). Haven't done it yet.

**Branch:** `poc/formula-driven-workbook` — full writeup in `demo/demo4-complete/poc-output/POC_FINDINGS.md`, scripts in `scripts/poc_inject_formulas.py` and `scripts/poc_add_selected_sheet.py`.

**Recommendation:** GO. Scaling to the full ~50 sheets looks like 1–2 days of focused work.

Happy to walk you through it whenever — also want your read on whether `7-tech-review.py` / peer-review should (a) assume the file's been opened in Excel, (b) get a LibreOffice-headless recalc step inserted, or (c) move to reading source parquets directly.
