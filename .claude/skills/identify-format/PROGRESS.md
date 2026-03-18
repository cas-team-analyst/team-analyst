# Step 2: identify-format -- Procedure

> This file owns the procedure for the Step 2: identify-format skill.
> For guidance on carrying out a sub-step, see `identify-format/SKILL.md`.
> Update sub-step status and write findings after each sub-step.
> Resume from the first uncompleted sub-step if interrupted.

## Pre-conditions

- [ ] Master PROGRESS.md exists in .claude/
- [ ] Step 1 (setup-project) is marked complete in master PROGRESS.md
- [ ] At least one data file is present in data/

---

## Pipeline

Mark each completed sub-step with a checkmark after successful completion.

1) [ ] Load data file
2) [ ] Summarize data
3) [ ] Identify data format
4) [ ] Close skill

### Sub-step 1. Load Data File

```
Files from setup-project: [list from master PROGRESS.md Step 1 / none recorded]
File path confirmed by user: [path]
File loaded successfully: [yes / no]
Error (if any): [none / message]
```

### Sub-step 2. Summarize Data

```
User confirmed summary looks correct: [yes / no]
```

### Sub-step 3. Identify Data Format

```
User confirmed format: [loss run / triangle]
Tab count: [int]
Tab names: [list / none]
Tabs matching loss run: [list / none]
Tabs matching exposure: [list / none]
Tabs matching incurred losses triangle: [list / none]
Tabs matching paid losses triangle: [list / none]
Tabs matching reported counts triangle: [list / none]
Tabs matching closed counts triangle: [list / none]
```

### Sub-step 4. Close Skill

```
a) Copy the block below into master PROGRESS.md → Step 2 Summary
b) Update master Pipeline Step 2 status to [x]
c) Alert analyst: "Format identification complete. Run validate-{identified format}."
```

---

## Master Closing Block

```
### Step 2 — identify-format
**Status:** Complete — [timestamp]
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
```
