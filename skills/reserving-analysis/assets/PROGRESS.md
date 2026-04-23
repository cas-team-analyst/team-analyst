# Step 1: Project Setup
Goal: Set up the project structure and standard documents.
- [ ] Copy markdown files from assets to the project folder: PROGRESS, REPLICATE, REPORT. IMPORTANT: Use `cp` or `mv`, DO NOT REGENERATE THE FILES. Find a way to get copy to work. If you are working in a sandbox or the skill source isn't accessible from bash, mount the skill folder.
- [ ] Ask the user the level of interaction they would like:
  - **Pause for Selections** — Runs automatically, but pauses after LDF selections and again after ultimate selections so you can explore and override them before the analysis continues.
  - **Fully Automatic** — Runs start to finish without stopping for input (except to confirm data format). Selections are made automatically.
  Use these exact option names. Do not recommend one. Note the user's choice at the top of PROGRESS.md.
- [ ] Create folders `raw-data/`, `processed-data/`, `selections/`, `scripts/`, and `ultimates/` in the project folder and ask the user to copy relevant data files into the raw-data folder.
- [ ] **Update REPORT.md:**
  - Fill in the header fields: Analysis name, Valuation Date (if known), Prepared by (user name), Draft Date (today).
  - Fill in **Section 1.1** with the purpose of this analysis (e.g., "quarterly reserve review") and **Section 1.2** Scope table with any known segment/LOB/coverage/basis info.
  - Add a row to **Section 14** Version History: v0.1, today's date, analyst, "Initial draft".
- [ ] **Update REPLICATE.md:**
  - Fill in the Overview section: Analysis name, Valuation Date, Prepared by, Date
  - Fill in Step 1: List folders created, note interaction mode selected

# Step 2: Exploratory Data Analysis
Goal: Understand what data is available.
- [ ] Review the files available using the explore-excel in the reserving-analysis skill scripts. For each file add a file summary subsection to REPORT.md in the data section.
- [ ] **Update REPORT.md:**
  - Fill in **Section 3.1** Data Used table: one row per file (source name, as-of date, any notes on format or coverage).
  - Fill in **Section 3.2** Data Reconciliation: note whether data was reconciled to a prior valuation or financial system and the result.
  - Fill in **Section 3.3** Data Quality Observations: any outliers, gaps, negative development, coding anomalies, or unusual patterns noticed during exploration.

# Step 3: Data Intake

- [ ] Copy all the numbered scripts and the modules folder from the reserving-analysis skill scripts folder to `scripts/` in the working directory. IMPORTANT: Use `cp` or `mv`, DO NOT REGENERATE THE FILES. Find a way to get copy to work. If you are working in a sandbox or the skill source isn't accessible from bash, mount the skill folder.
- [ ] Based on available data, determine which triangles we will use to come up with Ultimates estimates using the Chain Ladder method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc.
- [ ] If you haven't already found prior selections, ask the user if prior LDF selections exist from a previous analysis. If they do, ask where they are located (Excel file, CSV, database, etc.). You will need to modify `read_and_process_prior_selections()` in `1a-prep-data.py` to read from that source during data extraction.
- [ ] Ask the user if prior tail factor selections exist from a previous analysis. If they do, ask where they are located and what tail factor was used for each measure. Create a CSV file at `selections/tail-factor-prior.csv` with columns: `measure`, `cutoff_age`, `tail_factor`, `method`, `reasoning`. This will be loaded by `2d-tail-create-excel.py` and shown in the "Prior Selection" row for reference. If no prior tail selections exist, skip this step.
- [ ] If you haven't already found an input file with Expected Loss Rates (containing period, expected loss rate, and expected frequency), ask the user if this file exists and to place it in the raw-data folder. Without this file, we won't be able to use the Initial Expected or Bornhuetter-Ferguson methods.
- [ ] If initial expected data is not provided (no expected loss rate/frequency file) but exposure is available, confirm with the user whether to use the fallback approximation for BF expected rate: for each accident year, compute diagonal loss per dollar of exposure, smooth with a 3-year rolling average, and round to 3 decimals. Offer these options explicitly before continuing: (1) use this fallback (this is what `3-ie-ultimates.py` defaults to), (2) use a different approach the user specifies, (3) upload initial expected data in the required format, or (4) skip Initial Expected/BF and continue with Chain Ladder only. Note their response REPORT.md.
- [ ] Modify the variables at the top of each script with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH.
- [ ] Modify `1a-prep-data.py` to accept the format of the data provided by the user. This includes:
  - Customizing `read_and_process_triangles()` to read triangle data from your source
  - If prior selections exist, customizing `read_and_process_prior_selections()` to read from your source.
  - Run it to verify it works and passes validation. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format.
