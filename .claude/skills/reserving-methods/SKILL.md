---
name: reserving-methods
description: Actuaries use different methods to come up with candidate reserve methods. Use when asked to apply an actuarial reserving method. Contains step-by-step instructions, code samples, and templates for helping the user prep their data, run the method and make selections.
compatibility: python, node.js, git
---

# Reserving Methods


## Instructions

When a user asks to apply an actuarial reserving method: 
1. Copy the PROGRESS.md template into the main PROGRESS.md file. There is a folder in assets/ for each available method (and new ones can be added). Each has a PROGRESS.md. 
2. Go back to working through the main PROGRESS.md.


## Available Methods

- assets/chain-ladder
- assets/bf-bornhuetter-ferguson (UNDER CONSTRUCTION)


## Creating New Methods

To add a new reserving method, create a new folder in assets/ with the necessary files:
- PROGRESS.md: A checklist of detailed steps to generate ultimate projections using the method.
- report.html: An HTML template to display the results and gather user input. More info below. 
- 1-prep-data.py: Get data in standard format to simplify downstream operations. More info below. 
- 2-enhance-data.py: Add calculated columns needed for chain ladder. These should typically not be changed, they should work with the format of the data output by 1-prep-data.py.
- ... Other necessary scripts for the method
- {n}-selections.py: Make initial selections.
- {n+1}-update-report.py: Update report.html.
- {n+1}-project-ultimates.py: Update report.html. More info below. 

Review `assets/chain-ladder` for examples of a complete method implementation.

### report.html

- Place the data at the top of this file in a `<script>` tag so it can easily be replaced by `update-report.py`.
- Link to the CSS and JS files in the ./static/ folder in the project root for consistency. 
- See an example at `assets/chain-ladder/report.html`.

### 1-prep-data.py

- Output data should be in a long format with all the data in one table.
- Save as parquet to preserve ordering of categorical columns. For example, values like "7/1/2025-6/30/2026" can get sorted incorrectly if we don't capture their order when we read the raw data.
- Save as CSV too for easy user inspection.

### project-ultimates.py

- It is important that each method has the same output format so we can join them together to make final selections.
