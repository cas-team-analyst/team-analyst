User Interaction Level: Careful (Frequent Pauses to Review Work)

# Step 1: Project Setup
Goal: Set up the project structure and standard documents.
- [x] Copy markdown files from assets to the project folder (use `cp` or `mv`, don't rewrite it yourself): PROGRESS, REPLICATE, REPORT. (Completed 2026-04-06)
- [x] Install the Python packages in `requirements.txt`. (Completed 2026-04-06)
- [x] Ask the user the level of interaction they would like: Careful (Frequent Pauses to Review Work), Selections Only (Only Stop to Make Selections), Fully Automated (Skip Selections Review). Use these exact descriptions and don't recommend one of them. Note the user's choice at the top of PROGRESS.md (include the option label plus what it means). (Completed 2026-04-06)
- [x] Create folders `raw-data/`, `processed-data/`, `selections/`, `scripts/`, and `ultimates/` in the project folder and ask the user to copy relevant data files into the raw-data folder. (Completed 2026-04-06)

# Step 2: Exploratory Data Analysis
Goal: Understand what data is available.
- [x] Review the files available using the explore-excel in the reserving-analysis skill scripts. For each file add a file summary subsection to REPORT.md in the data section. (Completed 2026-04-06)

# Step 3: Data Intake

- [x] Copy all the numbered python scripts from the reserving-analysis skill scripts folder to `scripts/` (use `cp` or `mv`, don't rewrite it yourself): 1a-prep-data.py through 2b-chainladder-update-selections.py. (Completed 2026-04-06)
- [x] Based on available data, determine which triangles we will use to come up with Ultimates estimates using the Chain Ladder method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc. (Completed 2026-04-06)
- [x] If you haven't already found prior selections, ask the user if prior LDF selections exist from a previous analysis. If they do, ask where they are located (Excel file, CSV, database, etc.). You will need to modify `read_and_process_prior_selections()` in `1a-prep-data.py` to read from that source during data extraction. (Completed 2026-04-06: None exist)
- [x] If you haven't already found an input file with Expected Loss Rates (containing period, expected loss rate, and expected frequency), ask the user if this file exists and to place it in the raw-data folder. Without this file, we won't be able to use the Initial Expected or Bornhuetter-Ferguson methods. (Completed 2026-04-06)
- [x] Modify the variables at the top of each script with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH. (Completed 2026-04-06)
- [x] Modify `1a-prep-data.py` to accept the format of the data provided by the user. This includes:
  - Customizing `read_and_process_triangles()` to read triangle data from your source
  - If prior selections exist, customizing `read_and_process_prior_selections()` to read from your source.
  - Run it to verify it works and passes validation. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format. (Completed 2026-04-06) 
- [x] Report to the user what LDF averages (review `1d-averages-qa.py`) and metrics will be calculated and ask them if they'd like to add others. (Completed 2026-04-06)
- [x] Run all the other Python scripts to create output in `processed-data/`. (Completed 2026-04-06)

# Step 4: Actuarial Selections: Chain Ladder LDFs

- [/] Tell the user: "I'm about to apply the base selection logic framework to make LDF selections. This framework includes 14 selection criteria and 10 diagnostic adjustment rules. If you'd like to explore these in detail, you can use `/selection-logic` in a separate session or after this analysis is complete — using it here would interrupt the current workflow." (Started 2026-04-06)
- [x] Create a JSON file to hold selections: `selections/chain-ladder.json` with just "[]" for now. (Completed 2026-04-06)
- [/] Ask the user if they would like AI to (A) make selections all at once (faster, fewer tokens) or (B) make each selection independently (slower, will use many more tokens, better selections expected but NOT RECOMMENDED for now, needs more testing as it will eat up your usage in minutes). Use this exact language when you ask the user. (Started 2026-04-06) 

_If running each independently:_
- [ ] For each triangle measure and interval in `selections/Chain Ladder Selections.xlsx`, send only the data relevant to measure {measure name} and interval {interval} to the subagent `selector-chain-ladder-ldf`. Use a new subagent for each combo so each selection is independent and focused. So if there are 2 measures (paid/incurred) and 10 intervales (6-12, 12-18, etc.) then you should run 2*10 = 20 subagents in parallel. The subagent will return a selection. Add this factor reasoning used into `selections/chain-ladder.json` as a dict/object/map in the array with keys "measure", "interval", "selection", "reasoning" (along with other selections).
_else:_
- [ ] Task a single `selector-chain-ladder-ldf` subagent to: Review `selections/Chain Ladder Selections.xlsx` in full (NOT the files at `processed-data`), use this information to make actuarial LDF selections for each combination of Chain Ladder measure and interval **including a tail factor (interval "Tail") for each measure**, and add the selections and specific reasoning for each selection to `selections/chain-ladder.json`, each as a dict/object/map in the array with keys "measure", "interval", "selection", "reasoning" (along with other selections).
_end if_

- [ ] Run `2b-chainladder-update-selections.py` to insert the selections and reasoning into the Excel file.
- [ ] Open `selections/Chain Ladder Selections.xlsx` for the user (or tell them where it is). It is now ready for them to override the AI selections.
- [ ] Confirm the user has made selections and is ready to continue.

# Step 5: Run Methods That Don't Require Selections

- [ ] Run `2c-chainladder-ultimates.py`, `3-ie-ultimates.py`, and `4-bf-ultimates.py`. Debug any errors that occur.

# Step 6: Actuarial Selections: Ultimates

- [ ] Create an Excel worksheet at `selections/Ultimates.xlsx` with the context needed to select Ultimates using the available methods. Leave blank space for the selections (we'll select ultimates in the next step). Create a script for this at `scripts/5a-ultimates-create-excel.py`. Use `scripts/2a-chainladder-create-excel.py` as a guide for format.
- [ ] Create a script at `scripts/5b-ultimates-update-selections.py` that reads `selections/ultimates.json` and updates `selections/Ultimates.xlsx` with selections and reasoning. Use `scripts/2b-chainladder-update-selections.py` as a guide for format.
- [ ] Task a selector-ultimates subagent to make ultimates selections. Use a different subagent for each measure. Read the excel file and give them the context for the specific measure, and they'll return JSON which you should save to `selections/ultimates.json`.
- [ ] Task a single `selector-ultimates` subagent to: Review `selections/Ultimates.xlsx` in full (NOT the files at `processed-data`), use this information to make actuarial ultimate selections for each combination of Chain Ladder measure and period, and add the selections and specific reasoning for each selection to `selections/ultimates.json`, each as a dict/object/map in the array with keys "measure", "period", "selection", "reasoning" (along with other selections).
- [ ] Run `5b-ultimates-update-selections.py` to insert the selections and reasoning into `selections/Ultimates.xlsx`.

# Step 7: Build Complete Analysis Output

- [ ] Run `scripts/6-complete-analysis.py` and alert the user of the location and description of the final output files. 
- [ ] Run `scripts/7-tech-review.py` and alert the user of the results and where the output is saved to.

# Step 8: Suggest Peer Review

- [ ] Suggest to the user that they get a Peer Review of the results. If they would like TeamAnalyst to do this, they should close the current workflow (this will clear context to get an independent review) and use the /peer-review skill to get a AI Peer Review.

