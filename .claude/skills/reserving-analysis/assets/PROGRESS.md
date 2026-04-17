# Step 1: Project Setup
Goal: Set up the project structure and standard documents.
- [ ] Copy markdown files from assets to the project folder (use `cp` or `mv`, don't rewrite it yourself): PROGRESS, REPLICATE, REPORT.
- [ ] Install the Python packages in `requirements.txt`.
- [ ] Ask the user the level of interaction they would like:
  - **Pause for Selections** — Runs automatically, but pauses after LDF selections and again after ultimate selections so you can explore and override them before the analysis continues.
  - **Fully Automatic** — Runs start to finish without stopping for input (except to confirm data format). Selections are made automatically.
  Use these exact option names. Do not recommend one. Note the user's choice at the top of PROGRESS.md.
- [ ] Create folders `raw-data/`, `processed-data/`, `selections/`, `scripts/`, and `ultimates/` in the project folder and ask the user to copy relevant data files into the raw-data folder.
- [ ] **Update REPORT.md:**
  - Fill in the header fields: Analysis name, Valuation Date (if known), Prepared by (user name), Draft Date (today).
  - Fill in **Section 1.1** with the purpose of this analysis (e.g., "quarterly reserve review") and **Section 1.2** Scope table with any known segment/LOB/coverage/basis info.
  - Add a row to **Section 14** Version History: v0.1, today's date, analyst, "Initial draft".

# Step 2: Exploratory Data Analysis
Goal: Understand what data is available.
- [ ] Review the files available using the explore-excel in the reserving-analysis skill scripts. For each file add a file summary subsection to REPORT.md in the data section.
- [ ] **Update REPORT.md:**
  - Fill in **Section 3.1** Data Used table: one row per file (source name, as-of date, any notes on format or coverage).
  - Fill in **Section 3.2** Data Reconciliation: note whether data was reconciled to a prior valuation or financial system and the result.
  - Fill in **Section 3.3** Data Quality Observations: any outliers, gaps, negative development, coding anomalies, or unusual patterns noticed during exploration.

# Step 3: Data Intake

- [ ] Copy all the numbered python scripts from the reserving-analysis skill scripts folder to `scripts/` (use `cp` or `mv`, don't rewrite it yourself): 1a-prep-data.py through 2b-chainladder-update-selections.py. Also copy the `modules/` subfolder (containing `config.py`, `xl_styles.py`, `__init__.py`) into `scripts/modules/` — all scripts import from it.
- [ ] Based on available data, determine which triangles we will use to come up with Ultimates estimates using the Chain Ladder method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc.
- [ ] If you haven't already found prior selections, ask the user if prior LDF selections exist from a previous analysis. If they do, ask where they are located (Excel file, CSV, database, etc.). You will need to modify `read_and_process_prior_selections()` in `1a-prep-data.py` to read from that source during data extraction.
- [ ] If you haven't already found an input file with Expected Loss Rates (containing period, expected loss rate, and expected frequency), ask the user if this file exists and to place it in the raw-data folder. Without this file, we won't be able to use the Initial Expected or Bornhuetter-Ferguson methods.
- [ ] Modify the variables at the top of each script with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH.
- [ ] Modify `1a-prep-data.py` to accept the format of the data provided by the user. This includes:
  - Customizing `read_and_process_triangles()` to read triangle data from your source
  - If prior selections exist, customizing `read_and_process_prior_selections()` to read from your source.
  - Run it to verify it works and passes validation. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format.
- [ ] **Confirm data format with the user.** Show samples of the processed triangle data (row counts, date ranges, sample rows) and ask the user to confirm it looks correct before proceeding. This always happens regardless of mode.
- [ ] Report to the user what LDF averages (review `1d-averages-qa.py`) and metrics will be calculated. _(Pause for Selections only: also ask if they'd like to add others before continuing.)_
- [ ] Run all the other Python scripts to create output in `processed-data/`.
- [ ] **Update REPORT.md:**
  - Update **Section 3.1** Data Used table: add rows for triangle types used (paid, incurred, counts), confirm source file names and as-of dates; note if ELR file is present or absent.
  - Update **Section 3.3** Data Quality Observations: note any adjustments made to `1a-prep-data.py` (e.g., outlier exclusions, coding changes), any data limitations discovered.
  - Update **Section 3.4** Data Limitations: note missing data types (e.g., no ELR file → IE/BF skipped) and how limitations were handled.
  - Update **Section 1.2** Scope table: fill in accident/underwriting years, coverages, and basis once confirmed from the data.

# Step 4: Actuarial Selections: Chain Ladder LDFs

- [ ] Tell the user: "I'm about to apply the base selection logic framework to make LDF selections. This framework includes 14 selection criteria and 10 diagnostic adjustment rules. If you'd like to explore these in detail, you can use `/selection-logic` in a separate session or after this analysis is complete — using it here would interrupt the current workflow."
- [ ] Create a JSON file to hold selections: `selections/chain-ladder.json` with just "[]" for now.
- [ ] Task a single `selector-chain-ladder-ldf` subagent to: Review `selections/Chain Ladder Selections.xlsx` in full (NOT the files at `processed-data`), use this information to make actuarial LDF selections for each combination of Chain Ladder measure and interval **including a tail factor (interval "Tail") for each measure**, and add the selections and specific reasoning for each selection to `selections/chain-ladder.json`, each as a dict/object/map in the array with keys "measure", "interval", "selection", "reasoning" (along with other selections).
- [ ] Task a single `selector-chain-ladder-ldf-ai` subagent to: Review `selections/Chain Ladder Selections.xlsx` in full, independently make LDF selections for each combination of measure and interval **including a tail factor** using its own actuarial judgment (no rigid rules framework), and save results to `selections/chain-ladder-ai.json` with the same schema (`"measure"`, `"interval"`, `"selection"`, `"reasoning"`).
- [ ] Run `2b-chainladder-update-selections.py` to insert the selections and reasoning into the Excel file. This will populate both the **Selection** row (from `chain-ladder.json`) and the **AI Selection** row (from `chain-ladder-ai.json`, if present) in each sheet.
- [ ] Tell the user where `selections/Chain Ladder Selections.xlsx` is located. Explain that both rule-based and AI selections (purple rows) are visible. The **Selection** row is what gets used for ultimates — the user can override it manually. If the Selection row is left blank, the AI Selection will be used as a fallback.

_(Pause for Selections only):_
- [ ] Open `selections/Chain Ladder Selections.xlsx` for the user. Let them know they can review and override any AI selections. Pause and wait for the user to confirm they are done reviewing before continuing.

- [ ] **Update REPORT.md:**
  - Fill in **Section 4.1** Methods Applied: add "Paid LDF" and/or "Reported LDF" rows for each triangle measure used; note "Selected via rule-based framework + AI cross-check."
  - Fill in **Section 4.2** Method Weighting / Selection Logic: briefly describe the 14-criteria rule-based framework and that AI selections were used as a cross-check. Note maturity-based weighting approach.
  - Fill in **Section 5.1** Development Patterns: note the selection basis (volume-weighted averages, which average windows were considered) and the tail factor source (curve fit, benchmark, or judgment).
  - Add to **Section 11** Open Questions any selections flagged as low-confidence or where the rule-based and AI selections diverged materially.

# Step 5: Run Methods That Don't Require Selections

- [ ] Run `2c-chainladder-ultimates.py`, `3-ie-ultimates.py`, and `4-bf-ultimates.py`. Debug any errors that occur. It is normal for IE and BF to get skipped if the user didn't provide the necessary data (exposure, initial expected).
- [ ] **Update REPORT.md:**
  - Update **Section 4.1** Methods Applied: confirm which methods actually ran vs. were skipped, and why (e.g., "BF skipped — no ELR file provided").
  - Update **Section 5.2** Expected Loss Ratios: if IE/BF ran, fill in the ELR table from the input file.
  - Update **Section 4.3** LAE Treatment: fill in how DCC/ALAE and A&O/ULAE are handled, if applicable.

# Step 6: Actuarial Selections: Ultimates

- [ ] Copy `scripts/5a-ultimates-create-excel.py` and `scripts/5b-ultimates-update-selections.py` from the reserving-analysis skill scripts folder into the project `scripts/` folder (use `cp` or `mv`, don't rewrite them yourself). Ensure `scripts/modules/` is already in place (copied in Step 3).
- [ ] Task a single `selector-ultimates` subagent to: Review `selections/Ultimates.xlsx` in full (NOT the files at `processed-data`), use this information to make actuarial ultimate selections for each combination of Chain Ladder measure and period, and add the selections and specific reasoning for each selection to `selections/ultimates.json`, each as a dict/object/map in the array with keys "measure", "period", "selection", "reasoning" (along with other selections).
- [ ] Run `5b-ultimates-update-selections.py` to insert the selections and reasoning into `selections/Ultimates.xlsx`.
- [ ] Tell the user where `selections/Ultimates.xlsx` is located and that AI selections have been written to it.

_(Pause for Selections only):_
- [ ] Open `selections/Ultimates.xlsx` for the user. Let them know they can review and override any AI ultimate selections. Pause and wait for the user to confirm they are done reviewing before continuing.

- [ ] **Update REPORT.md:**
  - Fill in **Section 2** Summary of Indications table: paid to date, case reserves, IBNR, total unpaid, and ultimate by segment/AY from `selections/Ultimates.xlsx`. Use totals from the selected ultimates.
  - Fill in **Section 6** Results by Segment: one subsection per measure (Paid LDF, Incurred LDF, etc.) with selected ultimates and method weighting summary; note any low-confidence selections or overrides.
  - Fill in **Section 5.2** Expected Loss Ratios: if IE/BF ran, populate from the ELR input file.
  - Add to **Section 11** Open Questions any AYs where method indications diverged materially or selections required significant judgment.

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

# Step 8: Suggest Peer Review

- [ ] Suggest to the user that they get a Peer Review of the results. If they would like TeamAnalyst to do this, they should close the current workflow (this will clear context to get an independent review) and use the /peer-review skill to get a AI Peer Review.