- [ ] **Confirm data format with the user.** This step always runs, regardless of interaction mode. Use the exact template below so every analysis presents data validation the same way. Do not improvise the format, reorder sections, or omit headings — even if a section is short or trivial.

````
## Data Validation — Please Review

I've processed your raw data into the canonical triangle format. Please
confirm the summary below looks correct before I continue.

### 1. Measures Loaded

| Measure | # Records | AY Range | Dev Ages (months) | Min Value | Max Value |
|---|---|---|---|---|---|
| [measure 1] | [n] | [YYYY–YYYY] | [min–max] | [min] | [max] |
| ... | | | | | |

**Total records:** [N] across [K] measures.

### 2. Sample Rows

First 3 and last 3 rows of the processed triangle table (all measures combined):

| measure | accident_year | dev_age | value |
|---|---|---|---|
| ... | ... | ... | ... |

### 3. Spot-Check: One Full Triangle

Showing [Paid Loss] (cumulative) as a sanity check on shape and magnitude:

| AY \ Dev | 12 | 24 | 36 | ... | [ultimate age] |
|---|---|---|---|---|---|
| 2015 | ... | ... | ... | ... | ... |
| 2016 | ... | ... | ... | ... | |
| ... | | | | | |

### 4. Adjustments Made to `1a-prep-data.py`

- [Bullet each customization — column renames, source-specific parsing, outlier handling, etc.]
- If no changes were made, say: "No adjustments required — data matched the expected format."

### 5. Confirmation Needed

Please reply with one of:
- **"Looks good"** — I'll continue to LDF averages and diagnostics.
- **"Fix <issue>"** — describe what's wrong and I'll address it before moving on.
````

