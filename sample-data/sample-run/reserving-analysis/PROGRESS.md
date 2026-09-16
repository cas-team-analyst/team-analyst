# General Procedures

## Document Roles

- **REPORT.md** — the narrative actuarial report
- **REPLICATE.md** — an auditor replication guide. Write each entry as a prescription a human could follow to reproduce this analysis from scratch, without any AI assistance. Focus on final values, decisions, and script execution order — not on what the AI did or which selectors were invoked.

## Progress Tracking

Process to complete each step:
1. Perform each [ ] step in order. Keep the user informed as you work.
2. Mark each step complete with [X] when done.
3. Move on to the next step.

# Phase 1: Project Setup

- [X] Respond to the user with the message from `assets/welcome-message.md` and wait for confirmation.

- [X] Present the form `assets/project-setup-form.md`. Display the form exactly as written. Wait for the user to provide all the fields before proceeding. Do not skip fields or infer missing values.

- [X] Use bash cp or similar to copy PROGRESS.md, REPLICATE.md, and REPORT.md from skill assets into the project folder provided in the setup form. Do NOT read them or write them. 

- [X] If the user selected Selections Demo mode, rm REPLICATE.md and REPORT.md and remove mentions from PROGRESS.md. If the user selects Fully Automatic, remove PROGRESS.md steps that involve manual user input or review. Send PROGRESS.md, REPLICATE.md, and REPORT.md to the user as files, if they are still being used. 

- [X] Add the phases from PROGRESS.md to the task list. Include the complete phase (all [ ] steps) in each task.

- [X] Create folders `raw-data/`, `processed-data/`, `selections/`, `selections/agent-logic/`, and `scripts/` inside the project folder. The user will have selected their triangle file(s) and project folder via the file picker — use those paths to copy the triangle file(s) into `raw-data/` with bash cp. Do not ask the user to copy files manually.

- [X] Update REPORT.md: search for `AI (Phase 1):` in the template and follow the fill instructions at each match.

- [X] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

**Note:** Running as a cloud agent (no local machine access). "Project folder" refers to this session's private cloud workspace; all deliverables are sent to the user as files via SendUserFile, not written to a local machine.

# Phase 2: Exploratory Data Analysis

- [X] Review the files available using the `scripts/preview_data_file.py`.

- [X] Update REPORT.md: search for `AI (Phase 2):` in the template and follow the fill instructions at each match (Sections 3.1 Data Used, 3.2 Data Reconciliation, 3.3 Data Quality Observations).

- [X] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

**Findings:** `Triangle_Examples_1.xlsx` contains 5 sheets: "Tri 1" (metadata: WC line, low-hazard clerical risk, $100M-$500M payroll), "Paid 1" (paid loss triangle, AY2001-2024, ages 11-287mo), "Inc 1" (incurred loss triangle, same structure), "Ct 1" (claim count triangle, label ambiguous - reported vs closed unclear), "Exposure" (payroll by AY). No ELR file, no prior selections file.

# Phase 3: Data Intake

- [X] Use bash cp to copy all the numbered scripts and the modules folder from the reserving-analysis skill scripts folder to `scripts/` in the working directory. Do NOT regenerate.

- [X] Based on available data, determine which triangles we will use to come up with Ultimates estimates using the Chain Ladder method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc. **Decision: Paid Loss, Incurred Loss, and Reported Count all have complete triangles and will each get Chain Ladder LDF selections and ultimates. No Closed Count triangle is available.**

- [X] (Fully Automatic) No prior LDF selections file was provided alongside the triangle upload, so proceed without one — `read_and_process_prior_selections()` in `1a-load-and-validate.py` is left as a no-op.

- [X] (Fully Automatic) No prior tail curve selections file was provided, so skip creating `selections/agent-logic/tail-factor-prior.csv`.

- [X] (Fully Automatic) No Expected Loss Rate (period, expected loss rate, expected frequency) file was provided. Initial Expected and Bornhuetter-Ferguson will be skipped unless exposure data is present in the triangle file, in which case default to the 3-year rolling average empirical fallback used by `3-ie-ultimates.py`. Note this decision in REPORT.md Section 3.4 (Data Limitations) and Section 5.5 (Assumption Rationale). **Exposure (Payroll) data IS present, so the fallback will be used for IE/BF.**

- [X] Modify the variables at the top of each script with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH. (Defaults from `modules/config.py` were correct; added `TRIANGLE_FILE = "Triangle_Examples_1.xlsx"` to `1a-load-and-validate.py`.)

