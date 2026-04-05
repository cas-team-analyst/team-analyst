# Step 1: Project Setup
Goal: Set up the project structure and standard documents.
- [ ] Copy markdown files from assets to the project folder (use `cp` or `mv`, don't rewrite it yourself): PROGRESS, REPLICATE, REPORT.
- [ ] Install the Python packages in `requirements.txt`.
- [ ] Ask the user the level of interaction they would like: Careful (Frequent Pauses to Review Work), Selections Only (Only Stop to Make Selections), Fully Automated (Skip Selections Review). Use these exact descriptions and don't recommend one of them. Note the user's choice at the top of PROGRESS.md (include the option label plus what it means).
- [ ] Create folders `raw-data/`, `processed-data/`, `selections/`, `scripts/`, and `ultimates/` in the project folder and ask the user to copy relevant data files into the raw-data folder.

# Step 2: Exploratory Data Analysis
Goal: Understand what data is available.
- [ ] Review the files available using the explore-excel in the reserving-analysis skill scripts. For each file add a file summary subsection to REPORT.md in the data section.

# Step 3: Data Intake

- [ ] Copy all the numbered python scripts from the reserving-analysis skill scripts folder to `scripts/` (use `cp` or `mv`, don't rewrite it yourself): 1a-prep-data.py through 2b-chainladder-update-selections.py.
- [ ] Based on available data, determine which triangles we will use to come up with Ultimates estimates using the Chain Ladder method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc.
- [ ] If you haven't already found prior selections, ask the user if prior LDF selections exist from a previous analysis. If they do, ask where they are located (Excel file, CSV, database, etc.). You will need to modify `read_and_process_prior_selections()` in `1a-prep-data.py` to read from that source during data extraction.
- [ ] If you haven't already found an input file with Expected Loss Rates (containing period, expected loss rate, and expected frequency), ask the user if this file exists and to place it in the raw-data folder. Without this file, we won't be able to use the Initial Expected or Bornhuetter-Ferguson methods.
- [ ] Modify the variables at the top of each script with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH.
- [ ] Modify `1a-prep-data.py` to accept the format of the data provided by the user. This includes:
  - Customizing `read_and_process_triangles()` to read triangle data from your source
  - If prior selections exist, customizing `read_and_process_prior_selections()` to read from your source.
  - Run it to verify it works and passes validation. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format. 
- [ ] Report to the user what LDF averages (review `1d-averages-qa.py`) and metrics will be calculated and ask them if they'd like to add others.
- [ ] Run all the other Python scripts to create output in `processed-data/`.

### Chain Ladder: Actuarial LDF Selections

- [ ] Tell the user: "I'm about to apply the base selection logic framework to make LDF selections. This framework includes 14 selection criteria and 10 diagnostic adjustment rules. If you'd like to explore these in detail, you can use `/selection-logic` in a separate session or after this analysis is complete — using it here would interrupt the current workflow."
- [ ] Create a JSON file to hold selections: `selections/chain-ladder.json` with just "[]" for now.
- [ ] Ask the user if they would like AI to (A) make selections all at once (faster, fewer tokens) or (B) make each selection independently (slower, will use many more tokens, better selections expected but NOT RECOMMENDED for now, needs more testing as it will eat up your usage in minutes). Use this exact language when you ask the user. 

_If running each independently:_
- [ ] For each triangle measure and interval in `selections/Chain Ladder Selections.xlsx`, send only the data relevant to measure {measure name} and interval {interval} to the subagent `chain-ladder-ldf-selector`. Use a new subagent for each combo so each selection is independent and focused. So if there are 2 measures (paid/incurred) and 10 intervales (6-12, 12-18, etc.) then you should run 2*10 = 20 subagents in parallel. The subagent will return a selection. Add this factor reasoning used into `output/chain-ladder/selections/chain-ladder.json` as a dict/object/map in the array with keys "measure", "interval", "selection", "reasoning" (along with other selections).
- [ ] Also run one tail factor subagent per measure. For tail selection, send: the averages and CVs from the last two development intervals (so the agent can judge the level of remaining development), the late-maturity diagnostics (open_counts, claim_closure_rate, paid_to_incurred, average_case_reserve), and the prior tail selection if one exists. Use interval `"Tail"` in the JSON output.
_else:_
- [ ] Task a single `selector-chain-ladder-ldf` subagent to: Review `selections/Chain Ladder Selections.xlsx` in full (NOT the files at `processed-data`), use this information to make actuarial LDF selections for each combination of Chain Ladder measure and interval **including a tail factor (interval "Tail") for each measure**, and add the selections and specific reasoning for each selection to `selections/chain-ladder.json`, each as a dict/object/map in the array with keys "measure", "interval", "selection", "reasoning" (along with other selections).
_end if_

- [ ] Run `2b-chainladder-update-selections.py` to insert the selections and reasoning into the Excel file.
- [ ] Open `selections/Chain Ladder Selections.xlsx` for the user (or tell them where it is). It is now ready for them to override the AI selections.
- [ ] Confirm the user has made selections and is ready to continue.

### Run Methods That Don't Require Selections

- [ ] Run `2c-chainladder-ultimates.py`, `3-ie-ultimates.py`, and `4-bf-ultimates.py`. Debug any errors that occur.


