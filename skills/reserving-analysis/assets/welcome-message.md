# WELCOME

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

Throughout the workflow, you'll be kept informed of what is happening and why.
