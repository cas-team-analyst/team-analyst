# Interaction Level: Careful (Frequent Pauses to Review Work)

# Step 1: Project Setup [Complete - 2026-03-22]
Goal: Set up the project structure and standard documents.
- [x] Copy PROGRESS.md to project root (use `cp` or `mv`, don't rewrite it yourself).
- [x] Install the Python packages in `requirements.txt` (check for a venv and use it if one exists).
- [x] Create folder structure: /data, output/processed, output/selections, output/scripts
- [x] Ask the user the level of interaction they would like: Careful (Frequent Pauses to Review Work), Selections Only (Only Stop to Make Selections), Fully Automated (Skip Selections Review) and note this at the top of PROGRESS.md (include the option label plus what it means).
- [x] Ask user to copy relevant data files to data/

# Step 2: Exploratory Data Analysis [Complete - 2026-03-22]
Goal: Understand what data is available.
- [x] Review the files available using the explore-excel tool. For each file add a file summary subsection to PROJECT.md.
- [x] Use the AskUserQuestions tool and the project context to fill in the information in the PROJECT section "Project Metadata." Fill in any missing context you need to perform the most valuable actuarial analysis.

# Step 3: Add Steps for Each Reserving Method

## 3a Identify Methods [Complete - 2026-03-22]
- [x] Identify reserving methods to consider. Available methods are in the reserving-methods skill. New methods can be added.
- [x] Add each method's progress steps below in sections 3b, 3c, etc. USE THE EXACT TEXT and copy with commands/tools (don't write them yourself) whenever possible. Progress steps are in the assets for the reserving-methods skill, in the method's folder. For example: `.claude/skills/reserving-methods/assets/chain-ladder/PROGRESS.md`.

## 3b Chain Ladder [In Progress - 2026-03-22]

- [x] Based on available data, determine which triangles we will use to come up with Ultimates estimates from this method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc.
  - Selected: Paid Losses and Incurred Losses

### Data Extraction (One Time)

- [x] Copy all the python scripts from the reserve-methods's skill's chain-ladder assets (`skills/reserving-methods/assets/chain-ladder`) to `output/chain-ladder/scripts`.
- [x] Modify the variables at the top of the file with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH.
- [x] Modify `1-prep-data.py` to accept the format of the data provided by the user, and run it to verify it works and passes validation. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format.
- [x] Report to the user what LDF averages and metrics will be calculated and ask them if they'd like to add others.
- [x] Run all the other Python scripts to create processed output.

### Make Actuarial Selections for LDFs

- [x] Create a JSON file to hold selections: `selections/chain-ladder.json` with just "[]" for now.
- [x] For each triangle measure and interval in `output/selections/Chain Ladder Selections.xlsx`, send only the data relevant to measure {measure name} and interval {interval} to the subagent "chain-ladder-ldf-selector". It will return a selection. Add this factor reasoning used into `output/selections/chain-ladder.json` as a dict in the array with keys "method", "interval", "selection", "reasoning" (along with other selections).
- [x] Run `6-update-selections-excel.py` to insert the selections and reasoning into the Excel file.

### Get User Input On Selections

- [ ] Run these steps in a loop and only mark complete once the exit condition has been achieved.
  - Open `output/selections/Chain Ladder Selections.xlsx` for the user (or tell them where it is) and ask the user what changes they'd like to the selections.
  - Update `output/selections/chain-ladder.json` to make the appropriate edits.
  - Ask the user to close the Excel file if it is open (so you can edit it).
  - Run `6-update-selections-excel.py` to update excel from `output/selections/chain-ladder.json`.
  - Repeat until the user confirms there are no more changes necessary.
- [ ] Confirmed with user there are no more changes necessary.
