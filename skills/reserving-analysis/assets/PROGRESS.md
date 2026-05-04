# Step 1: Project Setup

- [ ] Respond to the user with the welcome message from assets and wait for their confirmation.

- [ ] Present the project-setup-form from assets. Display the form exactly as written. Wait for the user to provide all the fields before proceeding. Do not skip fields or infer missing values.

- [ ] Use bash cp to copy PROGRESS.md, REPLICATE.md, and REPORT.md from skill assets into the project folder provided in the setup form. Do NOT read them or write them.

- [ ] Create folders `raw-data/`, `processed-data/`, `selections/`, `scripts/`, and `ultimates/` inside the project folder. The user will have selected their triangle file(s) and project folder via the file picker — use those paths to copy the triangle file(s) into `raw-data/` with bash cp. Do not ask the user to copy files manually.

- [ ] **Update REPORT.md:**
  - Fill in the header fields using the values from the setup plus Prepared by (user name), Draft Date (today).
  - Fill in **Section 1.1 Purpose** with the purpose of this analysis from the setup form (e.g., "quarterly reserve review for internal management").
  - Fill in **Section 1.2 Scope** table with any known info from setup: Segment/LOB, basis (gross/net), currency, geography.
  - Fill in **Section 1.3 Intended Internal Users** with the audience from the setup form.
  - Add a row to **Section 14 Version History**: v0.1, today's date, analyst name, "Initial draft".

- [ ] **Update REPLICATE.md:**
  - Fill in the Overview section using values from the setup form: Analysis name, Prepared by, Draft Date, etc.
  - Fill in Step 1: List folders created, note interaction mode selected

# Step 2: Exploratory Data Analysis

- [ ] Review the files available using the explore-excel in the reserving-analysis skill scripts. For each file add a file summary subsection to REPORT.md in the data section.

- [ ] **Update REPORT.md:**
  - Fill in **Section 3.1 Data Used** table: one row per data file (source name, as-of date, notes on format/coverage). Include triangle files and any other inputs.
  - Fill in **Section 3.2 Data Reconciliation**: note whether data was reconciled to a prior valuation or financial system. If no reconciliation was performed, state "Not reconciled - data accepted as provided by [source]."
  - Fill in **Section 3.3 Data Quality Observations**: any outliers, gaps, negative development, coding anomalies, or unusual patterns noticed during exploration. If none observed, state "No material data quality issues observed during initial review."

# Step 3: Data Intake

- [ ] Use bash cp to copy all the numbered scripts and the modules folder from the reserving-analysis skill scripts folder to `scripts/` in the working directory. Do NOT regenerate.

- [ ] Based on available data, determine which triangles we will use to come up with Ultimates estimates using the Chain Ladder method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc.

- [ ] If you haven't already found prior selections, ask the user if prior LDF selections exist from a previous analysis. If they do, ask where they are located (Excel file, CSV, database, etc.). You will need to modify `read_and_process_prior_selections()` in `1a-load-and-validate.py` to read from that source during data extraction.

- [ ] Ask the user if prior tail factor selections exist from a previous analysis. If they do, ask where they are located and what tail factor was used for each measure. Create a CSV file at `selections/tail-factor-prior.csv` with columns: `measure`, `cutoff_age`, `tail_factor`, `method`, `reasoning`. This will be loaded by `2d-tail-create-excel.py` and shown in the "Prior Selection" row for reference. If no prior tail selections exist, skip this step.

- [ ] If you haven't already found an input file with Expected Loss Rates (containing period, expected loss rate, and expected frequency), ask the user if this file exists and to place it in the raw-data folder. Without this file, we won't be able to use the Initial Expected or Bornhuetter-Ferguson methods.

- [ ] **ELR Fallback Decision (CRITICAL USER COMMUNICATION):** If initial expected data is not provided (no expected loss rate/frequency file) but exposure is available, **STOP and clearly inform the user:**
  
  "**Expected Loss Rate (ELR) file not found.** Initial Expected and Bornhuetter-Ferguson methods require ELR data.
  
  **A fallback approximation is available:** For each accident year, I can compute the diagonal actual loss per dollar of exposure, smooth it with a 3-year rolling average, and use that as the expected rate. This is an empirical approximation based on historical loss emergence — it's less forward-looking than a pricing ELR but still provides a reasonable expected baseline for the BF method.
  
  **Your options:**
  1. **Use the fallback** (3-year rolling average of empirical loss rates) — this is what `3-ie-ultimates.py` defaults to
  2. **Use a different approach** — if you have an alternative source or method, describe it and I'll adjust the script
  3. **Upload the ELR file** — if you can provide expected loss rate/frequency data in the required format (columns: period, expected_loss_rate, expected_frequency)
  4. **Skip Initial Expected/BF entirely** — continue with Chain Ladder only
  
  Which option would you like to use?"
  
  Wait for the user to choose. Note their response in REPORT.md Section 5.2 (Expected Loss Ratios) and Section 5.5 (Assumption Rationale). If they choose option 1, also add to Section 3.4 (Data Limitations): "No ELR file provided - using 3-year rolling average of empirical loss rates as fallback for Initial Expected/BF methods."

