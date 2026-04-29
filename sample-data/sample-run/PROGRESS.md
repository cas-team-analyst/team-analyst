# Step 1: Project Setup

- [ ] Orient to the OS Environment following steps in SKILL.md. It is critical to get this set up before continuing. Downstream steps won't work if we lose track of this task.

- [ ] Respond to the user with the welcome message from assets and wait for their confirmation.

- [ ] Present the project-setup-form from assets. Display the form exactly as written. Wait for the user to provide all the fields before proceeding. Do not skip fields or infer missing values.

- [ ] Use bash cp to copy PROGRESS.md, REPLICATE.md, and REPORT.md from skill assets into the project folder provided in the setup form. Do NOT read them or write them.

- [ ] Create folders `raw-data/`, `processed-data/`, `selections/`, `scripts/`, and `ultimates/` inside the project folder. The user will have selected their triangle file(s) and project folder via the file picker — use those paths to copy the triangle file(s) into `raw-data/` with bash cp. Do not ask the user to copy files manually.

- [ ] **Update REPORT.md:**
  - Fill in the header fields using the values from the setup plus Prepared by (user name), Draft Date (today).
  - Fill in **Section 1.1** with the purpose of this analysis (e.g., "quarterly reserve review") and **Section 1.2** Scope table with any known segment/LOB/coverage/basis info.
  - Add a row to **Section 14** Version History: v0.1, today's date, analyst, "Initial draft".

- [ ] **Update REPLICATE.md:**
  - Fill in the Overview section using values from the setup form: Analysis name, Prepared by, Draft Date, etc.
  - Fill in Step 1: List folders created, note interaction mode selected

# Step 2: Exploratory Data Analysis

- [ ] Review the files available using the explore-excel in the reserving-analysis skill scripts. For each file add a file summary subsection to REPORT.md in the data section.

- [ ] **Update REPORT.md:**
  - Fill in **Section 3.1** Data Used table: one row per file (source name, as-of date, any notes on format or coverage).
  - Fill in **Section 3.2** Data Reconciliation: note whether data was reconciled to a prior valuation or financial system and the result.
  - Fill in **Section 3.3** Data Quality Observations: any outliers, gaps, negative development, coding anomalies, or unusual patterns noticed during exploration.

# Step 3: Data Intake

- [ ] Use bash cp to copy all the numbered scripts and the modules folder from the reserving-analysis skill scripts folder to `scripts/` in the working directory. Do NOT regenerate. Ensure copied files are writable (use chmod +w if needed) since you will edit them to track progress.

- [ ] Based on available data, determine which triangles we will use to come up with Ultimates estimates using the Chain Ladder method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc.

- [ ] If you haven't already found prior selections, ask the user if prior LDF selections exist from a previous analysis. If they do, ask where they are located (Excel file, CSV, database, etc.). You will need to modify `read_and_process_prior_selections()` in `1a-load-and-validate.py` to read from that source during data extraction.

- [ ] Ask the user if prior tail factor selections exist from a previous analysis. If they do, ask where they are located and what tail factor was used for each measure. Create a CSV file at `selections/tail-factor-prior.csv` with columns: `measure`, `cutoff_age`, `tail_factor`, `method`, `reasoning`. This will be loaded by `2d-tail-create-excel.py` and shown in the "Prior Selection" row for reference. If no prior tail selections exist, skip this step.

- [ ] If you haven't already found an input file with Expected Loss Rates (containing period, expected loss rate, and expected frequency), ask the user if this file exists and to place it in the raw-data folder. Without this file, we won't be able to use the Initial Expected or Bornhuetter-Ferguson methods.

- [ ] If initial expected data is not provided (no expected loss rate/frequency file) but exposure is available, confirm with the user whether to use the fallback approximation for BF expected rate: for each accident year, compute diagonal loss per dollar of exposure, smooth with a 3-year rolling average, and round to 3 decimals. Offer these options explicitly before continuing: (1) use this fallback (this is what `3-ie-ultimates.py` defaults to), (2) use a different approach the user specifies, (3) upload initial expected data in the required format, or (4) skip Initial Expected/BF and continue with Chain Ladder only. Note their response REPORT.md.

