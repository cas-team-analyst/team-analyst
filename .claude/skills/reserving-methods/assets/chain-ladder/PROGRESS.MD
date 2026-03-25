_Copy these steps into PROGRESS whenever a new method will be used. It applies only to the this asset folder's method._

- [ ] Based on available data, determine which triangles we will use to come up with Ultimates estimates from this method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc.
- [ ] **OPTIONAL:** If you haven't already found prior selections, ask the user if prior LDF selections exist from a previous analysis. If they do, ask where they are located (Excel file, CSV, database, etc.). You will need to modify `read_and_process_prior_selections()` in `1-prep-data.py` to read from that source during data extraction.

### Data Extraction (One Time)

- [ ] Copy all the python scripts from the reserve-methods's skill's chain-ladder assets (`skills/reserving-methods/assets/chain-ladder`) to `output/chain-ladder/scripts`.
- [ ] Modify the variables at the top of the file with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH.
- [ ] Modify `1-prep-data.py` to accept the format of the data provided by the user. This includes:
  - Customizing `read_and_process_triangles()` to read triangle data from your source
  - If prior selections exist, customizing `read_and_process_prior_selections()` to read from your source.
  - Run it to verify it works and passes validation. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format. 
- [ ] Report to the user what LDF averages and metrics will be calculated and ask them if they'd like to add others.
- [ ] Run all the other Python scripts to create output in output/chain-ladder.

### Make Actuarial Selections for LDFs

- [ ] Create a JSON file to hold selections: `output/chain-ladder/selections/chain-ladder.json` with just "[]" for now.
- [ ] Ask the user if they would like AI to (A) make selections all at once (faster, fewer tokens) or (B) make each selection independently (slower, will use many more tokens, better selections expected but NOT RECOMMENDED for now, needs more testing as it will eat up your usage in minutes). Use this exact language when you ask the user. 

_If running each independently:_
- [ ] For each triangle measure and interval in `output/chain-ladder/selections/Chain Ladder Selections.xlsx`, send only the data relevant to measure {measure name} and interval {interval} to the subagent `chain-ladder-ldf-selector`. Use a new subagent for each combo so each selection is independent and focused. So if there are 2 measures (paid/incurred) and 10 intervales (6-12, 12-18, etc.) then you should run 2*10 = 20 subagents in parallel. The subagent will return a selection. Add this factor reasoning used into `output/chain-ladder/selections/chain-ladder.json` as a dict/object/map in the array with keys "measure", "interval", "selection", "reasoning" (along with other selections). 
_else:_
- [ ] Task a single `chain-ladder-ldf-selector` subagent to: Review `output/chain-ladder/selections/Chain Ladder Selections.xlsx` in full (NOT the files at `output/chain-ladder/data`), use this information to make actuarial LDF selections for each combination of Chain Ladder measure and interval, and add the selections and specific reasoning for each selection to `output/chain-ladder/selections/chain-ladder.json`, each as a dict/object/map in the array with keys "measure", "interval", "selection", "reasoning" (along with other selections). 
_end if_

- [ ] Run `6-update-selections-excel.py` to insert the selections and reasoning into the Excel file.
- [ ] Delete `output/chain-ladder/selections/chain-ladder.json` as the new source of truth will be `output/chain-ladder/selections/Chain Ladder Selections.xlsx`
- [ ] Open `output/chain-ladder/selections/Chain Ladder Selections.xlsx` for the user (or tell them where it is). It is now ready for them to override the AI selections.