- [X] Modify `1a-load-and-validate.py` to accept the format of the data provided by the user. This includes:
  - Customizing `read_and_process_triangles()` to read triangle data from your source
  - If prior selections exist, customizing `read_and_process_prior_selections()` to read from your source.
  - Run it to verify it works and passes validation. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format.
  - **Result: `validate_combined_data()` passed. 924 rows written to `processed-data/1_triangles.csv`.**

- [X] **Confirm data format with the user.** This step always runs, regardless of interaction mode. Use the data-validation template from assets so every analysis presents data validation the same way. Do not improvise the format, reorder sections, or omit headings — even if a section is short or trivial. Populate every section from the actual processed data. The spot-check triangle should default to Paid Loss; if Paid Loss is not present, use the first loss measure available (Incurred, then Reported). Do not proceed until the user confirms. **User confirmed: "looks good" (08/30/2026).**

- [X] Report to the user what LDF averages (review `1d-ldf-averages.py`) and metrics will be calculated. **Averages: weighted, simple, exclude-high-low, each over all-years/3yr/5yr/10yr windows. QA metrics: coefficient of variation (CV) and slope trend, each over 3yr/5yr/10yr windows.**

- [X] Run all the other Python scripts to create output in `processed-data/`. (`1b-calculate-ldfs.py`, `1c-diagnostics.py`, `1d-ldf-averages.py` all ran successfully.)

- [X] Update REPORT.md: search for `AI (Phase 3):` in the template and follow the fill instructions at each match.

- [X] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

# Phase 4: Chain Ladder LDF Selections

- [X] Run `2a-chainladder-create-excel.py` to create the LDF selection workbook and export per-measure context files. The script will print the context file paths it creates (e.g., "Exported MD: selections/agent-logic/chainladder-context-paid_loss.md"). **Capture the list of context file paths** from the script output.

- [X] Before you call subagents, share the selector subagent instructions and a context file example with the user by sending them as files (not just describing them in chat) so they appear in the output tab: send the `selector-chain-ladder-ldf-ai-framework` and `selector-chain-ladder-ldf-ai-open-ended` agent files under user-readable names ("Framework-based Selector Agent" and "Open-Ended Selector Agent"), plus one of the context files captured above (call it "AI Context Example: LDF"). This is to allow the user to review this for transparency while they wait for selections to finish.

- [X] **Invoke the framework selector and the open-ended selector in parallel** (call both subagents in the same message, not one after the other). Each covers all measures in a single invocation. Both completed successfully; 6 JSON files written (3 measures x 2 selectors).

- [X] Run `2b-chainladder-update-selections.py` to collect all per-measure JSON files and insert the selections and reasoning into the Excel file.

- [X] Tell the user where `selections/Chain Ladder Selections - LDFs.xlsx` is located. Explain that both framework and open-ended AI selections (purple rows) are visible. The **Framework AI Selection** row is what gets used for ultimates — the user can override it manually. If the Framework AI Selection row is left blank, the Open-Ended AI Selection will be used as a fallback.

- [X] Update REPORT.md: search for `AI (Phase 4):` in the template and follow the fill instructions at each match. Sections 5.3, 5.4, and 4.3 are pre-filled; confirm they are correct and leave as-is.

- [X] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

**Findings:** All three measures cut off at 239 months (Framework) with 4 tail intervals remaining for curve fitting. Framework and Open-Ended selections matched closely for Reported Count; Paid Loss and Incurred Loss diverged >5% at a few early-maturity intervals (11-23, 23-35) — flagged in REPORT.md Section 11 for reviewer attention. Framework AI Selection is used for ultimates (Fully Automatic mode — no manual override).

# Phase 5: Chain Ladder Tail Curve Method Selections

- [ ] Tell the user: "I'm about to apply the tail curve selection framework. This uses curve fitting diagnostics (Bondy, Exponential Decay, McClenahan, Skurnick, etc.) and leave-one-out testing to select the best curve method for extrapolating development beyond the empirical cutoff age. The LDF agents already selected the cutoff age (where empirical selections end). The tail curve method will be used by the Chain Ladder script to generate fitted LDFs for ages after the cutoff."

- [ ] Run `2c-tail-methods-diagnostics.py` to fit tail curves and generate diagnostics. Debug any errors.

- [X] Run `2d-tail-create-excel.py` to create `selections/Chain Ladder Selections - Tail.xlsx` with curve fit results and diagnostics. If prior tail selections exist (`selections/agent-logic/tail-factor-prior.csv`), they will be included in a "Prior Selection" row for reference. The script will print the context file paths it creates (e.g., "  Exported MD: selections/agent-logic/tail-context-paid_loss.md"). **Capture the list of context file paths** from the script output. (No prior tail selections existed, as expected.)

