# Step 1: Project Setup
Goal: Set up the project structure and standard documents.
- [ ] Copy PROGRESS.md to project root (use `cp` or `mv`, don't rewrite it yourself).
- [ ] Install the Python packages in `requirements.txt` (check for a venv and use it if one exists).
- [ ] Ask the user the level of interaction they would like: Careful (Frequent Pauses to Review Work), Selections Only (Only Stop to Make Selections), Fully Automated (Skip Selections Review). Use these exact descriptions and don't recommend one of them. Note the user's choice at the top of PROGRESS.md (include the option label plus what it means).
- [ ] Create a root folder `data/` and ask the user to copy relevant data files into the folder.

# Step 2: Exploratory Data Analysis
Goal: Understand what data is available.
- [ ] Review the files available using the explore-excel tool. For each file add a file summary subsection to PROJECT.md.
- [ ] Use the AskUserQuestions tool and the project context to fill in the information in the PROJECT section "Project Metadata." Fill in any missing context you need to perform the most valuable actuarial analysis. 

# Step 3: Add Steps for Each Reserving Method

## 3a Identify Methods
- [ ] Identify reserving methods to consider. Available methods are in the reserving-methods skill. New methods can be added.
- [ ] Add each method's progress steps below in sections 3b, 3c, etc. USE THE EXACT TEXT and copy with commands/tools (don't write them yourself) whenever possible. Progress steps are in the assets for the reserving-methods skill, in the method's folder. For example: `.claude/skills/reserving-methods/assets/chain-ladder/PROGRESS.md`.

