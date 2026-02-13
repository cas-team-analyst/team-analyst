---
name: chain-ladder-method
description: Guide for using the Chain Ladder (Loss Development Method) for actuarial loss reserving.
---

## Required Inputs
- Loss triangle (accident year × valuation age)

## Progress Template

Copy steps from .claude\skills\chain-ladder-method\PROGRESS.MD into PROGRESS.md and then proceed with progress.

## Excel Template Structure

### Excel template Template - Chain Ladder Selections.xlsx
Sheet 1 "Instructions": Instructions for how to use the template. You can ignore this.
Sheet 2 "Template": Main template for chain ladder selections. To be copied for each triangle that needs selections. 
- 4 Sections: Development (title at row 1, age labels in n row 3, periods in col B), Loss Development Factors (title at row 16, age label formulas in row 18, periods in col B as formulas referring up to Development), Averages (title at row 30, average labels in col B, now age labels, contains formulas for calculating average LDFs at each development step), Selections (title at row 39, 3 scenarios starting at row 41, each has 4 rows: Scenario label, Selected, Average Used, Reasoning).
- Contains dummy Development data, formulas for LDFs and Averages. Selections are initially blank. 
- Period and age labels are meant to be replaced in the Development table.