- [ ] Modify the variables at the top of each script with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH.

- [ ] Modify `1a-load-and-validate.py` to accept the format of the data provided by the user. This includes:
  - Customizing `read_and_process_triangles()` to read triangle data from your source
  - If prior selections exist, customizing `read_and_process_prior_selections()` to read from your source.
  - Run it to verify it works and passes validation. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format.

- [ ] **Confirm data format with the user.** This step always runs, regardless of interaction mode. Use the data-validation template from assets so every analysis presents data validation the same way. Do not improvise the format, reorder sections, or omit headings — even if a section is short or trivial. Populate every section from the actual processed data. The spot-check triangle should default to Paid Loss; if Paid Loss is not present, use the first loss measure available (Incurred, then Reported). Do not proceed until the user confirms.

- [ ] Report to the user what LDF averages (review `1d-ldf-averages.py`) and metrics will be calculated. _(Pause for Selections only: also ask if they'd like to add others before continuing.)_

- [ ] Run all the other Python scripts to create output in `processed-data/`.

- [ ] **Update REPORT.md:**
  - Update **Section 3.1 Data Used** table: add rows for triangle types used (paid loss, incurred loss, reported count, closed count, exposure), confirm source file names and as-of dates; note if ELR file is present or absent.
  - Update **Section 3.3 Data Quality Observations**: note any adjustments made to `1a-load-and-validate.py` (e.g., outlier exclusions, coding changes, negative development corrections), any data limitations discovered.
  - Update **Section 3.4 Data Limitations**: note missing data types (e.g., "No closed count data - unable to estimate closure rates", "No ELR file provided - IE/BF methods skipped", "No prior selections available") and how limitations impact the analysis.
  - Update **Section 1.2 Scope** table: fill in accident/underwriting years range (e.g., "2001-2024"), coverages (which measures are available), and basis once confirmed from the processed data.

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
  - Fill in **Section 4.1 Methods Applied** table: add rows for each method used. For each triangle measure (Paid Loss, Incurred Loss, Reported Count), add rows for "Paid LDF" or "Incurred LDF" or "Reported LDF" as applicable. In "Why Selected" column, note "Selected via rule-based framework with AI cross-check - mature year primary method."
  - Fill in **Section 4.2 Method Weighting / Selection Logic**: Describe the 14-criteria rule-based framework used for LDF selections and note that AI selections provided a cross-check. Describe maturity-based weighting approach (e.g., "Chain Ladder weighted 100% for years 96+ months developed, BF/CL blend for immature years").
  - Fill in **Section 5.1 Development Patterns**: Note the selection basis: "Volume-weighted averages with averaging windows from 3-year to all-year. Rule-based framework selected optimal window per age based on stability, volume, and fit diagnostics."
  - **Section 5.3 Trend Assumptions** and **Section 5.4 Other Assumptions** are already filled with "Not implemented" - leave as-is unless user performed manual trend adjustments.
  - **Section 4.3 LAE Treatment** is already filled with "Not applicable" - leave as-is unless user indicates LAE is handled separately.
  - Add to **Section 11 Open Questions** any LDF selections flagged as low-confidence or where the rule-based and AI selections diverged materially (check the JSON reasoning files for "low" confidence flags).

- [ ] **Update REPLICATE.md Step 4:**
  - Document that `2a-chainladder-create-excel.py` was run to create the selection workbook
  - Note that AI selectors made rules-based and open-ended selections (JSON files created)
  - Document that `2b-chainladder-update-selections.py` populated the Excel file with AI selections
  - **Critical:** If user made manual overrides in the "User Selection" row, list each one with measure, interval, selected LDF, and reasoning. If no overrides, explicitly state "All selections are from Rules-Based AI Selection row."
  - Add instruction: "To replicate: Extract final selections from User Selection row if present, otherwise use Rules-Based AI Selection row. Do not re-run AI selector."

# Step 5: Chain Ladder Tail Curve Method Selections

- [ ] Tell the user: "I'm about to apply the tail curve selection framework. This uses curve fitting diagnostics (Bondy, Exponential Decay, McClenahan, Skurnick, etc.) and leave-one-out testing to select the best curve method for extrapolating development beyond the empirical cutoff age. The LDF agents already selected the cutoff age (where empirical selections end). The tail curve method will be used by the Chain Ladder script to generate fitted LDFs for ages after the cutoff."

- [ ] Run `2c-tail-methods-diagnostics.py` to fit tail curves and generate diagnostics. Debug any errors.

- [ ] Run `2d-tail-create-excel.py` to create `selections/Chain Ladder Selections - Tail.xlsx` with curve fit results and diagnostics. If prior tail selections exist (`selections/tail-factor-prior.csv`), they will be included in a "Prior Selection" row for reference. The script will print the context file paths it creates (e.g., "  Exported MD: selections/tail-context-paid_loss.md"). **Capture the list of context file paths** from the script output.

- [ ] **Invoke the rules-based tail selector once** for all measures. Call the `selector-tail-curve-ai-rules-based` subagent and pass the list of context file paths you captured from the script output. The subagent will:
  - Read each context file
  - Apply the tail curve decision framework to each measure independently
  - Select the best curve METHOD (not tail factor) based on diagnostics
  - Write one JSON file per measure: `selections/tail-curve-ai-rules-based-<measure>.json`
  
  Verify that one JSON file was created for each measure. **Do NOT read the context files yourself** — the subagent will read them. **Do NOT read the JSON responses** — only verify the files were created.

- [ ] **Invoke the open-ended tail selector once** for all measures. Call the `selector-tail-curve-ai-open-ended` subagent and pass the list of context file paths you captured from the script output. The subagent will:
  - Read each context file
  - Apply holistic actuarial judgment (no rigid rules framework) to each measure independently
  - Write one JSON file per measure: `selections/tail-curve-ai-open-ended-<measure>.json`
  
  Verify that one JSON file was created for each measure. **Do NOT read the context files yourself** — the subagent will read them. **Do NOT read the JSON responses** — only verify the files were created.

- [ ] Run `2e-tail-update-selections.py` to collect all per-measure JSON files and insert the selections into the Excel file. This script will:
  - Load all `selections/tail-curve-ai-rules-based-*.json` files and combine them
  - Load all `selections/tail-curve-ai-open-ended-*.json` files and combine them
  - Populate the **Rules-Based AI Selection** row and **Open-Ended AI Selection** row in each sheet

- [ ] Tell the user where `selections/Chain Ladder Selections - Tail.xlsx` is located. Explain that both rules-based and open-ended AI selections (purple rows) are visible. The **Rules-Based Selection** row shows the selected curve METHOD (e.g., 'bondy', 'exp_dev_quick') — this is what gets used to generate fitted LDFs in the Chain Ladder script. The user can override it manually. If the Rules-Based Selection row is left blank, the Open-Ended AI Selection will be used as a fallback.

_(Pause for Selections only):_
- [ ] Open `selections/Chain Ladder Selections - Tail.xlsx` for the user. Let them know they can review and override the tail curve method selections. Pause and wait for the user to confirm they are done reviewing before continuing.

- [ ] **Update REPORT.md:**
  - Update **Section 5.1 Development Patterns**: Add tail curve details: "Tail curve method selected from curve fitting diagnostics. [State which method was selected for each measure - Bondy, Exponential Decay, etc.] with R² values of [X.XX]. Leave-one-out testing showed [describe results]. Fitted LDFs for ages beyond the cutoff are generated using the selected curve method's formula." Reference the tail selection workbook for full diagnostics.
  - Add to **Section 11 Open Questions** any tail curve selections flagged as low-confidence or where curve fit diagnostics were poor (R² < 0.85) or where rule-based and AI selections diverged materially.

- [ ] **Update REPLICATE.md Step 5:**
  - Document that `2c-tail-methods-diagnostics.py` was run to fit curves and create diagnostics
  - Document that `2d-tail-create-excel.py` created the tail selection workbook
  - Note that AI selectors made rules-based and open-ended tail curve method selections (JSON files created)
  - Document that `2e-tail-update-selections.py` populated the Excel file with AI selections
  - **Critical:** If user made manual overrides in the "User Selection" row, list each one with measure and selected curve method (e.g., 'bondy', 'exp_dev_quick'). If no overrides, explicitly state "All selections are from Rules-Based AI Selection row."
  - Add instruction: "To replicate: Extract final tail curve methods from User Selection row if present, otherwise use Rules-Based AI Selection row. Fitted LDFs are generated by `2f-chainladder-ultimates.py` using the selected curve method. Do not re-run AI selector."

# Step 6: Calculate Method Projections

- [ ] Run `2f-chainladder-ultimates.py`, `3-ie-ultimates.py`, and `4-bf-ultimates.py`. Debug any errors that occur. It is normal for IE and BF to get skipped if the user didn't provide the necessary data (exposure, initial expected). Note: `2f-chainladder-ultimates.py` will:
  1. Read empirical LDF selections from `selections/Chain Ladder Selections - LDFs.xlsx` (up to the cutoff age)
  2. Read the selected tail curve METHOD from `selections/Chain Ladder Selections - Tail.xlsx` (priority: User Selection → Rules-Based AI → Open-Ended AI)
  3. Load curve parameters from `processed-data/tail-scenarios.parquet`
  4. Generate fitted LDFs for ages beyond the cutoff using the selected curve method's formula
  5. Build complete CDFs by chaining empirical + fitted LDFs
  6. Calculate Chain Ladder ultimates and save to `ultimates/projected-ultimates.parquet`

- [ ] **Update REPORT.md:**
  - Update **Section 4.1 Methods Applied** table: Confirm which methods actually ran vs. were skipped. If IE or BF were skipped, note why (e.g., "Initial Expected skipped - no expected loss rate file provided"). Update the "Segments Applied" and "Why Selected" columns based on actual execution.
  - Update **Section 5.2 Expected Loss Ratios**: If IE/BF ran, fill in the ELR table showing the a priori expected loss ratios used for each accident year. If these methods were skipped, state "Not applicable - IE/BF methods not used in this analysis."
  - **Section 4.3 LAE Treatment** should already state "Not applicable" unless user has specified separate LAE handling - confirm this is correct or update if needed.

- [ ] **Update REPLICATE.md Step 6:**
  - Document that `2f-chainladder-ultimates.py` was run (note which Excel file it read LDFs and tail factors from)
  - Document whether `3-ie-ultimates.py` ran or was skipped (and why)
  - Document whether `4-bf-ultimates.py` ran or was skipped (and why)
  - Note the output file: `ultimates/projected-ultimates.parquet` with columns added by each method

# Step 7: Ultimate Selections

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

- [ ] Run `scripts/5c-summary-indications.py` to compute headline indications from the selected ultimates. This script reads `selections/Ultimates.xlsx` and outputs a formatted markdown table with total unpaid reserve, case reserves, and IBNR.

- [ ] **Update PROGRESS.md with headline indications:** Copy the markdown table output from `5c-summary-indications.py` into a "Headline Indications" section in PROGRESS.md.

- [ ] **Update REPORT.md:**
  - Fill in **Section 2 Summary of Indications** table: Extract total unpaid reserve, case reserves, and IBNR from the selected ultimates in `selections/Ultimates.xlsx`. Sum across all accident years. If multiple segments/categories exist, create one row per category (Loss, Count) showing totals.
  - Fill in **Section 2 Comparison to prior estimate** table: If prior estimate data is available, show prior ultimate, current ultimate, change ($), and change (%). If no prior estimate exists, state "Not applicable - no prior estimate available for comparison."
  - Fill in **Section 2 Key drivers of change**: If comparing to prior, briefly describe what changed (e.g., "emergence better/worse than expected", "LDF selections revised", "additional year of data"). If no comparison, state "Not applicable."
  - Fill in **Section 6 Results by Segment**: Create one subsection (6.1, 6.2, etc.) per category (Loss, Count). For each, state: "Selected ultimates: See Ultimates.xlsx [category] sheet", "Method weighting: [summarize - e.g., mature years use CL, immature years use BF]", "Notable judgment calls: [list any manual overrides or low-confidence selections]."
  - Update **Section 5.2 Expected Loss Ratios**: If IE/BF methods were used, populate the table with the a priori ELRs by accident year. If not used, state "Not applicable - IE/BF not used."
  - Update **Section 5.5 Assumption Rationale**: Add the ELR source if applicable (e.g., "Expected loss ratios from [company pricing / industry benchmark / historical average]").
  - Add to **Section 11 Open Questions** any accident years where method indications diverged materially (e.g., "> 20% difference between CL and BF") or where selections required significant judgment. Flag any years with low confidence ratings.

- [ ] **Update REPLICATE.md Step 7:**
  - Document that `5a-ultimates-create-excel.py` was run to create the ultimates workbook with Losses and Counts sheets
  - Note that AI selectors made rules-based and open-ended ultimate selections for both categories (JSON files created)
  - Document that `5b-ultimates-update-selections.py` populated the Excel file with AI selections
  - **Critical:** If user made manual overrides in the "User Selection" column, list each one with category (Loss or Count), period, selected ultimate, and reasoning. If no overrides, explicitly state "All selections are from Rules-Based AI Selection columns."
  - Add instruction: "To replicate: Extract final ultimates from User Selection column if present, otherwise use Rules-Based AI Selection column. Do not re-run AI selector."

# Step 8: Build Analysis Workbook

- [ ] Run `scripts/6-analysis-create-excel.py` and alert the user of the location and description of the final output files.

- [ ] **Update REPORT.md:**
  - Verify **Section 2 Summary of Indications** table: Confirm the total unpaid reserve, case reserves, and IBNR totals match the final output from `6-analysis-create-excel.py`. Check against the Analysis.xlsx file totals.
  - Fill in **Section 0 Reviewer Quick-Start**: Write a brief 1-2 sentence summary of what the analysis covers (e.g., "Workers Compensation reserve analysis for AY 2001-2024 using Chain Ladder and Bornhuetter-Ferguson methods"). List 2-3 key judgment calls made (e.g., "BF selected for AY 2023-2024 due to low maturity"). State where reviewer scrutiny is most needed (e.g., "Recent year ultimate selections", "Tail factor assumptions", "Method divergence for AY 2012").
  - Fill in **Section 9 Reliance on Others** table: List data sources and information relied upon (e.g., "Claims Department - triangle data as of [date]", "Finance - exposure data", etc.). If no external reliance, state "No external sources relied upon beyond internal company data systems."
  - Fill in **Section 10 Information Date**: State the valuation date/as-of date for the analysis. Under "Subsequent events considered", state either "None known as of [draft date]" or describe any events.
  - Update **Section 14 Version History**: Add a row for the current version with today's date and a summary of changes since v0.1 (e.g., "v0.2 - added ultimate selections and completed initial analysis").
  - **Final completeness check**: Review all sections and fill any remaining placeholders. For sections that genuinely don't apply (LAE, trending, sensitivity), confirm the "Not implemented" or "Not applicable" text is present. For sections with content, ensure no bracketed placeholders remain.

- [ ] **Update REPLICATE.md Step 8:**
  - Document that `6-analysis-create-excel.py` was run
  - Note which files it read (projected-ultimates.parquet, Ultimates.xlsx)
  - List the output files created (selected-ultimates.xlsx, post-method-series.xlsx, post-method-triangles.xlsx, complete-analysis.xlsx)
  - Fill in the "Key Outputs" section listing primary deliverables

# Step 9: Technical Review & Peer Review

- [ ] Run `scripts/7-tech-review.py` and alert the user of the results and where the output is saved to.

- [ ] **Update REPORT.md:**
  - Fill in **Section 7 Diagnostics and Reasonableness Checks**: Check off each item in the checklist and add notes:
    - "Loss ratios by AY": State "Reviewed - progression is reasonable" or note any anomalies (e.g., "AY 2007 shows elevated loss ratio - large claim suspected")
    - "Frequency / severity trends": State "Consistent with historical patterns" or note any flags from `7-tech-review.py` (e.g., "YoY severity spikes flagged in periods 3, 4, 6 - see tech review")
    - "Implied paid and reported development": State "Patterns consistent with triangle selections"
    - "Actual vs. expected emergence": State "Not applicable - no prior estimate" or provide brief comparison if available
    - "Comparison to independent benchmark": State "Not performed" unless benchmark data was used
    - "Hindsight test on prior ultimates": State "Not performed" or provide results if available
    - "Ratio of IBNR to case reserves": State "Reviewed - ratios reasonable" or note concerns
  - Under **"Anomalies to investigate"**: List all FAIL and WARN items from `7-tech-review.py`. Examples: "Tech review FAIL: 16 periods with IBNR < 0 (IE method mis-calibrated)", "Tech review WARN: YoY severity spikes of 45%, 101%, 244% in periods 3, 4, 6", "Tech review WARN: 136 reported-to-ult cells > 1.0 due to sub-1.0 count CDFs"
  - Fill in **Section 8.2 Sources of Uncertainty**: Describe key risk factors:
    - Process risk: e.g., "Limited development history for recent years - thin data increases parameter uncertainty"
    - Parameter risk: e.g., "Tail factor uncertainty - curve fits show R² of [values], alternative tail factors could shift reserve by [estimate]", "LDF selection uncertainty - mature years stable, recent years volatile"
    - Model risk: e.g., "Method selection for immature years - CL vs BF choice drives material reserve differences"
    - Systemic risk: Note any flagged by tech review or judgment (e.g., "AY 2007 large loss not separately estimated - if re-opened could impact ultimate")
  - **Section 8.1 Sensitivity** is marked "Not implemented" - leave as-is unless user performed manual sensitivity testing.

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
