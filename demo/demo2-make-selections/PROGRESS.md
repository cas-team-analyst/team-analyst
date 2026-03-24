**Interaction Mode: Careful (Frequent Pauses to Review Work)**

# Step 1: Project Setup
Goal: Set up the project structure and standard documents.
- [x] Copy PROGRESS.md to project root (use `cp` or `mv`, don't rewrite it yourself). - 2026-03-24
- [x] Install the Python packages in `requirements.txt` (check for a venv and use it if one exists). - 2026-03-24 (packages already installed)
- [x] Ask the user the level of interaction they would like: Careful (Frequent Pauses to Review Work), Selections Only (Only Stop to Make Selections), Fully Automated (Skip Selections Review). Use these exact descriptions and don't recommend one of them. Note the user's choice at the top of PROGRESS.md (include the option label plus what it means). - 2026-03-24 (Careful)
- [x] Create a root folder `data/` and ask the user to copy relevant data files into the folder. - 2026-03-24 (data/ folder already exists with Triangle Examples 1.xlsx)

# Step 2: Exploratory Data Analysis
Goal: Understand what data is available.
- [x] Review the files available using the explore-excel tool. For each file add a file summary subsection to PROJECT.md. - 2026-03-24
- [x] Use the AskUserQuestions tool and the project context to fill in the information in the PROJECT section "Project Metadata." Fill in any missing context you need to perform the most valuable actuarial analysis. - 2026-03-24

# Step 3: Add Steps for Each Reserving Method

## 3a Identify Methods
- [x] Identify reserving methods to consider. Available methods are in the reserving-methods skill. New methods can be added. - 2026-03-24 (Chain Ladder)
- [x] Add each method's progress steps below in sections 3b, 3c, etc. USE THE EXACT TEXT and copy with commands/tools (don't write them yourself) whenever possible. Progress steps are in the assets for the reserving-methods skill, in the method's folder. For example: `.claude/skills/reserving-methods/assets/chain-ladder/PROGRESS.md`. - 2026-03-24

## 3b Chain Ladder

- [x] Based on available data, determine which triangles we will use to come up with Ultimates estimates from this method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc. - 2026-03-24 (Paid Losses, Incurred Losses, Claim Counts)

### Data Extraction (One Time)

- [x] Copy all the python scripts from the reserve-methods's skill's chain-ladder assets (`skills/reserving-methods/assets/chain-ladder`) to `output/chain-ladder/scripts`. - 2026-03-24
- [x] Modify the variables at the top of the file with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH. - 2026-03-24 (no template needed; updated DATA_FILE_PATH, set DATA_FILE, fixed header_row for Inc 1/Paid 1 to 2, Ct 1 to 1)
- [x] Modify `1-prep-data.py` to accept the format of the data provided by the user, and run it to verify it works and passes validation. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format. - 2026-03-24 (validation passed: 900 rows, 3 measures)
- [x] Report to the user what LDF averages and metrics will be calculated and ask them if they'd like to add others. - 2026-03-24 (user confirmed no additions needed)
- [x] Run all the other Python scripts to create output in output/chain-ladder. - 2026-03-24 (scripts 2-5 all ran successfully)

### Make Actuarial Selections for LDFs

- [ ] Create a JSON file to hold selections: `output/chain-ladder/selections/chain-ladder.json` with just "[]" for now. - 2026-03-24
- [ ] Ask the user if they would like AI to (A) make selections all at once (faster, fewer tokens) or (B) make each selection independently (slower, will use many more tokens, better selections expected but NOT RECOMMENDED for now, needs more testing as it will eat up your usage in minutes). Use this exact language when you ask the user.

_If running each independently:_
- [ ] For each triangle measure and interval in `output/chain-ladder/selections/Chain Ladder Selections.xlsx`, send only the data relevant to measure {measure name} and interval {interval} to the subagent `chain-ladder-ldf-selector`. Use a new subagent for each combo so each selection is independent and focused. So if there are 2 measures (paid/incurred) and 10 intervales (6-12, 12-18, etc.) then you should run 2*10 = 20 subagents in parallel. The subagent will return a selection. Add this factor reasoning used into `output/chain-ladder/selections/chain-ladder.json` as a dict/object/map in the array with keys "measure", "interval", "selection", "reasoning" (along with other selections).
_else:_
- [ ] Task a single `chain-ladder-ldf-selector` subagent to: Review `output/chain-ladder/selections/Chain Ladder Selections.xlsx` in full (NOT the files at `output/chain-ladder/data`), use this information to make actuarial LDF selections for each combination of Chain Ladder measure and interval, and add the selections and specific reasoning for each selection to `output/chain-ladder/selections/chain-ladder.json`, each as a dict/object/map in the array with keys "measure", "interval", "selection", "reasoning" (along with other selections).
_end if_

- [ ] Run `6-update-selections-excel.py` to insert the selections and reasoning into the Excel file.
- [ ] Delete `output/chain-ladder/selections/chain-ladder.json` as the new source of truth will be `output/chain-ladder/selections/Chain Ladder Selections.xlsx`
- [ ] Open `output/chain-ladder/selections/Chain Ladder Selections.xlsx` for the user (or tell them where it is). It is now ready for them to override the AI selections.


