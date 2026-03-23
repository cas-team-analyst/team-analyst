_Copy these steps into PROGRESS whenever a new method will be used. It applies only to the this asset folder's method._

- [ ] Based on available data, determine which triangles we will use to come up with Ultimates estimates from this method: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc.

## Data Extraction (One Time)

- [ ] Copy all the python scripts, and `report.html`, from the reserve-methods's skill's chain-ladder assets (`skills/reserving-methods/assets/chain-ladder`) to `output/scripts` and `output/reports`, respectively.
- [ ] Modify the variables at the top of the file with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH.
- [ ] Modify `1-prep-data.py` to accept the format of the data provided by the user. Only mark this step complete once the tests in the script have passed to verify the output is in the necessary format. 
- [ ] Report to the user what LDF averages and metrics will be calculated and ask them if they'd like to add others.
- [ ] Run all the other scripts to create processed output.

---

## Get User Input On Selections

_For each triangle identified, copy these steps into PROGRESS (a full copy of the steps for each triangle) and then work through them one at a time. Triangles are things like Incurred Loss, Paid Loss, Reported Count, Closed Count._

**Triangle: [NAME]**
Don't continue with the next triangle until this one is finished.

### 1. User Reviews Report in Browser
- [ ] Start Vite dev server from project root: `npx vite --port 5175`
- [ ] Open: http://localhost:5175/output/reports/[triangle_name]_report.html. triangle_name might be "incurred_loss", "paid_loss", "reported_count", "closed_count".
- [ ] Run these steps in a loop and only mark complete once the exit condition has been achieved.
  - Ask the user what changes they'd like to the selections. If they ask you questions about the report, you can find the report data at `output/reports/[triangle_name]_report.json`.
  - Create or update `selection-overrides.json` to make the appropriate edits.
  - Rerun `5-selections.py`, `6-project-ultimates.py`, and `7-update-report.py` which will read in overrides, update the report, then Vite will see the file changed and refresh the report automatically. 
  - Repeat until the user confirms there are no more changes necessary.
- [ ] Confirmed with user there are no more changes necessary.
- [ ] Close Vite server.