- [X] Before you call subagents, share the selector subagent instructions and a context file example with the user by sending them as files (not just describing them in chat) so they appear in the output tab: send the `selector-tail-curve-ai-framework` and `selector-tail-curve-ai-open-ended` agent files under user-readable names ("Framework-based Selector Agent" and "Open-Ended Selector Agent"), plus one of the context files captured above (call it "AI Context Example: Tail"). This is to allow the user to review this for transparency while they wait for selections to finish.

- [X] **Invoke the framework tail selector and the open-ended tail selector in parallel** (call both subagents in the same message, not one after the other). Each covers all measures in a single invocation. Both completed successfully; 6 JSON files written (3 measures x 2 selectors).

- [X] Run `2e-tail-update-selections.py` to collect all per-measure JSON files and insert the selections into the Excel file.

- [X] Tell the user where `selections/Chain Ladder Selections - Tail.xlsx` is located. Explain that both framework and open-ended AI selections (purple rows) are visible. The **Framework AI Selection** row shows the selected curve METHOD (e.g., 'bondy', 'exp_dev_quick') — this is what gets used to generate fitted LDFs in the Chain Ladder script. The user can override it manually. If the Framework AI Selection row is left blank, the Open-Ended AI Selection will be used as a fallback.

- [X] Update REPORT.md: search for `AI (Phase 5):` in the template and follow the fill instructions at each match.

- [X] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

**Findings:** Framework AI selections (used for ultimates): Paid Loss = bondy (1.0060), Incurred Loss = mcclenahan (≈1.0000), Reported Count = exp_dev_quick (≈1.0000, R²=1.000). Exponential-decay forms were hard-rejected for Paid and Incurred Loss under the Gap Rule (gap_flag=True). Open-Ended selected bondy for all three measures, diverging from Framework's mcclenahan choice for Incurred Loss (1.017 vs ≈1.000) — flagged in REPORT.md Section 11.

# Phase 6: Calculate Method Projections

- [ ] Run `2f-chainladder-ultimates.py`, `3-ie-ultimates.py`, and `4-bf-ultimates.py`. Debug any errors that occur. It is normal for IE and BF to get skipped if the user didn't provide the necessary data (exposure, initial expected). Note: `2f-chainladder-ultimates.py` will:
  1. Read empirical LDF selections from `selections/Chain Ladder Selections - LDFs.xlsx` (up to the cutoff age)
  2. Read the selected tail curve METHOD from `selections/Chain Ladder Selections - Tail.xlsx` (priority: User Selection → Framework AI → Open-Ended AI)
  3. Load curve parameters from `processed-data/tail-scenarios.parquet`
  4. Generate fitted LDFs for ages beyond the cutoff using the selected curve method's formula
  5. Build complete CDFs by chaining empirical + fitted LDFs
  6. Calculate Chain Ladder ultimates and save to `processed-data/projected-ultimates.csv`

- [X] Update REPORT.md: search for `AI (Phase 6)` in the template and follow the fill instructions at each match.

- [X] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

**Findings:** All three methods ran successfully (IE/BF were NOT skipped — exposure data was present and the ELR fallback was used). Summary of ultimate totals by method:
- **Chain Ladder:** Paid Loss $52.82M (IBNR $11.05M) | Incurred Loss $51.73M (IBNR $8.11M) | Reported Count 9,737 (IBNR 21)
- **Initial Expected:** Paid/Incurred Loss $46.00M | Reported/Closed Count 10,325
- **Bornhuetter-Ferguson:** Paid Loss $48.57M (IBNR $6.80M) | Incurred Loss $48.81M (IBNR $5.20M) | Reported Count 9,738 (IBNR 22)

# Phase 7: Ultimate Selections

- [X] Run `scripts/5a-ultimates-create-excel.py` to create the ultimates workbook and export category context files. The script will create two sheets: **Losses** (combining Incurred and Paid) and **Counts** (combining Reported and Closed). It will print the context file paths it creates (e.g., "  Exported MD: selections/agent-logic/ultimates-context-loss.md", "  Exported MD: selections/agent-logic/ultimates-context-count.md"). **Capture the list of context file paths** from the script output.

- [X] Before you call subagents, share the selector subagent instructions and a context file example with the user by sending them as files (not just describing them in chat) so they appear in the output tab: send the `selector-ultimates-ai-framework` and `selector-ultimates-ai-open-ended` agent files under user-readable names ("Framework-based Selector Agent" and "Open-Ended Selector Agent"), plus one of the context files captured above (call it "AI Context Example: Ultimates"). This is to allow the user to review this for transparency while they wait for selections to finish.

- [X] **Invoke the framework ultimates selector and the open-ended ultimates selector in parallel** (call both subagents in the same message, not one after the other). Each covers both categories in a single invocation. Both completed successfully; 4 JSON files written (2 categories x 2 selectors, 24 accident years each).

