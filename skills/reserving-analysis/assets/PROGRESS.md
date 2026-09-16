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

- [ ] Respond to the user with the message from `assets/welcome-message.md` and wait for confirmation.

- [ ] Present the form `assets/project-setup-form.md`. Display the form exactly as written. Wait for the user to provide all the fields before proceeding. Do not skip fields or infer missing values.

- [ ] Use bash cp or similar to copy PROGRESS.md, REPLICATE.md, and REPORT.md from skill assets into the project folder provided in the setup form. Do NOT read them or write them. 

- [ ] If the user selected Selections Demo mode, rm REPLICATE.md and REPORT.md and remove mentions from PROGRESS.md. If the user selects Fully Automatic, remove PROGRESS.md steps that involve manual user input or review. Send PROGRESS.md, REPLICATE.md, and REPORT.md to the user as files, if they are still being used. 

- [ ] Add the phases from PROGRESS.md to the task list. Include the complete phase (all [ ] steps) in each task.

- [ ] Create folders `raw-data/`, `processed-data/`, `selections/`, `selections/agent-logic/`, and `scripts/` inside the project folder. `selections/agent-logic/` holds the non-Excel selection inputs and outputs (JSON, MD context files, saved selector agent specs) so `selections/` itself only shows the Excel workbooks a human needs to open. The user will have selected their triangle file(s) and project folder via the file picker — use those paths to copy the triangle file(s) into `raw-data/` with bash cp. Do not ask the user to copy files manually.

- [ ] Update REPORT.md: search for `AI (Phase 1):` in the template and follow the fill instructions at each match.

- [ ] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

# Phase 2: Exploratory Data Analysis

- [ ] Review the files available using the `scripts/preview_data_file.py`.

- [ ] Update REPORT.md: search for `AI (Phase 2):` in the template and follow the fill instructions at each match (Sections 3.1 Data Used, 3.2 Data Reconciliation, 3.3 Data Quality Observations).

- [ ] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

# Phase 3: Data Intake

- [ ] Use bash cp to copy all the numbered scripts and the modules folder from the reserving-analysis skill scripts folder to `scripts/` in the working directory. Do NOT regenerate.

- [ ] Based on available data, determine which triangles we will use to come up with Ultimates estimates using the Chain Ladder method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc.

- [ ] If you haven't already found prior selections, ask the user if prior LDF selections exist from a previous analysis. If they do, ask where they are located (Excel file, CSV, database, etc.). You will need to modify `read_and_process_prior_selections()` in `1a-load-and-validate.py` to read from that source during data extraction.

- [ ] Ask the user if prior tail curve selections exist from a previous analysis. If they do, ask where they are located and what tail factor was used for each measure. Create a CSV file at `selections/agent-logic/tail-factor-prior.csv` with columns: `measure`, `cutoff_age`, `tail_factor`, `method`, `reasoning`. This will be loaded by `2d-tail-create-excel.py` and shown in the "Prior Selection" row for reference. If no prior tail selections exist, skip this step.

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

