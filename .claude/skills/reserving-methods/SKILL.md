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
- report.html: An HTML template to display the results and gather user input.
- 1-prep-data.py: Get data in standard format to simplify downstream operations. 
- 2-enhance-data.py: Add calculated columns needed for chain ladder. These should typically not be changed, they should work with the format of the data output by 1-prep-data.py.
- ... Other necessary scripts for the method
- {n}-selections.py: Make initial selections.
- {n+1}-update-report.py: Update report.html.