- [X] Run `5b-ultimates-update-selections.py` to load the category JSON files and insert both framework and open-ended selections and reasoning into `selections/Ultimates.xlsx`.

- [X] Tell the user where `selections/Ultimates.xlsx` is located. Explain that both framework and open-ended AI selections are visible. The framework selection is what gets used by default — the user can override it manually. The open-ended selection provides an independent cross-check. Note that the workbook now has **Losses** and **Counts** sheets instead of per-measure sheets, and one ultimate is selected per category per accident year.

- [X] Run `scripts/5c-summary-indications.py` to compute headline indications from the selected ultimates. This script reads `selections/Ultimates.xlsx` and outputs a formatted markdown table with total unpaid reserve, case reserves, and IBNR.

- [X] **Update PROGRESS.md with headline indications:** Copy the markdown table output from `5c-summary-indications.py` into a "Headline Indications" section in PROGRESS.md. (See below.)

- [X] Send updated PROGRESS.md to the user.

- [X] Update REPORT.md: search for `AI (Phase 7):` in the template and follow the fill instructions at each match.

- [X] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

## Headline Indications

| Metric | Loss | Count |
|---|---|---|
| Paid / Reported to Date | $41,767,854 | 9,716 |
| Case Reserves | $1,848,541 | — |
| IBNR | $5,558,363 | 23 |
| **Total Unpaid** | **$7,406,904** | **23** |
| **Selected Ultimate** | **$49,174,758** | **~9,739** |

**Findings:** Framework AI selected ultimates blending Chain Ladder, Initial Expected, and Bornhuetter-Ferguson per the WC-shifted maturity schedule (long-tail line — BF credible longer, CL arrives later). Two accident years (2012, 2020) were flagged by the Framework selector for wide CL dispersion / anomalous case reserve pattern — carried into REPORT.md Section 11 as open questions. Open-Ended selector broadly discounted Initial Expected throughout (viewed it as consistently diverging from realized experience) and leaned more heavily on Chain Ladder/BF — a second opinion the reviewer can compare against.

# Phase 8: Build Analysis Workbook

- [X] Run `scripts/6-analysis-create-excel.py` and alert the user of the location and description of the final output files. Produced `Analysis.xlsx` (15 sheets) in the project root.

- [X] Update REPORT.md: search for `AI (Phase 8):` in the template and follow the fill instructions at each match. Then do a final completeness pass: confirm pre-filled sections (LAE, trending, sensitivity) still say "Not implemented" or "Not applicable" and no bracketed placeholders remain. Verified Section 2 totals match `Analysis.xlsx` exactly. Cleaned up two leftover template rows in Section 2. LAE/trending/sensitivity sections confirmed still correctly say "Not applicable"/"Not implemented".

- [X] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

# Phase 9: Technical Review

- [X] Run `scripts/7-tech-review.py` and alert the user of the results and where the output is saved to. **Result: 94 checks run — 64 PASS, 30 WARN, 0 FAIL. Saved to `Tech Review.xlsx`.**

- [X] Update REPORT.md: search for `AI (Phase 9):` in the template and follow the fill instructions at each match.

- [X] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

**Findings:** No FAIL results. All 30 WARNs trace back to already-documented, non-material causes: early-maturity WC link ratios naturally exceeding a generic ceiling check, minor negative development documented in Phase 2/3, and the AY2012/AY2020 judgment calls documented in Phase 7/REPORT.md Section 11. No data or calculation fixes were required.

# Phase 10: Summarize Final Outputs

Be explicit and exhaustive. The user should leave this step knowing exactly what was produced, where it lives, and what each file is for. Present the list below (adapted to what actually ran in this analysis — skip items that did not run, e.g., BF if it was skipped).

- [X] After listing the files, tell the user the single most important takeaway: **REPORT.md is the primary narrative deliverable, and `Analysis.xlsx` is the primary numerical deliverable.** Everything else is supporting evidence or reproducibility material.

- [X] Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait, as well as a .zip with all the project files.

- [X] Provide the user a closing summary following the template at `assets/closing-summary.md`.

- [X] Let the user know: If they'd like to continue with Peer Review, they should start a New Chat, upload the zip, and run `/peer-review` for an independent AI peer review of the completed analysis. Or, they can ask questions about the analysis or the workflow.

**ANALYSIS COMPLETE.** All 10 phases finished in Fully Automatic mode. Final headline indication: Selected Ultimate Loss $49,174,758 (IBNR $5,558,363); Selected Ultimate Count ~9,739 (IBNR 23). Technical review: 94 checks, 64 PASS, 30 WARN, 0 FAIL.

---