Populate every section from the actual processed data. The spot-check triangle should default to Paid Loss; if Paid Loss is not present, use the first loss measure available (Incurred, then Reported). Do not proceed until the user confirms.
- [ ] Report to the user what LDF averages (review `1d-averages-qa.py`) and metrics will be calculated. _(Pause for Selections only: also ask if they'd like to add others before continuing.)_
- [ ] Run all the other Python scripts to create output in `processed-data/`.
- [ ] **Update REPORT.md:**
  - Update **Section 3.1** Data Used table: add rows for triangle types used (paid, incurred, counts), confirm source file names and as-of dates; note if ELR file is present or absent.
  - Update **Section 3.3** Data Quality Observations: note any adjustments made to `1a-prep-data.py` (e.g., outlier exclusions, coding changes), any data limitations discovered.
  - Update **Section 3.4** Data Limitations: note missing data types (e.g., no ELR file → IE/BF skipped) and how limitations were handled.
  - Update **Section 1.2** Scope table: fill in accident/underwriting years, coverages, and basis once confirmed from the data.
- [ ] **Update REPLICATE.md Step 2:**
  - List all input files in raw-data/ with brief descriptions
  - Document which scripts were run (1a through 1d)
  - List any customizations made to `1a-prep-data.py` (column mappings, data transformations, outlier handling)
  - Note the output files created in `processed-data/`
  - Record the data validation confirmation date

# Step 4: Actuarial Selections: Chain Ladder LDFs

- [ ] Tell the user: "I'm about to apply the base selection logic framework to make LDF selections. This framework includes 14 selection criteria and 10 diagnostic adjustment rules. If you'd like to explore these in detail, you can use `/selection-logic` in a separate session or after this analysis is complete — using it here would interrupt the current workflow."
- [ ] Create JSON files to hold selections: `selections/chainladder-ai-rules-based.json` and `selections/chainladder-ai-open-ended.json` with just "[]" for now.
- [ ] Compress your context to make space for the upcoming subagent responses.
- [ ] For each measure, task a  `selector-chain-ladder-ldf-ai-rules-based.agent.md` subagent (located in `skills/reserving-analysis/agents/`) to: Review the per-measure context markdown exported by `2a-chainladder-create-excel.py` at `selections/chainladder-context-<measure>.md` (NOT the files at `processed-data`, and do NOT use Excel as the primary source because formulas may be unevaluated), use this information to make actuarial LDF selections for each combination of Chain Ladder measure and interval, and write the selections to `selections/chainladder-ai-rules-based.json`. Remove any temporary files created during the selection process.
- [ ] For each measure, task a  `selector-chain-ladder-ldf-ai-open-ended.agent.md` subagent (located in `skills/reserving-analysis/agents/`) to: Review the per-measure context markdown exported by `2a-chainladder-create-excel.py` at `selections/chainladder-context-<measure>.md` (do NOT use Excel as the primary source because formulas may be unevaluated), independently make LDF selections for each combination of measure and interval using its own actuarial judgment (no rigid rules framework), and write the selections to `selections/chainladder-ai-open-ended.json`. Remove any temporary files created during the selection process.
- [ ] Run `2b-chainladder-update-selections.py` to insert the selections and reasoning into the Excel file. This will populate both the **Rules-Based Selection** row (from `chainladder-ai-rules-based.json`) and the **Open-Ended AI Selection** row (from `chainladder-ai-open-ended.json`, if present) in each sheet.
- [ ] Tell the user where `selections/Chain Ladder Selections - LDFs.xlsx` is located. Explain that both rules-based and open-ended AI selections (purple rows) are visible. The **Rules-Based Selection** row is what gets used for ultimates — the user can override it manually. If the Rules-Based Selection row is left blank, the Open-Ended AI Selection will be used as a fallback.

_(Pause for Selections only):_
- [ ] Open `selections/Chain Ladder Selections - LDFs.xlsx` for the user. Let them know they can review and override any AI selections. Pause and wait for the user to confirm they are done reviewing before continuing.

- [ ] **Update REPORT.md:**
  - Fill in **Section 4.1** Methods Applied: add "Paid LDF" and/or "Reported LDF" rows for each triangle measure used; note "Selected via rule-based framework + AI cross-check."
  - Fill in **Section 4.2** Method Weighting / Selection Logic: briefly describe the 14-criteria rule-based framework and that AI selections were used as a cross-check. Note maturity-based weighting approach.
  - Fill in **Section 5.1** Development Patterns: note the selection basis (volume-weighted averages, which average windows were considered).
  - Add to **Section 11** Open Questions any selections flagged as low-confidence or where the rule-based and AI selections diverged materially.
- [ ] **Update REPLICATE.md Step 3:**
  - Document that `2a-chainladder-create-excel.py` was run to create the selection workbook
  - Note that AI selectors made rules-based and open-ended selections (JSON files created)
  - Document that `2b-chainladder-update-selections.py` populated the Excel file with AI selections
  - **Critical:** If user made manual overrides in the "User Selection" row, list each one with measure, interval, selected LDF, and reasoning. If no overrides, explicitly state "All selections are from Rules-Based AI Selection row."
  - Add instruction: "To replicate: Extract final selections from User Selection row if present, otherwise use Rules-Based AI Selection row. Do not re-run AI selector."

# Step 4.5: Actuarial Selections: Chain Ladder Tail Factors

- [ ] Tell the user: "I'm about to apply the tail factor selection framework. This uses curve fitting diagnostics (Bondy, Exponential Decay, McClenahan, Skurnick, etc.), leave-one-out testing, and a 15-point decision framework to select tail factors. Tail selections are separate from LDF selections and are used in the Chain Ladder ultimates calculation."
- [ ] Run `2c-tail-methods-diagnostics.py` to fit tail curves and generate diagnostics. Debug any errors.
- [ ] Run `2d-tail-create-excel.py` to create `selections/Chain Ladder Selections - Tail.xlsx` with curve fit results and diagnostics. If prior tail selections exist (`selections/tail-factor-prior.csv`), they will be included in a "Prior Selection" row for reference.
- [ ] Create JSON files to hold selections: `selections/tail-ai-rules-based.json` and `selections/tail-ai-open-ended.json` with just "[]" for now.
- [ ] Compress your context to make space for the upcoming subagent responses.
- [ ] For each measure, task a `selector-tail-factor-ai-rules-based.agent.md` subagent (located in `skills/reserving-analysis/agents/`) to: Review the per-measure context markdown exported by `2d-tail-create-excel.py` at `selections/tail-context-<measure>.md` (NOT the files at `processed-data`, and do NOT use Excel as the primary source because formulas may be unevaluated), including prior tail factor selections if present, use this information to make actuarial tail factor selections for each measure using the 15-point tail factor decision framework, and write the selections to `selections/tail-ai-rules-based.json`. Remove any temporary files created during the selection process.
- [ ] For each measure, task a `selector-tail-factor-ai-open-ended.agent.md` subagent (located in `skills/reserving-analysis/agents/`) to: Review the per-measure context markdown exported by `2d-tail-create-excel.py` at `selections/tail-context-<measure>.md` (do NOT use Excel as the primary source because formulas may be unevaluated), including prior selections if present, independently make tail factor selections for each measure using holistic actuarial judgment (no rigid rules framework), and write the selections to `selections/tail-ai-open-ended.json`. Remove any temporary files created during the selection process.
- [ ] Run `2e-tail-update-selections.py` to insert the selections into the Excel file. This will populate both the **Rules-Based Selection** row (from `tail-ai-rules-based.json`) and the **Open-Ended AI Selection** row (from `tail-ai-open-ended.json`, if present) in each sheet.
- [ ] Tell the user where `selections/Chain Ladder Selections - Tail.xlsx` is located. Explain that both rules-based and open-ended AI selections (purple rows) are visible. The **Rules-Based Selection** row is what gets used for ultimates — the user can override it manually. If the Rules-Based Selection row is left blank, the Open-Ended AI Selection will be used as a fallback.

_(Pause for Selections only):_
- [ ] Open `selections/Chain Ladder Selections - Tail.xlsx` for the user. Let them know they can review and override any tail factor selections. Pause and wait for the user to confirm they are done reviewing before continuing.

- [ ] **Update REPORT.md:**
  - Update **Section 5.1** Development Patterns: add tail factor source (curve fit method selected, R² values, leave-one-out diagnostics).
  - Add to **Section 11** Open Questions any tail selections flagged as low-confidence or where curve fit diagnostics were poor or rule-based and AI selections diverged materially.
- [ ] **Update REPLICATE.md Step 4:**
  - Document that `2c-tail-methods-diagnostics.py` was run to fit curves and create diagnostics
  - Document that `2d-tail-create-excel.py` created the tail selection workbook
  - Note that AI selectors made rules-based and open-ended tail selections (JSON files created)
  - Document that `2e-tail-update-selections.py` populated the Excel file with AI selections
  - **Critical:** If user made manual overrides in the "User Selection" row, list each one with measure, cutoff age, tail factor, method, and reasoning. If no overrides, explicitly state "All selections are from Rules-Based AI Selection row."
  - Add instruction: "To replicate: Extract final tail factors from User Selection row if present, otherwise use Rules-Based AI Selection row. Do not re-run AI selector."

# Step 5: Run Methods That Don't Require Selections

- [ ] Run `2f-chainladder-ultimates.py`, `3-ie-ultimates.py`, and `4-bf-ultimates.py`. Debug any errors that occur. It is normal for IE and BF to get skipped if the user didn't provide the necessary data (exposure, initial expected). Note: `2f-chainladder-ultimates.py` will use tail factors from `selections/Chain Ladder Selections - Tail.xlsx` (priority 1 — user's final selection), falling back to `selections/tail-ai-rules-based.json` (priority 2), then `selections/tail-ai-open-ended.json` (priority 3) if Excel is empty.
- [ ] **Update REPORT.md:**
  - Update **Section 4.1** Methods Applied: confirm which methods actually ran vs. were skipped, and why (e.g., "BF skipped — no ELR file provided").
  - Update **Section 5.2** Expected Loss Ratios: if IE/BF ran, fill in the ELR table from the input file.
  - Update **Section 4.3** LAE Treatment: fill in how DCC/ALAE and A&O/ULAE are handled, if applicable.
