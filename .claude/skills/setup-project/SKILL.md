---
name: setup-project
description:
    First step of the actuarial reserving pipeline; sets up a new actuarial reserving project from scratch. Use when the master PROGRESS.md shows Step 1 pending and the user requests "start a loss reserving project", "develop ultimate losses", "perform actuarial reserving", "set up a new project", "initialize a reserving project", or similar.
---

# Step 1: setup-project -- Reference

Initializes a new actuarial reserving project by establishing the folder structure, Python and Node.js environments, and data files needed to run the full reserving pipeline.

Procedure is in `setup-project/PROGRESS.md`. Consult this file for additional guidance.

---

## Sub-step Guidance

### Sub-step 2. Create folder structure
Create the following directories relative to the project root:

| Purpose | Relative Path |
| ------- | ------------- |
| Raw input data | `data/` |
| Intermediate processed outputs | `output/processed/` |
| Analyst selections and picks | `output/selections/` |
| Generated or archived scripts | `output/scripts/` |

### Sub-step 3. Set up .venv
Run in the project root:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
If `requirements.txt` is not found at the root, search one level up and in `output/scripts/`. Record the resolved path in PROGRESS.md.

### Sub-step 4. Install Node.js requirements
Run `npm install` in the project root. If `package.json` is absent, note that in PROGRESS.md and skip with no failure.

### Sub-step 5. Request user's desired level of interaction
| Mode | Description |
| ---- | ------- |
| **Careful** | Pause frequently to review work before proceeding |
| **Selections Only** | Only stop when an analyst selection or pick is required |
| **Fully Automated** | Run all steps without interruption; skip selections review |

### Sub-step 6. Request user to copy data files to `data/`
Ask the user to place their loss triangle data files (CSV, Excel, etc.) in the `data/` directory. Once they confirm, list the files found in `data/` and record them in PROGRESS.md. Do not proceed to close the skill until at least one data file is present.

### Sub-step 7. Close skill
Fill in all output fields in PROGRESS.md, then copy the completed **Master Closing Block** into the master `.claude/PROGRESS.md` → Step 1 Summary and mark Step 1 `[x]` in the master pipeline.