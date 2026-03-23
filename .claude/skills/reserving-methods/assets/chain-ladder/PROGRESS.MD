_Copy these steps into PROGRESS whenever a new method will be used. It applies only to the this asset folder's method._

- [ ] Based on available data, determine which triangles we will use to come up with Ultimates estimates from this method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc.

### Data Extraction (One Time)

- [ ] Copy all the python scripts from the reserve-methods's skill's chain-ladder assets (`skills/reserving-methods/assets/chain-ladder`) to `output/chain-ladder/scripts`.
- [ ] Modify the variables at the top of the file with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH.
- [ ] Modify `1-prep-data.py` to accept the format of the data provided by the user, and run it to verify it works and passes validation. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format. 
- [ ] Report to the user what LDF averages and metrics will be calculated and ask them if they'd like to add others.
- [ ] Run all the other Python scripts to create processed output.

### Make Actuarial Selections for LDFs

- [ ] Create a JSON file to hold selections: `selections/chain-ladder.json` with just "[]" for now.
- [ ] For each triangle measure and interval in `output/selections/Chain Ladder Selections.xlsx`, send only the data relevant to measure {measure name} and interval {interval} to the subagent "chain-ladder-ldf-selector". Use a new subagent for each combo so each selection is independent and focused. The subagent will return a selection. Add this factor reasoning used into `output/selections/chain-ladder.json` as a dict in the array with keys "method", "interval", "selection", "reasoning" (along with other selections). 
- [ ] Run `6-update-selections-excel.py` to insert the selections and reasoning into the Excel file.

### Get User Input On Selections

- [ ] Run these steps in a loop and only mark complete once the exit condition has been achieved.
  - Open `output/selections/Chain Ladder Selections.xlsx` for the user (or tell them where it is) and ask the user what changes they'd like to the selections.
  - Update `output/selections/chain-ladder.json` to make the appropriate edits.
  - Ask the user to close the Excel file if it is open (so you can edit it).
  - Run `6-update-selections-excel.py` to update excel from `output/selections/chain-ladder.json`.
  - Repeat until the user confirms there are no more changes necessary.
- [ ] Confirmed with user there are no more changes necessary.
