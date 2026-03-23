---
name: reserving-methods
description: Actuaries use different methods to come up with candidate reserve methods. Use when asked to apply an actuarial reserving method. Contains step-by-step instructions, code samples, and templates for helping the user prep their data, run the method and make selections. Available methods (new ones can be added) are chain-ladder and bf-bornhuetter-ferguson.
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
- output/selections/{method-name}.json: A JSON file to hold user selections for the method. Initially just "[]".
- 1-prep-data.py: Get data in standard format to simplify downstream operations. More info below. 
- ... Other necessary scripts for the method
- {n}-create-excel.py: Create an Excel file to help the user make selections. This file should initially have empty cells where selections will go, and it should contain in each sheet all the information that will be helpful for making selections.
- {n+1}-update-excel.py: Update the excel file with the latest selections from the JSON file (should not modify any other fields or rebuild he file completely).
- {n+2}-project-ultimates.py: After selections are made, this script will read the selections and data, create ultimate projections, and add them to the excel file. It is important that each method has the same output format so we can join them together to make final selections so review other methods' project ultimates script to understand format.

Review `assets/chain-ladder` for examples of a complete method implementation.

### 1-prep-data.py

- Output data should be in a long format with all the data in one table, where possible.
- Save as parquet to preserve ordering of categorical columns. For example, values like "7/1/2025-6/30/2026" can get sorted incorrectly if we don't capture the order from the input data.
- Save as CSV too for easy user inspection.
