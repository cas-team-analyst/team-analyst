# Interaction Mode: Pause for Selections

# Step 1: Project Setup — COMPLETE (2026-04-21)
Goal: Set up the project structure and standard documents.
- [x] Copy markdown files from assets to the project folder: PROGRESS, REPLICATE, REPORT.
- [x] Install Python packages (pandas, openpyxl, xlsxwriter, scipy, numpy, pyarrow).
- [x] Interaction mode confirmed: **Pause for Selections**
- [x] Created folders: raw-data/, processed-data/, selections/, scripts/, ultimates/, output/
- [x] Data files confirmed in raw-data/: canonical-triangles.xlsx, canonical-elrs.xlsx
- [x] Updated REPORT.md: header, Sections 1.1, 1.2, 14
- [x] Updated REPLICATE.md: Overview and Step 1

# Step 2: Exploratory Data Analysis — COMPLETE (2026-04-21)
Goal: Understand what data is available.
- [x] Reviewed canonical-triangles.xlsx (5 sheets: Incurred, Paid, Reported, Closed, Exposure — 10 AYs x 10 dev ages each) and canonical-elrs.xlsx (ELR sheet — 10 periods).
- [x] Updated REPORT.md Section 3.1 (Data Used), 3.2 (Reconciliation), 3.3 (Quality Observations), 3.4 (Limitations).

# Step 3: Data Intake — COMPLETE (2026-04-21)

- [x] Copied scripts 1a–2b and modules/ to scripts/
- [x] Triangles to use: Paid Loss and Incurred Loss for Chain Ladder; Reported/Closed counts and Exposure for diagnostics
- [x] No prior LDF selections — skipped
- [x] No prior tail factor selections — skipped
- [x] ELR file confirmed: canonical-elrs.xlsx (IE and BF will run)
- [x] Paths already correct via modules/config.py — no changes needed
- [x] 1a-prep-data.py customized: enabled ELR file, renamed ELR columns; ran and passed validation
- [x] Data format confirmed by user on 2026-04-21
- [x] LDF averages reviewed with user (vol-weighted, simple, excl-high/low × all/3yr/5yr/10yr windows; CV and slope diagnostics) — no additions requested
- [x] All scripts run: 1a, 1b, 1c, 1d — output in processed-data/
- [x] Updated REPORT.md Sections 1.2, 3.1, 3.2, 3.3, 3.4
- [x] Updated REPLICATE.md Step 2

# Step 4: Actuarial Selections: Chain Ladder LDFs — COMPLETE (2026-04-21)

- [x] Notified user about selection logic framework
- [x] Created JSON stubs: chainladder-ai-rules-based.json, chainladder-ai-open-ended.json
- [x] Rules-based selector ran: 36 selections across Incurred Loss, Paid Loss, Reported Count, Closed Count x 9 intervals
- [x] Open-ended selector ran: 36 selections independently
- [x] Ran 2b-chainladder-update-selections.py — both selection rows populated in workbook
- [x] User reviewed — no overrides. All selections from Rules-Based AI Selection row.
- [x] Updated REPORT.md Sections 4.1, 4.2, 5.1, 11
- [x] Updated REPLICATE.md Step 3

# Step 4.5: Actuarial Selections: Chain Ladder Tail Factors — COMPLETE (2026-04-21)

- [x] Notified user about tail factor selection framework
- [x] Ran 2c-tail-methods-diagnostics.py — 64 scenarios (8 methods x 2 starting ages x 4 measures); fixed label lookup bug (targeted edit)
- [x] Ran 2d-tail-create-excel.py — created selections/Chain Ladder Selections - Tail.xlsx
- [x] Created JSON stubs: tail-ai-rules-based.json, tail-ai-open-ended.json
- [x] Rules-based selector ran: 4 tail selections; fixed METHOD_ID bug in 2e (targeted edit)
- [x] Open-ended selector ran: 4 tail selections independently
- [x] Ran 2e-tail-update-selections.py — both selection rows populated in workbook
- [x] User reviewed — no overrides. All selections from Rules-Based AI Selection row.
- [x] Updated REPORT.md Section 5.1, 11
- [x] Updated REPLICATE.md Step 4

# Step 5: Run Methods That Don't Require Selections — COMPLETE (2026-04-21)

