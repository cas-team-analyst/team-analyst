# Step 1: Project Setup
Goal: Set up the project structure and standard documents. 
- [x] Copy PROGRESS.md to project root. (2024-12-30)
- [ ] Create folder structure: /data, /prior, output/processed, output/selections, output/scripts
- [ ] Set up .venv with `python -m venv .venv; .venv/Scripts/activate; pip install -r requirements.txt`
- [ ] Run `npm install` to install Node.js requirements
- [ ] Ask user to copy relevant data files to data/

# Step 2: Exploratory Data Analysis
Goal: Understand what data is available. 
- [ ] Review the files available using the explore-excel tool. Create summaries and save them at `output/eda`
- [ ] Use the AskUserQuestions tool and the project context to fill in the information in the README section "Project Metadata."

# Step 3: Add Steps for Each Reserving Method

## 3a Identify Methods
- [ ] Identify reserving methods to consider. _For now, we only do Chain Ladder (Loss Development Method)._
- [ ] Add each method's progress steps below in sections 3b, 3c, etc. Progress steps are in the skills. Example: .claude\skills\chain-ladder-method\PROGRESS.MD.

## Technical Issues Resolved

### Chain Ladder Method Skill Simplification (2024-12-30)
- [x] Complete: Simplified chain-ladder-method skill structure from 9 files to 6 files
- [x] Complete: Converted from JSON to CSV format for triangle data and selections  
- [x] Complete: Removed ActuarialTriangle class abstraction - now uses pandas DataFrames directly
- [x] Complete: Fixed ActuarialTriangle references causing import errors in chain_ladder_functions.py
- [x] Complete: Updated template_extraction.py and populate_selections.py for DataFrame workflow
- [x] Complete: Consolidated documentation into single SKILL.md file
- [x] Complete: Removed YAML file dependency - embedded diagnostics configuration in Python dictionary (2024-12-30)
