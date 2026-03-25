**Interaction Level: Fully Automated** — Skip Selections Review. Claude runs everything end-to-end, including making AI selections, with no pauses.

# Step 1: Project Setup (Complete — 2026-03-25)
Goal: Set up the project structure and standard documents.
- [x] Copy PROGRESS.md to project root.
- [x] Install the Python packages in `requirements.txt` (used existing .venv).
- [x] Ask the user the level of interaction they would like. User chose: Fully Automated.
- [x] Data already present at `data/Claude Agent Triangles 5 Demo Data.xlsx`.

# Step 2: Exploratory Data Analysis (Complete — 2026-03-25)
Goal: Understand what data is available.
- [x] Review the files available using the explore-excel tool. Added file summary to PROJECT.md.
  - 3 sheets: Inc (Incurred Losses), Pd (Paid Losses), Count
  - 18 fiscal accident years: 2008-2025
  - 18 development ages: 15-219 months (annual intervals)
  - Prior Age-to-Age Selections row present in each sheet
- [x] Project metadata filled into PROJECT.md.

# Step 3: Add Steps for Each Reserving Method

## 3a Identify Methods (Complete — 2026-03-25)
- [x] Identified method: **Chain Ladder** — data is in triangle format with Incurred Losses, Paid Losses, and Count triangles.
- [x] Steps added below in section 3b.

## 3b Chain Ladder (In Progress — 2026-03-25)

- [X] Based on available data, determine which triangles we will use: Paid Losses, Incurred Losses, Count.
- [x] Prior selections exist — embedded as last row in each Excel sheet. Will read from Excel during data extraction.

### Data Extraction (One Time)

- [X] Copy all the python scripts from the reserve-methods's skill's chain-ladder assets to `output/chain-ladder/scripts`.
- [X] Modify the variables at the top of the file with the appropriate DATA_FILE_PATH, OUTPUT_PATH, and TEMPLATE_PATH.
- [X] Modify `1-prep-data.py` to accept the format of the data provided by the user.
- [X] Report to the user what LDF averages and metrics will be calculated and ask them if they'd like to add others.
- [X] Run all the other Python scripts to create output in output/chain-ladder.

### Make Actuarial Selections for LDFs

- [X] Create a JSON file to hold selections: `output/chain-ladder/selections/chain-ladder.json`.
- [ ] Task a single `chain-ladder-ldf-selector` subagent to make all selections (Fully Automated mode).
- [ ] Run `6-update-selections-excel.py` to insert the selections and reasoning into the Excel file.
- [ ] Delete `output/chain-ladder/selections/chain-ladder.json`.
- [ ] Open `output/chain-ladder/selections/Chain Ladder Selections.xlsx` for the user.
