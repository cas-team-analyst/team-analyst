_Copy these steps into PROGRESS whenever a new method will be used. It applies only to the this asset folder's method._

- [ ] Based on available data, determine which triangles we will use to come up with Ultimates estimates from this method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc.

## Data Extraction (One Time)

- [ ] Copy all the python scripts from the reserve-methods's skill's chain-ladder assets (`skills/reserving-methods/assets/chain-ladder`) to `output/chain-ladder/scripts`.
- [ ] Modify the variables at the top of the file with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH.
- [ ] Modify `1-prep-data.py` to accept the format of the data provided by the user, and run it to verify it works and passes validation. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format. 
- [ ] Report to the user what LDF averages and metrics will be calculated and ask them if they'd like to add others.
- [ ] Run all the other Python scripts to create processed output.

---

## Before Making Actuarial Selections, Bring Relevant Data Together

- [ ] Preview 2_chainladder_enhanced_data.parquet, 3_chainladder_diagnostics.parquet, and 4_chainladder_ldf_averages.parquet to understand the data structure.
- [ ] Create an excel file that contains the one sheet per triangle with each sheet containing from top to bottom: a triangle of the measurement (filter by measure, cols = ages, rows = periods, cells = value from 2_chainladder_enhanced_data), a triangle of LDFs (cols = intervals, rows = periods, cells = ldf from 2_chainladder_enhanced_data.parquet), all the diagnostics triangles (cols = age, rows = period, cells = 1 triangle for each other column from 3_chainladder_diagnostics), the various cv/slope/averages (cols = interval, 1 row per additional column from 4_chainladder_ldf_averages), and below it recommended LDF selections (cols = interval, rows = selection/reasoning, cells = blank for now). This should be relatively simple to create by extracting data directly from the files. Save the file as `output/selections/Chain Ladder Selections.xlsx`.

## Make Actuarial Selections for LDFs

- [ ] Create a JSON file to hold selections: selections/chain-ladder.json with just "[]" for now.
- [ ] Replace this step with many steps, one for each triangle measure and interval in `Chain Ladder Selections.xlsx`, each step being: "Read only the data relevant to measure {measure name} and interval {interval} and apply the selection logic from assets > chain-ladder > SELECTION-LOGIC-REFERENCE.md from the reserving-methods skill to select an LDF factor. Note this factor and the specific logic used into selections/chain-ladder.json as a dict in the array with keys "method", "interval", "selection", "reasoning" (along with other selections).
- [ ] Insert the selections and reasoning into the Excel file where we added the blank cells.

## Get User Input On Selections

**!! Ignore these steps, they aren't finished yet.**

_For each triangle identified, copy the steps below into PROGRESS (a full copy of the steps for each triangle) and then work through them one at a time. Triangles are things like Incurred Loss, Paid Loss, Reported Count, Closed Count._

**Triangle: [NAME]**
Don't continue with the next triangle until this one is finished.

### 1. User Reviews Report in Browser
- [ ] Run these steps in a loop and only mark complete once the exit condition has been achieved.
  - Open the file for the user (or tell them where it is) and ask the user what changes they'd like to the selections. If they ask you questions about the report, you can find the report data at `output/reports/[triangle_name]_report.json`.
  - Create or update `selection-overrides.json` to make the appropriate edits.
  - Ask the user to close the Excel file if it is open (so you can edit it).
  - Rerun `5-selections.py`, `6-project-ultimates.py`, and `7-update-json.py` which will read in overrides, update the json. 
  - Update the Excel file with the new data.
  - Repeat until the user confirms there are no more changes necessary.
- [ ] Confirmed with user there are no more changes necessary.