- [ ] Modify the variables at the top of each script with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH.

- [ ] Modify `1a-load-and-validate.py` to accept the format of the data provided by the user. This includes:
  - Customizing `read_and_process_triangles()` to read triangle data from your source
  - If prior selections exist, customizing `read_and_process_prior_selections()` to read from your source.
  - Run it to verify it works and passes validation. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format.

- [ ] **Confirm data format with the user.** This step always runs, regardless of interaction mode. Use the data-validation template from assets so every analysis presents data validation the same way. Do not improvise the format, reorder sections, or omit headings — even if a section is short or trivial. Populate every section from the actual processed data. The spot-check triangle should default to Paid Loss; if Paid Loss is not present, use the first loss measure available (Incurred, then Reported). Do not proceed until the user confirms.

- [ ] Report to the user what LDF averages (review `1d-ldf-averages.py`) and metrics will be calculated. _(Pause for Selections only: also ask if they'd like to add others before continuing.)_

- [ ] Run all the other Python scripts to create output in `processed-data/`.

- [ ] **Update REPORT.md:**
  - Update **Section 3.1** Data Used table: add rows for triangle types used (paid, incurred, counts), confirm source file names and as-of dates; note if ELR file is present or absent.
  - Update **Section 3.3** Data Quality Observations: note any adjustments made to `1a-load-and-validate.py` (e.g., outlier exclusions, coding changes), any data limitations discovered.
  - Update **Section 3.4** Data Limitations: note missing data types (e.g., no ELR file → IE/BF skipped) and how limitations were handled.
  - Update **Section 1.2** Scope table: fill in accident/underwriting years, coverages, and basis once confirmed from the data.

- [ ] **Update REPLICATE.md Step 2:**
  - List all input files in raw-data/ with brief descriptions
  - Document which scripts were run (1a through 1d)
  - List any customizations made to `1a-load-and-validate.py` (column mappings, data transformations, outlier handling)
  - Note the output files created in `processed-data/`
  - Record the data validation confirmation date

# Step 4: Chain Ladder LDF Selections

- [ ] Tell the user: "I'm about to apply the base selection logic framework to make LDF selections. If you'd like to explore these in detail, you can use `/selection-logic` in a separate session or after this analysis is complete — using it here would interrupt the current workflow."

- [ ] Run `2a-chainladder-create-excel.py` to create the LDF selection workbook and export per-measure context files. The script will print the context file paths it creates (e.g., "Exported MD: selections/chainladder-context-paid_loss.md"). **Capture the list of context file paths** from the script output.

- [ ] **Invoke the rules-based selector once** for all measures. Call the `selector-chain-ladder-ldf-ai-rules-based` subagent and pass the list of context file paths you captured from the script output. The subagent will:
  - Read each context file
  - Apply the rules-based selection framework to each measure independently
  - Write one JSON file per measure: `selections/chainladder-ai-rules-based-<measure>.json`
  
  Verify that one JSON file was created for each measure. **Do NOT read the context files yourself** — the subagent will read them. **Do NOT read the JSON responses** — only verify the files were created.

- [ ] **Invoke the open-ended selector once** for all measures. Call the `selector-chain-ladder-ldf-ai-open-ended` subagent and pass the list of context file paths you captured from the script output. The subagent will:
  - Read each context file
  - Apply holistic actuarial judgment (no rigid rules framework) to each measure independently
  - Write one JSON file per measure: `selections/chainladder-ai-open-ended-<measure>.json`
  
  Verify that one JSON file was created for each measure. **Do NOT read the context files yourself** — the subagent will read them. **Do NOT read the JSON responses** — only verify the files were created.

- [ ] Run `2b-chainladder-update-selections.py` to collect all per-measure JSON files and insert the selections and reasoning into the Excel file. This script will:
  - Load all `selections/chainladder-ai-rules-based-*.json` files and combine them
  - Load all `selections/chainladder-ai-open-ended-*.json` files and combine them
  - Populate the **Rules-Based AI Selection** row (from rules-based files) and **Open-Ended AI Selection** row (from open-ended files) in each sheet

- [ ] Tell the user where `selections/Chain Ladder Selections - LDFs.xlsx` is located. Explain that both rules-based and open-ended AI selections (purple rows) are visible. The **Rules-Based Selection** row is what gets used for ultimates — the user can override it manually. If the Rules-Based Selection row is left blank, the Open-Ended AI Selection will be used as a fallback.

_(Pause for Selections only):_
- [ ] Open `selections/Chain Ladder Selections - LDFs.xlsx` for the user. Let them know they can review and override any AI selections. Pause and wait for the user to confirm they are done reviewing before continuing.

- [ ] **Update REPORT.md:**
  - Fill in **Section 4.1** Methods Applied: add "Paid LDF" and/or "Reported LDF" rows for each triangle measure used; note "Selected via rule-based framework + AI cross-check."
  - Fill in **Section 4.2** Method Weighting / Selection Logic: briefly describe the 14-criteria rule-based framework and that AI selections were used as a cross-check. Note maturity-based weighting approach.
  - Fill in **Section 5.1** Development Patterns: note the selection basis (volume-weighted averages, which average windows were considered).
  - Add to **Section 11** Open Questions any selections flagged as low-confidence or where the rule-based and AI selections diverged materially.

- [ ] **Update REPLICATE.md Step 4:**
  - Document that `2a-chainladder-create-excel.py` was run to create the selection workbook
  - Note that AI selectors made rules-based and open-ended selections (JSON files created)
  - Document that `2b-chainladder-update-selections.py` populated the Excel file with AI selections
  - **Critical:** If user made manual overrides in the "User Selection" row, list each one with measure, interval, selected LDF, and reasoning. If no overrides, explicitly state "All selections are from Rules-Based AI Selection row."
  - Add instruction: "To replicate: Extract final selections from User Selection row if present, otherwise use Rules-Based AI Selection row. Do not re-run AI selector."

# Step 5: Chain Ladder Tail Factor Selections

- [ ] Tell the user: "I'm about to apply the tail factor selection framework. This uses curve fitting diagnostics (Bondy, Exponential Decay, McClenahan, Skurnick, etc.), leave-one-out testing, and a 15-point decision framework to select tail factors. Tail selections are separate from LDF selections and are used in the Chain Ladder ultimates calculation."

- [ ] Run `2c-tail-methods-diagnostics.py` to fit tail curves and generate diagnostics. Debug any errors.

- [ ] Run `2d-tail-create-excel.py` to create `selections/Chain Ladder Selections - Tail.xlsx` with curve fit results and diagnostics. If prior tail selections exist (`selections/tail-factor-prior.csv`), they will be included in a "Prior Selection" row for reference. The script will print the context file paths it creates (e.g., "  Exported MD: selections/tail-context-paid_loss.md"). **Capture the list of context file paths** from the script output.

- [ ] **Invoke the rules-based tail selector once** for all measures. Call the `selector-tail-factor-ai-rules-based` subagent and pass the list of context file paths you captured from the script output. The subagent will:
  - Read each context file
  - Apply the 15-point tail factor decision framework to each measure independently
  - Write one JSON file per measure: `selections/tail-ai-rules-based-<measure>.json`
  
  Verify that one JSON file was created for each measure. **Do NOT read the context files yourself** — the subagent will read them. **Do NOT read the JSON responses** — only verify the files were created.

- [ ] **Invoke the open-ended tail selector once** for all measures. Call the `selector-tail-factor-ai-open-ended` subagent and pass the list of context file paths you captured from the script output. The subagent will:
  - Read each context file
  - Apply holistic actuarial judgment (no rigid rules framework) to each measure independently
  - Write one JSON file per measure: `selections/tail-ai-open-ended-<measure>.json`
  
  Verify that one JSON file was created for each measure. **Do NOT read the context files yourself** — the subagent will read them. **Do NOT read the JSON responses** — only verify the files were created.

- [ ] Run `2e-tail-update-selections.py` to collect all per-measure JSON files and insert the selections into the Excel file. This script will:
  - Load all `selections/tail-ai-rules-based-*.json` files and combine them
  - Load all `selections/tail-ai-open-ended-*.json` files and combine them
  - Populate the **Rules-Based AI Selection** row and **Open-Ended AI Selection** row in each sheet

- [ ] Tell the user where `selections/Chain Ladder Selections - Tail.xlsx` is located. Explain that both rules-based and open-ended AI selections (purple rows) are visible. The **Rules-Based Selection** row is what gets used for ultimates — the user can override it manually. If the Rules-Based Selection row is left blank, the Open-Ended AI Selection will be used as a fallback.

_(Pause for Selections only):_
- [ ] Open `selections/Chain Ladder Selections - Tail.xlsx` for the user. Let them know they can review and override any tail factor selections. Pause and wait for the user to confirm they are done reviewing before continuing.

- [ ] **Update REPORT.md:**
  - Update **Section 5.1** Development Patterns: add tail factor source (curve fit method selected, R² values, leave-one-out diagnostics).
  - Add to **Section 11** Open Questions any tail selections flagged as low-confidence or where curve fit diagnostics were poor or rule-based and AI selections diverged materially.

- [ ] **Update REPLICATE.md Step 5:**
  - Document that `2c-tail-methods-diagnostics.py` was run to fit curves and create diagnostics
  - Document that `2d-tail-create-excel.py` created the tail selection workbook
  - Note that AI selectors made rules-based and open-ended tail selections (JSON files created)
  - Document that `2e-tail-update-selections.py` populated the Excel file with AI selections
  - **Critical:** If user made manual overrides in the "User Selection" row, list each one with measure, cutoff age, tail factor, method, and reasoning. If no overrides, explicitly state "All selections are from Rules-Based AI Selection row."
  - Add instruction: "To replicate: Extract final tail factors from User Selection row if present, otherwise use Rules-Based AI Selection row. Do not re-run AI selector."

# Step 6: Calculate Method Projections

- [ ] Run `2f-chainladder-ultimates.py`, `3-ie-ultimates.py`, and `4-bf-ultimates.py`. Debug any errors that occur. It is normal for IE and BF to get skipped if the user didn't provide the necessary data (exposure, initial expected). Note: `2f-chainladder-ultimates.py` will use tail factors from `selections/Chain Ladder Selections - Tail.xlsx` (priority 1 — user's final selection), falling back to `selections/tail-ai-rules-based.json` (priority 2), then `selections/tail-ai-open-ended.json` (priority 3) if Excel is empty.

