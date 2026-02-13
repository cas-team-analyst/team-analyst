# Step 1: Project Setup
Goal: Set up the project structure and standard documents. 
- [ ] Copy PROGRESS.md to project root.
- [ ] Create folder structure: /data, /prior, output/processed, output/selections, output/scripts
- [ ] Set up .venv with `python -m venv .venv; .venv/Scripts/activate; pip install -r requirements.txt`
- [ ] Run `npm install` to install Node.js requirements
- [ ] Ask the user the level of interaction they would like: Careful (Frequent Pauses to Review Work), Quick First Pass (Only Stop to Make Selections), Fully Automated (Skip Selections Review) and note this at the top of PROGRESS.md.
- [ ] Ask user to copy relevant data files to data/

# Step 2: Exploratory Data Analysis
Goal: Understand what data is available. 
- [ ] Review the files available using the explore-excel tool. Create summaries and save them at `output/eda`
- [ ] Use the AskUserQuestions tool and the project context to fill in the information in the README section "Project Metadata."

# Step 3: Add Steps for Each Reserving Method

## 3a Identify Methods
- [ ] Identify reserving methods to consider. _For now, we only do Chain Ladder (Loss Development Method)._
- [ ] Add each method's progress steps below in sections 3b, 3c, etc. Progress steps are in the skills. Example: .claude\skills\chain-ladder-method\PROGRESS.MD.

