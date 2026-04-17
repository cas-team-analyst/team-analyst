Hey Bryce — quick update on the formula-driven workbook POC.

**TL;DR:** Full pipeline now formula-driven end-to-end. All 4 measure sheets, cross-sheet selected ultimates, Ult Severity, X-to-Ult ratio triangles, Avg IBNR, Avg Unpaid. Script 6 patched to rewrite sheet refs during the `CL - ` prefix rename. 2,070/2,070 cross-sheet formulas resolve in the aggregated master. Branch `poc/formula-driven-workbook`, two new commits.

**What's in:**
- 4 measure sheets with live age-to-age → averages → CDF → projected ultimate
- 4 `Sel Ults - <measure>` summary sheets with cross-sheet IBNR
- Ult Severity (Incurred Ult / Reported Ult)
- 4 X-to-Ult ratio triangles (one per measure)
- Avg IBNR and Avg Unpaid triangles
- Patched `6-create-complete-analysis.py` in the skill — regex rewriter handles quoted and unquoted sheet refs, keeps the existing copy loop intact otherwise. Same patch mirrored into demo4's copy.

**Validation:** CL ultimate values 0.0 diff vs `projected-ultimates.parquet` across all 4 measures. Full script-6 smoke test produces `complete-analysis-poc.xlsx` with all 30 sheets; zero broken refs.

**Still open — want your read:**
1. **Recalc policy for review scripts.** `7-tech-review.py` and peer-review read `complete-analysis.xlsx` with `data_only=True` — they need cached values. Options: (a) actuary opens in Excel and saves before review, (b) LibreOffice headless recalc step, (c) migrate reviewers to read parquets directly. (a) fits the current actuary workflow; (b) is the "keep it simple?" question you raised; (c) is the cleanest but biggest refactor.
2. **Exposure-dependent diagnostics** (Loss Rate, Frequency). Exposure isn't in the CL workbook — need to inject it from `1_triangles.parquet`. Trivial once we decide where it lives (hidden Exposure sheet vs. extending Ult Severity).
3. **Legacy intermediate workbooks.** Script 6 still writes `selected-ultimates.xlsx`, `post-method-series.xlsx`, `post-method-triangles.xlsx` as hard-coded value files before aggregating. Now redundant with the formula-driven sheets in the template. Delete or keep as standalone backward-compat outputs?

Full writeup in `demo/demo4-complete/poc-output/POC_FINDINGS.md`. Happy to demo anytime.
