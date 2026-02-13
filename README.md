# Actuarial Reserve Ultimate Estimates

## Project Overview
This project supports the development of actuarial reserve ultimate estimates using systematic methodology and thorough documentation, with the help of an AI coding agent.

## Prerequisites
*TODO: Add more detailed instructions.*

- Python
- Git
- Claude Code
- Node

# Notes for Developers Working on Skills:

## Testing strategy

You can use a branch to run a test and then easily switch back to the baseline repo.

```bash
git branch -D test
git checkout -B test
claude
```

Then make notes in a notepad for things you want to change. 

When done testing
```bash
git checkout main
```

## Guidelines

- If something unexpected is happening, first check to make sure the skill isn't making it happen. Avoid creating new instructions that override prior instructions, which can happen easily if the skill is complex. 

## Quick Start

1. Clone this repository into a new folder. 
2. Open Claude Code in the folder and say "Let's get started!"

## Project Structure

```
├── .claude              # Skills and documentation for Claude Code
├── PROGRESS.md          # Progress tracking and status
├── README.md            # This file
├── requirements.txt     # Required Python packages.
├── data/                # Raw data files
│   └── processed/       # Cleaned/transformed data
├── analysis/            # Intermediate calculations and diagnostics
├── selections/          # Documented selection decisions
├── scripts/             # Python scripts for repeatability
│   └── pytest/          # Unit tests for Python scripts
└── output/              # Final results and exhibits
```

## Progress Tracking
See [PROGRESS.md](PROGRESS.md) for current status, completed steps, and pending items.

## Project Metadata
*To be documented*
- Client: 
- Segment (if applicable):
- Evaluation Date: 
- Accident Periods:
- etc.

## Contacts/Stakeholders
- *To be documented*

## Special Considerations
- *To be documented during planning phase*

## Data
*To be documented: add important info about files at ./data/*
| File Name | Description | Location | Special Notes |
|-----------|-------------|----------|---------------|
| | | | |