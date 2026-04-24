
**Standard documents (project root):**
- `REPORT.md` — The primary deliverable. Structured actuarial report covering purpose, scope, data, methodology, assumptions, results by segment, diagnostics, uncertainty, open questions, and ASOP self-check. This is the document to share with reviewers or stakeholders.
- `PROGRESS.md` — Workflow checklist showing every step that was completed and the scripts produced at each step. Useful for auditing how the analysis proceeded.
- `REPLICATE.md` — Reproducibility log listing input files, scripts run, and manual edits (with reasoning). A reviewer without AI support should be able to follow this to reproduce the results.

**Data and analysis files:**
- `raw-data/` — The original input files the user supplied.
- `processed-data/` — Cleaned triangles, diagnostics, and LDF averages produced by scripts 1a–1d.
- `scripts/` — All numbered Python scripts (1a through 7) and `scripts/modules/`, exactly as run for this analysis. Re-running them against `raw-data/` should reproduce `processed-data/` and the selection workbooks.
- `selections/Chain Ladder Selections - LDFs.xlsx` — Workbook with age-to-age factors, averages, rule-based Selection row, and AI Selection row. This is the record of LDF selections and reasoning (excluding tail).
- `selections/chainladder.json` and `selections/chainladder-ai.json` — Machine-readable LDF selections (rule-based and AI-based) with per-selection reasoning.
- `selections/Chain Ladder Selections - Tail.xlsx` — Workbook with tail curve fits (Bondy, Exponential Decay, etc.), diagnostics, rule-based tail selection, and AI tail selection. This is the record of tail factor selections and reasoning.
- `selections/tail-factor.json` and `selections/tail-factor-ai.json` — Machine-readable tail factor selections (rule-based and AI-based) with per-selection reasoning and decision points.
- `selections/Ultimates.xlsx` — Workbook with method indications (Chain Ladder, Initial Expected, BF where applicable) and the selected ultimate by measure and period.
- `selections/ultimates.json` — Machine-readable ultimate selections with per-selection reasoning.
- `ultimates/` — Per-method ultimate outputs from scripts 2f, 3, and 4 (Chain Ladder, Initial Expected, Bornhuetter-Ferguson). Note any methods that were skipped and why.
- `output/complete-analysis.xlsx` — Consolidated workbook from `6-create-complete-analysis.py` containing paid-to-date, case reserves, IBNR, total unpaid, and selected ultimates by segment/period. This is the single-file view of the results.
- `output/tech-review.*` — Output from `7-tech-review.py` flagging any internal-consistency or reasonableness issues found in the analysis.