- [ ] **Update REPLICATE.md Step 5:**
  - Document that `2f-chainladder-ultimates.py` was run (note which Excel file it read LDFs and tail factors from)
  - Document whether `3-ie-ultimates.py` ran or was skipped (and why)
  - Document whether `4-bf-ultimates.py` ran or was skipped (and why)
  - Note the output file: `ultimates/projected-ultimates.parquet` with columns added by each method

# Step 6: Actuarial Selections: Ultimates

- [ ] Copy `scripts/5a-ultimates-create-excel.py` and `scripts/5b-ultimates-update-selections.py` from the reserving-analysis skill scripts folder into the project `scripts/` folder (use `cp` or `mv`, don't rewrite them yourself). Ensure `scripts/modules/` is already in place (copied in Step 3).
- [ ] Create JSON files to hold selections: `selections/ultimates-ai-rules-based.json` and `selections/ultimates-ai-open-ended.json` with just "[]" for now.
- [ ] For each measure, task a `selector-ultimates-ai-rules-based.agent.md` subagent (located in `skills/reserving-analysis/agents/`) to: Review the per-measure context markdown exported by `5a-ultimates-create-excel.py` at `selections/ultimates-context-<measure>.md` (NOT the files at `processed-data`, and do NOT use Excel as the primary source because formulas may be unevaluated), use this information to make actuarial ultimate selections for each combination of Chain Ladder measure and period using the structured method weighting framework, and write the selections to `selections/ultimates-ai-rules-based.json`. Remove any temporary files created during the selection process.
- [ ] For each measure, task a `selector-ultimates-ai-open-ended.agent.md` subagent (located in `skills/reserving-analysis/agents/`) to: Review the per-measure context markdown exported by `5a-ultimates-create-excel.py` at `selections/ultimates-context-<measure>.md` (do NOT use Excel as the primary source because formulas may be unevaluated), independently make ultimate selections for each combination of measure and period using holistic actuarial judgment (no rigid rules framework), and write the selections to `selections/ultimates-ai-open-ended.json`. Remove any temporary files created during the selection process.
- [ ] Run `5b-ultimates-update-selections.py` to insert both rules-based and open-ended selections and reasoning into `selections/Ultimates.xlsx`.
- [ ] Tell the user where `selections/Ultimates.xlsx` is located. Explain that both rules-based and open-ended AI selections are visible. The rules-based selection is what gets used by default — the user can override it manually. The open-ended selection provides an independent cross-check.

_(Pause for Selections only):_
- [ ] Open `selections/Ultimates.xlsx` for the user. Let them know they can review and override any AI ultimate selections. Pause and wait for the user to confirm they are done reviewing before continuing.

- [ ] **Update REPORT.md:**
  - Fill in **Section 2** Summary of Indications table: paid to date, case reserves, IBNR, total unpaid, and ultimate by segment/AY from `selections/Ultimates.xlsx`. Use totals from the selected ultimates.
  - Fill in **Section 6** Results by Segment: one subsection per measure (Paid LDF, Incurred LDF, etc.) with selected ultimates and method weighting summary; note any low-confidence selections or overrides.
  - Fill in **Section 5.2** Expected Loss Ratios: if IE/BF ran, populate from the ELR input file.
  - Add to **Section 11** Open Questions any AYs where method indications diverged materially or selections required significant judgment.
- [ ] **Update REPLICATE.md Step 6:**
  - Document that `5a-ultimates-create-excel.py` was run to create the ultimates workbook
  - Note that AI selectors made rules-based and open-ended ultimate selections (JSON files created)
  - Document that `5b-ultimates-update-selections.py` populated the Excel file with AI selections
  - **Critical:** If user made manual overrides in the "User Selection" column, list each one with measure, period, selected ultimate, and reasoning. If no overrides, explicitly state "All selections are from Rules-Based AI Selection columns."
  - Add instruction: "To replicate: Extract final ultimates from User Selection column if present, otherwise use Rules-Based AI Selection column. Do not re-run AI selector."

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
