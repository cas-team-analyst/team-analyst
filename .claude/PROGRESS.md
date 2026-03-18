# TeamAnalyst — Master Progress Log

> **For Claude:** This file owns the pipeline. Read it at the start of every
> session to orient yourself. Each skill closes by writing its summary block
> here and updating the pipeline. For sub-step procedure, open the skill's
> own PROGRESS.md. For methodology and judgment guidance, open the skill's SKILL.md.

---

## Run Metadata

| Field | Value |
|-------|-------|
| Valuation Date | |
| Line of Business | |
| Analyst | |
| Interaction Mode | |
| Data Source | |
| Data Format | |
| Currency / Units | |
| Run Started | |
| Run Completed | |

---

## Pipeline

Mark each fully completed step with a checkmark after completing all skill sub-steps.

1) [ ] setup-project (`setup-project/PROGRESS.md` )
2) [ ] identify-format (`identify-format/PROGRESS.md` )
3) [ ] validate-data (use only one of the following):
    - validate-loss-run (`validate-loss-run/PROGRESS.md` ) — use when `Data format` from Step 2 is `loss run`
    - validate-triangles (`validate-triangles/PROGRESS.md` ) — use when `Data format` from Step 2 is `triangle`

---

## Step Summaries

> Downstream skills read these blocks to get key outputs from prior steps.
> Only open a prior skill's PROGRESS.md if you need sub-step detail not here.
> Return to this file to see what steps have been completed and what needs to be done.
> Resume from the first uncompleted step in the pipeline if interrupted.

---

### Step 1 — setup-project
<!--
- Project root directory: [path]
- Data folder path: [path]
- Processed folder path: [path]
- Selections folder path: [path]
- Scripts folder path: [path]
- Interaction Mode: [careful/selections only/fully automated]
- Data files identified: [list]
-->

### Step 2 — identify-format
<!--
- Input file: [path]
- Data format: [loss run / triangle]
- Tab count: [int]
- Tab names: [list / none]
- Tabs matching loss run: [list / none]
- Tabs matching exposure: [list / none]
- Tabs matching incurred losses triangle: [list / none]
- Tabs matching paid losses triangle: [list / none]
- Tabs matching reported counts triangle: [list / none]
- Tabs matching closed counts triangle: [list / none]
-->

### Step 3b: validate-triangles

---

## Issues & Decisions Log

| # | Step | Issue | Decision | Rationale |
|---|------|-------|----------|-----------|
| — | — | — | — | — |

---

## Output Files Index

| File | Description | Step |
|------|-------------|------|
| — | — | — |

---

<!-- WORKFLOW COMPLETE block written here by Step 9 -->