# Current Status

*Add current step and status here.*

# Step 1: Project Setup
Goal: Set up the project structure and standard documents. 
- [ ] Copy PROGRESS.md to project root.
- [ ] Create folder structure: /data, /analysis, /selections, /output, /prior
- [ ] Ask user to copy relevant data files to data/
- [ ] Ask user to copy the README from the prior analysis into /prior

# Step 2: Data Gathering
Goal: Understand the necessary inputs and outputs.
At this point, data may not be in the exact format we need, but the building blocks will need to be there by the end of this step.

## 2a Identify Data Requirements
- [ ] Copy relevant content from prior README.md if it exists
- [ ] Identify reserving methods to consider.
*By default, we consider Chain Ladder (Loss Development Method), Bornhuetter-Ferguson Method. Each will be duplicated for Paid, Incurred, Reported, Closed depending on available data. Other potential methods: Cape Cod Method, Expected Loss Ratio Method, Frequency/Severity*
- [ ] Add a step for each method under step 3 and 4.
- [ ] If there is not already a skill for a reserving method, create one using the `create-reserving-method-skill` skill. 
- [ ] Note data requirements in README.md
- [ ] Add a step below for each data requirement.

## 2b Data Confirmation and Preprocessing
For each below, identify and document the data source at README.md. If a source is missing, identify a workaround or mark it as excluded (this may mean we need to exclude a related method).
For excel files, document what sheets exist and add short notes about what each sheet contains.
- [ ] Large Loss Details (threshold: $[amount] or a file of large losses to cap or exclude)
- [ ] Historical Trend Factors
- [ ] Industry Benchmarks
- [ ] Other: [Specify]

# Step 3: Process Data
- [ ] Write and run a script to transform the raw data into a format readily usable by reserving method skill: [Method Skill Name Here]. 
- [ ] Make and document initial selections for reserving method skill: [Method Skill Name Here]. 
- [ ] Create 3 alternative selections and include reasons a different choice might be made. 

Scripts should read from `./data/` and save to `./data/processed/`.
Selections should be saved at ./selections/{method skill name}.md

# Step 4: User Selections: Methods
- [ ] Show the user the selections and alternatives and highlight any that definitely need review for method skill: [Method Skill Name Here]
- [ ] Ask if they want to override any selections for method skill: [Method Skill Name Here]

# Step 5: Method Weights
- [ ] Recommend weights for each period and method so we can take a weighted average of ultimates from each method, using different weights for different periods.
- [ ] Ask the user if they want to override any selections for the weights. 

# Step 6: Final Overrides
- [ ] Ask the user if they want to override any of the weighted averages.

# Step 7: TODO
At this point, ask the user what they'd like to do next. 