- [ ] Report to the user what LDF averages (review `1d-ldf-averages.py`) and metrics will be calculated. _(Pause for Selections/Selections Demo: also ask if they'd like to add others before continuing.)_

- [ ] Run all the other Python scripts to create output in `processed-data/`.

- [ ] Update REPORT.md: search for `AI (Phase 3):` in the template and follow the fill instructions at each match.

- [ ] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

# Phase 4: Chain Ladder LDF Selections

- [ ] Run `2a-chainladder-create-excel.py` to create the LDF selection workbook and export per-measure context files. The script will print the context file paths it creates (e.g., "Exported MD: selections/agent-logic/chainladder-context-paid_loss.md"). **Capture the list of context file paths** from the script output.

- [ ] Before you call subagents, share the selector subagent instructions and a context file example with the user by sending them as files (not just describing them in chat) so they appear in the output tab: send the `selector-chain-ladder-ldf-ai-framework` and `selector-chain-ladder-ldf-ai-open-ended` agent files under user-readable names ("Framework-based Selector Agent" and "Open-Ended Selector Agent"), plus one of the context files captured above (call it "AI Context Example: LDF"). This is to allow the user to review this for transparency while they wait for selections to finish.

- [ ] **Invoke the framework selector and the open-ended selector in parallel** (call both subagents in the same message, not one after the other). Each covers all measures in a single invocation:
  - Framework: call a general subagent following the spec at `selector-chain-ladder-ldf-ai-framework` and pass the list of context file paths you captured from the script output. It will read each context file (one measure at a time), apply the selection framework, and write one JSON file per measure: `selections/agent-logic/chainladder-ai-framework-<measure>.json`
  - Open-ended: call a general subagent following the spec at `selector-chain-ladder-ldf-ai-open-ended` and pass the same list of context file paths. It will read each context file (one measure at a time), apply holistic actuarial judgment, and write one JSON file per measure: `selections/agent-logic/chainladder-ai-open-ended-<measure>.json`
  
  Verify that one JSON file per measure was created for each selector. **Do NOT read the context files yourself** — the subagents will read them. **Do NOT read the JSON responses** — only verify the files were created. This keeps each selector's judgment independent: if you read the context or reasoning first, your own read on the data can leak into how you frame later steps and bias any selection stage toward agreeing with what you already concluded.

- [ ] Use bash cp to copy the `selector-chain-ladder-ldf-ai-framework` and `selector-chain-ladder-ldf-ai-open-ended` agent files into `selections/agent-logic/` so the selection logic that produced these JSON files is preserved alongside the output.

- [ ] Run `2b-chainladder-update-selections.py` to collect all per-measure JSON files and insert the selections and reasoning into the Excel file. This script will:
  - Load all `selections/agent-logic/chainladder-ai-framework-*.json` files and combine them
  - Load all `selections/agent-logic/chainladder-ai-open-ended-*.json` files and combine them
  - Populate the **Framework AI Selection** row (from framework files) and **Open-Ended AI Selection** row (from open-ended files) in each sheet

- [ ] Tell the user where `selections/Chain Ladder Selections - LDFs.xlsx` is located. Explain that both framework and open-ended AI selections (purple rows) are visible. The **Framework AI Selection** row is what gets used for ultimates — the user can override it manually. If the Framework AI Selection row is left blank, the Open-Ended AI Selection will be used as a fallback.

_(Pause for Selections/Selections Demo):_
- [ ] Open `selections/Chain Ladder Selections - LDFs.xlsx` for the user. Let them know they can review and override any AI selections. Pause and wait for the user to confirm they are done reviewing before continuing.

- [ ] Update REPORT.md: search for `AI (Phase 4):` in the template and follow the fill instructions at each match. Sections 5.3, 5.4, and 4.3 are pre-filled; confirm they are correct and leave as-is.

- [ ] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

# Phase 5: Chain Ladder Tail Curve Method Selections

- [ ] Tell the user: "I'm about to apply the tail curve selection framework. This uses curve fitting diagnostics (Bondy, Exponential Decay, McClenahan, Skurnick, etc.) and leave-one-out testing to select the best curve method for extrapolating development beyond the empirical cutoff age. The LDF agents already selected the cutoff age (where empirical selections end). The tail curve method will be used by the Chain Ladder script to generate fitted LDFs for ages after the cutoff."

- [ ] Run `2c-tail-methods-diagnostics.py` to fit tail curves and generate diagnostics. Debug any errors.

- [ ] Run `2d-tail-create-excel.py` to create `selections/Chain Ladder Selections - Tail.xlsx` with curve fit results and diagnostics. If prior tail selections exist (`selections/agent-logic/tail-factor-prior.csv`), they will be included in a "Prior Selection" row for reference. The script will print the context file paths it creates (e.g., "  Exported MD: selections/agent-logic/tail-context-paid_loss.md"). **Capture the list of context file paths** from the script output.

- [ ] Before you call subagents, share the selector subagent instructions and a context file example with the user by sending them as files (not just describing them in chat) so they appear in the output tab: send the `selector-tail-curve-ai-framework` and `selector-tail-curve-ai-open-ended` agent files under user-readable names ("Framework-based Selector Agent" and "Open-Ended Selector Agent"), plus one of the context files captured above (call it "AI Context Example: Tail"). This is to allow the user to review this for transparency while they wait for selections to finish.

- [ ] **Invoke the framework tail selector and the open-ended tail selector in parallel** (call both subagents in the same message, not one after the other). Each covers all measures in a single invocation:
  - Framework: call a general subagent following the spec at `selector-tail-curve-ai-framework` and pass the list of context file paths you captured from the script output. It will read each context file (one measure at a time), apply the tail curve decision framework, select the best curve METHOD (not tail factor) based on diagnostics, and write one JSON file per measure: `selections/agent-logic/tail-curve-ai-framework-<measure>.json`
  - Open-ended: call a general subagent following the spec at `selector-tail-curve-ai-open-ended` and pass the same list of context file paths. It will read each context file (one measure at a time), apply holistic actuarial judgment, and write one JSON file per measure: `selections/agent-logic/tail-curve-ai-open-ended-<measure>.json`
  
  Verify that one JSON file per measure was created for each selector. **Do NOT read the context files yourself** — the subagents will read them. **Do NOT read the JSON responses** — only verify the files were created. This keeps each selector's judgment independent: if you read the context or reasoning first, your own read on the data can leak into how you frame later steps and bias any selection stage toward agreeing with what you already concluded.

- [ ] Use bash cp to copy the `selector-tail-curve-ai-framework` and `selector-tail-curve-ai-open-ended` agent files into `selections/agent-logic/` so the selection logic that produced these JSON files is preserved alongside the output.

- [ ] Run `2e-tail-update-selections.py` to collect all per-measure JSON files and insert the selections into the Excel file. This script will:
  - Load all `selections/agent-logic/tail-curve-ai-framework-*.json` files and combine them
  - Load all `selections/agent-logic/tail-curve-ai-open-ended-*.json` files and combine them
  - Populate the **Framework AI Selection** row and **Open-Ended AI Selection** row in each sheet

- [ ] Tell the user where `selections/Chain Ladder Selections - Tail.xlsx` is located. Explain that both framework and open-ended AI selections (purple rows) are visible. The **Framework AI Selection** row shows the selected curve METHOD (e.g., 'bondy', 'exp_dev_quick') — this is what gets used to generate fitted LDFs in the Chain Ladder script. The user can override it manually. If the Framework AI Selection row is left blank, the Open-Ended AI Selection will be used as a fallback.

_(Pause for Selections/Selections Demo:)_
- [ ] Open `selections/Chain Ladder Selections - Tail.xlsx` for the user. Let them know they can review and override the tail curve method selections. Pause and wait for the user to confirm they are done reviewing before continuing.

- [ ] Update REPORT.md: search for `AI (Phase 5):` in the template and follow the fill instructions at each match.

- [ ] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

# Phase 6: Calculate Method Projections

- [ ] Run `2f-chainladder-ultimates.py`, `3-ie-ultimates.py`, and `4-bf-ultimates.py`. Debug any errors that occur. It is normal for IE and BF to get skipped if the user didn't provide the necessary data (exposure, initial expected). Note: `2f-chainladder-ultimates.py` will:
  1. Read empirical LDF selections from `selections/Chain Ladder Selections - LDFs.xlsx` (up to the cutoff age)
  2. Read the selected tail curve METHOD from `selections/Chain Ladder Selections - Tail.xlsx` (priority: User Selection → Framework AI → Open-Ended AI)
  3. Load curve parameters from `processed-data/tail-scenarios.csv`
  4. Generate fitted LDFs for ages beyond the cutoff using the selected curve method's formula
  5. Build complete CDFs by chaining empirical + fitted LDFs
  6. Calculate Chain Ladder ultimates and save to `processed-data/projected-ultimates.csv`

- [ ] Update REPORT.md: search for `AI (Phase 6)` in the template and follow the fill instructions at each match.

- [ ] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

# Phase 7: Ultimate Selections

- [ ] Run `scripts/5a-ultimates-create-excel.py` to create the ultimates workbook and export category context files. The script will create two sheets: **Losses** (combining Incurred and Paid) and **Counts** (combining Reported and Closed). It will print the context file paths it creates (e.g., "  Exported MD: selections/agent-logic/ultimates-context-loss.md", "  Exported MD: selections/agent-logic/ultimates-context-count.md"). **Capture the list of context file paths** from the script output.

- [ ] Before you call subagents, share the selector subagent instructions and a context file example with the user by sending them as files (not just describing them in chat) so they appear in the output tab: send the `selector-ultimates-ai-framework` and `selector-ultimates-ai-open-ended` agent files under user-readable names ("Framework-based Selector Agent" and "Open-Ended Selector Agent"), plus one of the context files captured above (call it "AI Context Example: Ultimates"). This is to allow the user to review this for transparency while they wait for selections to finish.

- [ ] **Invoke the framework ultimates selector and the open-ended ultimates selector in parallel** (call both subagents in the same message, not one after the other). Each covers both categories in a single invocation:
  - Framework: call a general subagent following the spec at `selector-ultimates-ai-framework` and pass the list of context file paths you captured from the script output. It will read each context file (loss, then count, one at a time), for each category choose ONE ultimate per accident year (selecting between Incurred/Paid for Loss, or Reported/Closed for Count), apply the structured method weighting framework, and write two JSON files: `selections/agent-logic/ultimates-ai-framework-loss.json` and `selections/agent-logic/ultimates-ai-framework-count.json`
  - Open-ended: call a general subagent following the spec at `selector-ultimates-ai-open-ended` and pass the same list of context file paths. It will read each context file (loss, then count, one at a time), for each category choose ONE ultimate per accident year, apply holistic actuarial judgment, and write two JSON files: `selections/agent-logic/ultimates-ai-open-ended-loss.json` and `selections/agent-logic/ultimates-ai-open-ended-count.json`
  
  Verify that two JSON files were created for each selector (one for Loss, one for Count). **Do NOT read the context files yourself** — the subagents will read them. **Do NOT read the JSON responses** — only verify the files were created. This keeps each selector's judgment independent: if you read the context or reasoning first, your own read on the data can leak into how you frame later steps and bias any selection stage toward agreeing with what you already concluded.

- [ ] Use bash cp to copy the `selector-ultimates-ai-framework` and `selector-ultimates-ai-open-ended` agent files into `selections/agent-logic/` so the selection logic that produced these JSON files is preserved alongside the output.

- [ ] Run `5b-ultimates-update-selections.py` to load the category JSON files and insert both framework and open-ended selections and reasoning into `selections/Ultimates.xlsx`. This script will:
  - Load `selections/agent-logic/ultimates-ai-framework-loss.json` and `selections/agent-logic/ultimates-ai-framework-count.json`
  - Load `selections/agent-logic/ultimates-ai-open-ended-loss.json` and `selections/agent-logic/ultimates-ai-open-ended-count.json`
  - Populate the Framework AI Selection and Open-Ended AI Selection columns in the Loss and Count sheets

- [ ] Tell the user where `selections/Ultimates.xlsx` is located. Explain that both framework and open-ended AI selections are visible. The framework selection is what gets used by default — the user can override it manually. The open-ended selection provides an independent cross-check. Note that the workbook now has **Losses** and **Counts** sheets instead of per-measure sheets, and one ultimate is selected per category per accident year.

_(Pause for Selections/Selections Demo:)_
- [ ] Open `selections/Ultimates.xlsx` for the user. Let them know they can review and override any AI ultimate selections. Pause and wait for the user to confirm they are done reviewing before continuing.

- [ ] Run `scripts/5c-summary-indications.py` to compute headline indications from the selected ultimates. This script reads `selections/Ultimates.xlsx` and outputs a formatted markdown table with total unpaid reserve, case reserves, and IBNR.

- [ ] **Update PROGRESS.md with headline indications:** Copy the markdown table output from `5c-summary-indications.py` into a "Headline Indications" section in PROGRESS.md.

- [ ] Send updated PROGRESS.md to the user.

- [ ] Update REPORT.md: search for `AI (Phase 7):` in the template and follow the fill instructions at each match.

- [ ] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

# Phase 8: Build Analysis Workbook

- [ ] Run `scripts/6-analysis-create-excel.py` and alert the user of the location and description of the final output files.

- [ ] Update REPORT.md: search for `AI (Phase 8):` in the template and follow the fill instructions at each match. Then do a final completeness pass: confirm pre-filled sections (LAE, trending, sensitivity) still say "Not implemented" or "Not applicable" and no bracketed placeholders remain.

- [ ] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

# Phase 9: Technical Review

- [ ] Run `scripts/7-tech-review.py` and alert the user of the results and where the output is saved to.

- [ ] Update REPORT.md: search for `AI (Phase 9):` in the template and follow the fill instructions at each match.

- [ ] Update REPLICATE.md and PROGRESS.md. Review next phase in PROGRESS.md. Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait.

# Phase 10: Summarize Final Outputs

Be explicit and exhaustive. The user should leave this step knowing exactly what was produced, where it lives, and what each file is for. Present the list below (adapted to what actually ran in this analysis — skip items that did not run, e.g., BF if it was skipped).

- [ ] After listing the files, tell the user the single most important takeaway: **REPORT.md is the primary narrative deliverable, and `Analysis.xlsx` is the primary numerical deliverable.** Everything else is supporting evidence or reproducibility material.

- [ ] Send updated REPORT.md, REPLICATE.md, and PROGRESS.md to the user as files so they can review them while they wait, as well as a .zip with all the project files.

- [ ] Provide the user a closing summary following the template at `assets/closing-summary.md`.

- [ ] Let the user know: If they'd like to continue with Peer Review, they should start a New Chat, upload the zip, and run `/peer-review` for an independent AI peer review of the completed analysis. Or, they can ask questions about the analysis or the workflow.

---