- [x] Ran 2f-chainladder-ultimates.py — CL ultimates: Incurred $544.8M, Paid $625.3M (tail 1.1787 significant driver)
- [x] Ran 3-ie-ultimates.py — IE ultimates: $525.0M (both loss measures, from ELR file)
- [x] Ran 4-bf-ultimates.py — BF ultimates: Incurred $516.7M, Paid $562.2M
- [x] Updated REPORT.md Sections 4.1, 5.2, 4.3
- [x] Updated REPLICATE.md Step 5

# Step 6: Actuarial Selections: Ultimates — IN PROGRESS (2026-04-21)

- [x] Copied 5a-ultimates-create-excel.py and 5b-ultimates-update-selections.py
- [x] Created JSON stubs: ultimates-ai-rules-based.json, ultimates-ai-open-ended.json
- [x] Ran 5a-ultimates-create-excel.py — created selections/Ultimates.xlsx
- [x] Rules-based selector ran: 40 selections (4 measures x 10 AYs)
- [x] Open-ended selector ran: 40 selections independently
- [x] Fixed key name mismatch in 5b (selected_ultimate vs selection) — targeted edit
- [x] Ran 5b-ultimates-update-selections.py — both selection columns populated
- [ ] _(Pause for Selections)_ Waiting for user to review selections/Ultimates.xlsx
- [ ] Update REPORT.md Sections 2, 5.2, 6, 11
- [ ] Update REPLICATE.md Step 6

# Step 7: Build Complete Analysis Output

- [ ] Copy `scripts/6-create-complete-analysis.py` and `scripts/7-tech-review.py` from the reserving-analysis skill scripts folder into the project `scripts/` folder (use `cp` or `mv`). Ensure `scripts/modules/` is already in place.
- [ ] Run `scripts/6-create-complete-analysis.py` and alert the user of the location and description of the final output files. 
- [ ] Run `scripts/7-tech-review.py` and alert the user of the results and where the output is saved to.
- [ ] **Update REPORT.md:**
  - Fill in **Section 7** Diagnostics and Reasonableness Checks: check off each item and note results (e.g., loss ratio progression, frequency/severity trends, actual vs. expected emergence). Populate "Anomalies to investigate" with any flags from `7-tech-review.py`.
  - Fill in **Section 0** Reviewer Quick-Start: summarize what the analysis covers (1–2 sentences), what key judgment calls were made, and where reviewer scrutiny is most needed.
  - Fill in **Section 8.2** Sources of Uncertainty: note key risk factors — process risk (thin data), parameter risk (trend/tail uncertainty), model risk (method selection), any systemic risks flagged.
  - Update **Section 14** Version History: add a row for the current version with today's date and a summary of changes since v0.1.
  - Fill any other sections to complete the first draft of the report.
- [ ] **Update REPLICATE.md Step 7:**
  - Document that `6-create-complete-analysis.py` was run
  - Note which files it read (projected-ultimates.parquet, Ultimates.xlsx)
  - List the output files created (selected-ultimates.xlsx, post-method-series.xlsx, post-method-triangles.xlsx, complete-analysis.xlsx)
  - Document that `7-tech-review.py` was run
  - List any issues flagged, or note "None - all checks passed"
  - Fill in the "Key Outputs" section listing primary deliverables
  - Add any final notes about special considerations or known issues

# Step 8: Suggest Peer Review

- [ ] Suggest to the user that they get a Peer Review of the results. If they would like TeamAnalyst to do this, they should close the current workflow (this will clear context to get an independent review) and use the /peer-review skill to get a AI Peer Review.

# Step 9: Summarize Final Outputs for the User

Be explicit and exhaustive. The user should leave this step knowing exactly what was produced, where it lives, and what each file is for. Present the list below (adapted to what actually ran in this analysis — skip items that did not run, e.g., BF if it was skipped).

- [ ] Tell the user the analysis is complete and list every output file produced, grouped by folder. For each file, give the path and a one-line description of what it contains and who it is for.

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

- [ ] After listing the files, tell the user the single most important takeaway: **REPORT.md is the primary narrative deliverable, and `output/complete-analysis.xlsx` is the primary numerical deliverable.** Everything else is supporting evidence or reproducibility material.

- [ ] Ask the user if anything is unclear about any of the outputs before the workflow closes.