- [ ] **Update REPORT.md:**
  - Update **Section 4.1** Methods Applied: confirm which methods actually ran vs. were skipped, and why (e.g., "BF skipped — no ELR file provided").
  - Update **Section 5.2** Expected Loss Ratios: if IE/BF ran, fill in the ELR table from the input file.
  - Update **Section 4.3** LAE Treatment: fill in how DCC/ALAE and A&O/ULAE are handled, if applicable.

- [ ] **Update REPLICATE.md Step 6:**
  - Document that `2f-chainladder-ultimates.py` was run (note which Excel file it read LDFs and tail factors from)
  - Document whether `3-ie-ultimates.py` ran or was skipped (and why)
  - Document whether `4-bf-ultimates.py` ran or was skipped (and why)
  - Note the output file: `ultimates/projected-ultimates.parquet` with columns added by each method

# Step 7: Ultimate Selections

- [ ] Copy `scripts/5a-ultimates-create-excel.py` and `scripts/5b-ultimates-update-selections.py` from the reserving-analysis skill scripts folder into the project `scripts/` folder (use `cp` or `mv`, don't rewrite them yourself). Ensure `scripts/modules/` is already in place (copied in Step 3).

- [ ] Run `scripts/5a-ultimates-create-excel.py` to create the ultimates workbook and export category context files. The script will create two sheets: **Losses** (combining Incurred and Paid) and **Counts** (combining Reported and Closed). It will print the context file paths it creates (e.g., "  Exported MD: selections/ultimates-context-loss.md", "  Exported MD: selections/ultimates-context-count.md"). **Capture the list of context file paths** from the script output.

- [ ] **Invoke the rules-based ultimates selector once** for both categories. Call the `selector-ultimates-ai-rules-based` subagent and pass the list of context file paths you captured from the script output. The subagent will:
  - Read each context file (loss and count)
  - For each category, choose ONE ultimate per accident year (selecting between Incurred/Paid for Loss, or Reported/Closed for Count)
  - Apply the structured method weighting framework to both categories
  - Write two JSON files: `selections/ultimates-ai-rules-based-loss.json` and `selections/ultimates-ai-rules-based-count.json`
  
  Verify that two JSON files were created (one for Loss, one for Count). **Do NOT read the context files yourself** — the subagent will read them. **Do NOT read the JSON responses** — only verify the files were created.

- [ ] **Invoke the open-ended ultimates selector once** for both categories. Call the `selector-ultimates-ai-open-ended` subagent and pass the list of context file paths you captured from the script output. The subagent will:
  - Read each context file (loss and count)
  - For each category, choose ONE ultimate per accident year (selecting between Incurred/Paid for Loss, or Reported/Closed for Count)
  - Apply holistic actuarial judgment (no rigid rules framework) to both categories
  - Write two JSON files: `selections/ultimates-ai-open-ended-loss.json` and `selections/ultimates-ai-open-ended-count.json`
  
  Verify that two JSON files were created (one for Loss, one for Count). **Do NOT read the context files yourself** — the subagent will read them. **Do NOT read the JSON responses** — only verify the files were created.

- [ ] Run `5b-ultimates-update-selections.py` to load the category JSON files and insert both rules-based and open-ended selections and reasoning into `selections/Ultimates.xlsx`. This script will:
  - Load `selections/ultimates-ai-rules-based-loss.json` and `selections/ultimates-ai-rules-based-count.json`
  - Load `selections/ultimates-ai-open-ended-loss.json` and `selections/ultimates-ai-open-ended-count.json`
  - Populate the Rules-Based AI Selection and Open-Ended AI Selection columns in the Loss and Count sheets

- [ ] Tell the user where `selections/Ultimates.xlsx` is located. Explain that both rules-based and open-ended AI selections are visible. The rules-based selection is what gets used by default — the user can override it manually. The open-ended selection provides an independent cross-check. Note that the workbook now has **Losses** and **Counts** sheets instead of per-measure sheets, and one ultimate is selected per category per accident year.

_(Pause for Selections only):_
- [ ] Open `selections/Ultimates.xlsx` for the user. Let them know they can review and override any AI ultimate selections. Pause and wait for the user to confirm they are done reviewing before continuing.

- [ ] **Update PROGRESS.md with headline indications:** After ultimate selections are complete, add a "Headline Indications" section showing: total unpaid reserve, case reserves, and IBNR from `selections/Ultimates.xlsx`. Use totals from the selected ultimates.

- [ ] **Update REPORT.md:**
  - Fill in **Section 2** Summary of Indications table: total unpaid reserve, case reserves, and IBNR by segment/AY from `selections/Ultimates.xlsx`. Use totals from the selected ultimates.
  - Fill in **Section 6** Results by Segment: one subsection per category (Loss and Count) with selected ultimates and method weighting summary; note any low-confidence selections or overrides.
  - Fill in **Section 5.2** Expected Loss Ratios: if IE/BF ran, populate from the ELR input file.
  - Add to **Section 11** Open Questions any AYs where method indications diverged materially or selections required significant judgment.

- [ ] **Update REPLICATE.md Step 7:**
  - Document that `5a-ultimates-create-excel.py` was run to create the ultimates workbook with Losses and Counts sheets
  - Note that AI selectors made rules-based and open-ended ultimate selections for both categories (JSON files created)
  - Document that `5b-ultimates-update-selections.py` populated the Excel file with AI selections
  - **Critical:** If user made manual overrides in the "User Selection" column, list each one with category (Loss or Count), period, selected ultimate, and reasoning. If no overrides, explicitly state "All selections are from Rules-Based AI Selection columns."
  - Add instruction: "To replicate: Extract final ultimates from User Selection column if present, otherwise use Rules-Based AI Selection column. Do not re-run AI selector."

# Step 8: Build Analysis Workbook

- [ ] Copy `scripts/6-analysis-create-excel.py` from the reserving-analysis skill scripts folder into the project `scripts/` folder (use `cp` or `mv`). Ensure `scripts/modules/` is already in place.

- [ ] Run `scripts/6-analysis-create-excel.py` and alert the user of the location and description of the final output files.

- [ ] **Update REPORT.md:**
  - Fill in **Section 2** Summary of Indications table: verify the total unpaid reserve, case reserves, and IBNR totals match the final output from `6-analysis-create-excel.py`.
  - Fill in **Section 0** Reviewer Quick-Start: summarize what the analysis covers (1–2 sentences), what key judgment calls were made, and where reviewer scrutiny is most needed.
  - Update **Section 14** Version History: add a row for the current version with today's date and a summary of changes since v0.1.
  - Fill any other sections to complete the first draft of the report.

- [ ] **Update REPLICATE.md Step 8:**
  - Document that `6-analysis-create-excel.py` was run
  - Note which files it read (projected-ultimates.parquet, Ultimates.xlsx)
  - List the output files created (selected-ultimates.xlsx, post-method-series.xlsx, post-method-triangles.xlsx, complete-analysis.xlsx)
  - Fill in the "Key Outputs" section listing primary deliverables

# Step 9: Technical Review & Peer Review

- [ ] Copy `scripts/7-tech-review.py` from the reserving-analysis skill scripts folder into the project `scripts/` folder (use `cp` or `mv`). Ensure `scripts/modules/` is already in place.

- [ ] Run `scripts/7-tech-review.py` and alert the user of the results and where the output is saved to.

- [ ] **Update REPORT.md:**
  - Fill in **Section 7** Diagnostics and Reasonableness Checks: check off each item and note results (e.g., loss ratio progression, frequency/severity trends, actual vs. expected emergence). Populate "Anomalies to investigate" with any flags from `7-tech-review.py`.
  - Fill in **Section 8.2** Sources of Uncertainty: note key risk factors — process risk (thin data), parameter risk (trend/tail uncertainty), model risk (method selection), any systemic risks flagged.

- [ ] **Update REPLICATE.md Step 9:**
  - Document that `7-tech-review.py` was run
  - List any issues flagged, or note "None - all checks passed"
  - Add any final notes about special considerations or known issues

- [ ] Suggest to the user that they get a Peer Review of the results. If they would like TeamAnalyst to do this, they should close the current workflow (this will clear context to get an independent review) and use the /peer-review skill to get an AI Peer Review.

# Step 10: Summarize Final Outputs

Be explicit and exhaustive. The user should leave this step knowing exactly what was produced, where it lives, and what each file is for. Present the list below (adapted to what actually ran in this analysis — skip items that did not run, e.g., BF if it was skipped).

- [ ] Tell the user the analysis is complete and list every output file produced, grouped by folder. For each file, give the path and a one-line description of what it contains and who it is for. See closing-summary.md from assets.

- [ ] After listing the files, tell the user the single most important takeaway: **REPORT.md is the primary narrative deliverable, and `Complete Analysis.xlsx` is the primary numerical deliverable.** Everything else is supporting evidence or reproducibility material.

- [ ] Ask the user if anything is unclear about any of the outputs before the workflow closes.

- [ ] Ask the user if they have any questions about the analysis itself — methodology, selections, assumptions, data quality, results interpretation, or any findings in the technical review. Remind them they can also run `/peer-review` in a separate session for an independent AI review of the analysis.
