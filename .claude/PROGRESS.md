# Step 1: Project Setup
Goal: Set up the project structure and standard documents. 
- [ ] Copy PROGRESS.md to project root.
- [ ] Create folder structure: /data, /prior, output/processed, output/selections, output/scripts
- [ ] Set up .venv with `python -m venv .venv; .venv/Scripts/activate; pip install -r requirements.txt`
- [ ] Ask user to copy relevant data files to data/
- [ ] Use the AskUserQuestions tool and the project context to fill in the information in the README section "Project Metadata."

# Step 2: Exploratory Data Analysis
Goal: Understand what data is available. 
- [ ] Review the files available using the explore-excel tool. Create summaries and save them at `output/eda`

# Step 3: Add Steps for Each Reserving Method

## 2a Identify Methods
- [ ] Identify reserving methods to consider. _For now, we only do Chain Ladder (Loss Development Method)._
- [ ] Add each method's progress steps below in sections 2b, 2c, etc. Progress steps are in the skills. Example: .claude\skills\chain-ladder-method\PROGRESS.MD.

