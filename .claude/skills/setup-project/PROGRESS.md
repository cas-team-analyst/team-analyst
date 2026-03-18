# Step 1: setup-project -- Procedure

> This file owns the procedure for the setup-project skill.
> For guidance on carrying out a sub-step, see `setup-project/SKILL.md`.
> Update sub-step status and write findings after each sub-step.
> Resume from the first uncompleted sub-step if interrupted.

## Pre-condition

- [ ] Master PROGRESS.md exists in .claude/

---

## Pipeline

Mark each completed sub-step with a checkmark after successful completion.

1) [ ] Copy PROGRESS.md to project root
2) [ ] Create folder structure
3) [ ] Set up .venv
4) [ ] Install Node.js requirements
5) [ ] Request user's desired level of interaction
6) [ ] Request user to copy relevant data files to data/
7) [ ] Close skill

### Sub-step 1. Copy PROGRESS.md to project root

```
PROGRESS.md copied to project root: [yes / no]
Project root directory: [path]
```

### Sub-step 2. Create Folder Structure

```
Folder structure created: [yes / no]
Data folder path: [path]
Processed folder path: [path]
Selections folder path: [path]
Scripts folder path: [path]
```

### Sub-step 3. Set up .venv

```
.venv set up: [yes / no]
requirements.txt path: [path]
requirements.txt Failures: [none / list]
requirements.txt Warnings: [none / list]
```

### Sub-step 4. Install Node.js requirements

```
Node.js Failures: [none / list]
Node.js Warnings: [none / list]
```

### Sub-step 5. Request user's desired level of interaction

```
Interaction Mode: [careful/selections only/fully automated]
```

### Sub-step 6. Request user to copy relevant data files to data/

```
Data files copied to data/: [yes / no]
Data files identified: [list]
```

### Sub-step 7. Close Skill

```
a) Copy the block below into master PROGRESS.md → Step 1 Summary
b) Update master Pipeline Step 1 status to [x]
c) Alert analyst: "Project setup complete. Run identify-format."
```

---

## Master Closing Block

```
### Step 1 — setup-project
**Status:** Complete — [timestamp]
- Project root directory: [path]
- Data folder path: [path]
- Processed folder path: [path]
- Selections folder path: [path]
- Scripts folder path: [path]
- Interaction Mode: [careful/selections only/fully automated]
- Data files identified: [list]
```
