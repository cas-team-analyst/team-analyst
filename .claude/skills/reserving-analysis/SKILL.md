---
name: reserving-analysis
description: Main skill. Use when asked to work on a reserving analysis project. Do NOT use for peer review, there is a separate skill for that.
---

# WELCOME

When the user first triggers this skill, present the following message:

```
Reserving Analysis — TeamAnalyst Plugin

This workflow walks you through a full actuarial reserving analysis:

1. Project Setup — set up folders, install dependencies, choose interaction mode
2. Exploratory Data Analysis — review and summarize your data files
3. Data Intake — prepare triangles, calculate LDF averages and diagnostics
4. Chain Ladder Selections — AI-assisted LDF selections with actuarial judgment
5. Run Methods — project ultimates using Chain Ladder, Initial Expected, and BF
6. Ultimate Selections — select final ultimates across methods

Note: The Initial Expected method requires an Expected Loss Rate input file
(period, expected loss rate, expected frequency) and exposure data. The
Bornhuetter-Ferguson method builds on both Chain Ladder and Initial Expected
results — if IE can't run, BF will be skipped automatically. Chain Ladder
always runs. You'll be asked about your available data during data intake.

Interaction modes:
- Pause for Selections: pauses after LDF selections and after ultimate selections for your review
- Fully Automatic: runs start to finish with no pauses (except to confirm data format)

Three standard documents will be created in your project folder and filled in
as the analysis progresses:
- REPORT.md — the primary deliverable: a structured actuarial report
  (purpose, scope, data, methodology, assumptions, results, diagnostics,
  uncertainty, ASOP self-check). This is what you share with reviewers.
- PROGRESS.md — a running checklist of the workflow: which steps are done,
  in progress, and what scripts were produced along the way.
- REPLICATE.md — a reproducibility log so someone without AI assistance
  can follow the steps and arrive at the same results.

Throughout the workflow, keep the user you'll be kept informed of what is happening and why.
```

Then ask the user to identify the folder where they'd like to conduct this analysis. This should be an existing folder that contains (or will contain) their triangle data. Do not create a new folder in an arbitrary location. Once the user has confirmed the folder, proceed with the main operation flow below.

# MAIN OPERATION FLOW

Always follow these steps when working on this project:

If a file named PROGRESS.md does not already exist in the project directory: copy this skill's `PROGRESS.md` file to a new file in the project directory.

Continue with the next step until all steps are complete.

When a PROGRESS.md step is started: 
1. Mark it as "In Progress" 
2. Note the date. 

When a step is complete: 
1. Mark it as "Complete" 
2. Note any applicable scripts that were created by listing them to the right of the progress step, on the same line.

As you go:
- Keep the user informed at every step: report what you are doing and why, show samples and summaries of data output when you run Python scripts, tell the user what files were created and where. This applies in all modes.
- Only ask for user input at steps marked for the chosen interaction mode. In Fully Automatic mode, the only required user input is the data format confirmation in Step 3. If you aren't sure what interaction mode has been chosen, ask again.
- Update REPORT.md in the appropriate section at every step. This is the primary document we'll use to communicate our analysis. It starts as boilerplate and you will fill it out as the project goes.
- Track steps to replicate results in a file REPLICATE.md: files to add (w/ size and last modified date to verify correct file), scripts to run, any manual edits made to automatically generated files (with reasoning), etc. A user without AI support should be able to follow the steps in REPLICATE.md to get the same results.
- Create python scripts as necessary to ensure the steps are repeatable.

# OTHER GUIDELINES

- Never include checkmarks or other unicode symbols in PowerShell commands - only use standard ASCII text and operators.
- If you are having folder access or file copy issues, it may mean the user hasn't accepted your request to access that folder. IMPORTANT: STOP WHAT YOU ARE DOING and wait for the user to approve any open requests. 
- CRITICAL: USE POWERSHELL `cp` COMMAND TO COPY FILES. DO NOT use the create_file tool to write new files from scratch. Template files exist in `.claude\skills\reserving-analysis\assets\` and scripts exist in `.claude\skills\reserving-analysis\scripts\` — use PowerShell `cp` to copy these to the project directory. If the copy operation fails STOP AND WORK WITH THE USER TO DEBUG IT. Real bugs (wrong path variable, wrong column name, missing customization for the user's data format) should be fixed with a targeted Edit after copying, not a full rewrite. Rewriting loses tested logic and introduces divergence from the skill's canonical scripts.
