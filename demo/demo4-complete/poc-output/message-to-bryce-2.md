Hey Bryce — update on the formula-driven workbook POC.

**TL;DR:** Full pipeline is formula-driven end-to-end. All 4 measure sheets + Sel Ults summaries + Ult Severity + X-to-Ult triangles + Avg IBNR/Unpaid. Script 6 patched to rewrite sheet refs during the `CL - ` prefix rename — 2,070/2,070 cross-sheet formulas resolve in the master. 0.0 diff vs `projected-ultimates.parquet`. Branch `poc/formula-driven-workbook`.

**Still open — want your read:**
1. **Recalc policy for review scripts.** `7-tech-review.py` and peer-review read `complete-analysis.xlsx` with `data_only=True` — they need cached values that don't exist until Excel opens + saves. Options: (a) actuary opens in Excel before review, (b) LibreOffice headless recalc step, (c) migrate reviewers to read parquets directly.
2. **Exposure data** for Loss Rate / Frequency diagnostics (not in the CL workbook today).
3. **Legacy intermediate workbooks** (`selected-ultimates.xlsx` et al.) — keep as standalone value-based outputs or delete?

Full writeup: `demo/demo4-complete/poc-output/POC_FINDINGS.md`.
