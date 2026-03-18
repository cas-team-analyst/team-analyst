---
name: identify-format
description:
  Second step of the actuarial reserving pipeline; loads data provided by the user and identifies the data format for further processing. Use when the master PROGRESS.md shows Step 1 "setup-project" complete and Step 2 "identify-format" pending.
---

# Step 2: identify-format -- Reference

Loads actuarial input data, identifies the data format, and confirms the format with the user.

Procedure is in `identify-format/PROGRESS.md`. Consult this file for additional guidance.

---

## Sub-step Guidance

### Sub-step 1. Load Data File

**Read from setup-project output, then confirm with the user.**

Open the master `.claude/PROGRESS.md` and read the **Step 1 — setup-project** summary block.
Extract the `Data files identified` list and the `Data folder path`.

If one or more files were recorded, list all, propose the most likely candidate (prefer `.xlsx`/`.xlsm` over `.csv`), and ask the user which file to use:

> Setup identified the following data file(s) in `{data_folder}`:
>
> {numbered list of files}
>
>
> I'll use **{proposed_file}** — does that look right, or would you like to use a different file?

**If the user confirms the proposed file** → record the path and proceed with it for Sub-step 2; do not proceed to Sub-step 2 until the user has explicitly confirmed (e.g. "yes", "looks good", "confirmed").
**If the user selects a different file or provides a new path** → record their answer and proceed with the new path for Sub-step 2.
**If no files were recorded in Step 1** → ask:
> I don't see any data files recorded from setup. Please provide the full path to your data file (accepted: `.csv`, `.xlsx`, `.xlsm`, `.xls`).

**Once the path is confirmed** → load it:

```python
from scripts.`1-load-data` import load_data

sheets = load_data("{path}")
```

If a `FileNotFoundError` or `ValueError` is raised, report it and ask the user to provide a corrected path.

Record the following in `identify-format/PROGRESS.md`:
- Files from `setup-project`
- File path confirmed by user
- File loaded successfully
- Error (if any)

---

### Sub-step 2. Summarize Data

Call `summarize_workbook()` and present the report to the user:

```python
from scripts.`2-summarize-workbook` import summarize_workbook

summary = summarize_workbook(sheets)
print(summary.report())
```

> Here's a quick look at the file — tabs, shapes, columns, and a few rows from each tab:
>
> {report output}
>
> Does this look correct before I proceed?

**If the user does not confirm** → ask what looks wrong and return to Sub-step 1 if needed.

Record the following in `identify-format/PROGRESS.md`:
- User confirmed summary looks correct

---

### Sub-step 3. Identify Tabs and Format

**Run tab identification first, then confirm with the user.**

```python
from scripts.`3-identify-tabs` import identify_tabs

tab_check_results = identify_tabs(sheets)
```

`tab_check_results.tabs_matching_loss_run` shows which tabs matched loss run patterns.
`tab_check_results.tabs_matching_exposure` shows which tabs matched exposure patterns.
`tab_check_results.tabs_matching_triangle` shows which tabs matched triangle patterns.

Report the tab mapping results to the user and ask the user to confirm.

> I found the following in {path}:
> - tab count: {tab_check_results.tab_count}
> - tab names: {tab_check_results.tab_names}
> - tabs matching loss run patterns: {tab_check_results.tabs_matching_loss_run} (e.g. `["Loss Run", "Loss Run Data"]`)
> - tabs matching exposure patterns: {tab_check_results.tabs_matching_exposure} (e.g. `["Exposure", "Exposure Data"]`)
> - tabs matching triangle patterns: {tab_check_results.tabs_matching_triangle} (e.g. `{"incurred_losses": ["Incurred Losses", "Incurred Losses Data"], "paid_losses": ["Paid Losses", "Paid Losses Data"], "reported_counts": ["Reported Counts", "Reported Counts Data"], "closed_counts": ["Closed Counts", "Closed Counts Data"]}`)

 - **If tabs_matching_loss_run is not empty, tabs_matching_triangle is empty for all measures, and the user confirms** → tell the user that TeamAnalyst will be run in loss run mode and update "User confirmed format" to "loss run" in skill's PROGRESS.md.
 - **If tabs_matching_triangle is not empty for at least one measure, tabs_matching_loss_run is empty, and the user confirms** → tell the user that TeamAnalyst will be run in triangle mode and update "User confirmed format" to "triangle" in skill's PROGRESS.md.
 - **If tabs_matching_loss_run is not empty, tabs_matching_triangle is not empty, and the user confirms** → ask the user to confirm which format they want to use.
    - **If the user indicates "loss run"** → tell the user that {tabs_matching_triangle} will not be used and update "User confirmed format" to "loss run" in skill's PROGRESS.md.
    - **If the user indicates "triangle"** → tell the user that {tabs_matching_loss_run} will not be used and update "User confirmed format" to "triangle" in skill's PROGRESS.md.
 - **If the user does not confirm** → ask the user to correct the tab mapping and return to Sub-step 1 if needed.