---
name: reserving-analysis
description: Actuarial reserving analysis workflow. Use when the user requests reserving. Do NOT use for peer review (separate skill exists).
---

# Reserving Analysis Workflow

## Startup Steps - Follow Every Time!

1. Identify and mount the project folder. Obtain permission to modify it.
2. Identify and mount the plugin skill folder (if applicable, NOT the anthropic-skills folder) so you can copy files from it into the project folder.
3. Check for existing `PROGRESS.md` file and use it to understand what the next step is.
4. If no `PROGRESS.md` exists:
   - Copy PROGRESS.md, REPORT.md, and REPLICATE.md from `assets/` to project directory. Use copy commands, do NOT read and write the files.
   - Start steps in PROGRESS.md. Mark them in progress/complete as you go.

## CoWork Agent Guidelines

**File operations:** Copy files with `cp {BASE_DIRECTORY}/{skill_path} {PROJECT_FOLDER}/{target_path}`. Mount skill folder first. DO NOT use `create_file` for templates. Convert Windows paths to Unix: `C:\Users\...` → `/mnt/c/Users/...`

**Template guardrails:** If copy fails, STOP and debug. Fix bugs with targeted edits AFTER copying - never rewrite entire files (loses tested logic).

**Other:** Cache out of date? Suggest close/reopen CoWork. Never use unicode symbols in commands.

## Quick Reference

**Sections in this skill:**
- [Supporting Files](#supporting-files)
- [Key Principles](#key-principles)
- [Progress Tracking](#progress-tracking)
- [User Communication](#user-communication)

---

## Supporting Files

**Skill folder structure:**
- `assets/` - Templates (PROGRESS.md, REPORT.md, REPLICATE.md, welcome message) and selection framework guide
- `scripts/` - Numbered Python workflow scripts (1a-7) and modules/ subdirectory with shared utilities
- `agents/` - Selector subagents for LDF, tail curve method, and ultimate selections (rules-based and open-ended variants)

## Key Principles

**File handling:**
- Copy template files from `assets/` using command line - never create from scratch
- Copy Python scripts from `scripts/` to project folder before running
- Fix bugs with targeted edits AFTER copying - never rewrite entire files

**Project folder naming (Windows path length):**
- When creating a new project folder, derive a short slug from the analysis title — do NOT use the full title as the folder name. Convert to lowercase, replace spaces with hyphens, strip special characters, and cap at 30 characters. Example: "Q1 2025 Reserve Review — WC" → `q1-2025-reserve-review-wc`. The full analysis title is used only inside documents (REPORT.md, REPLICATE.md).
- Windows MAX_PATH is 260 characters. Deep project paths (base folder + project slug + `selections/Chain Ladder Selections - LDFs.xlsx`) can easily hit this limit if the folder name is long. If the resolved output path will exceed 200 characters, warn the user and suggest moving the project folder closer to the drive root.

**Documentation:**
- Follow PROGRESS.md to track workflow state (mark In Progress → Complete)
- Update REPORT.md at each step with findings, selections, and rationale
- Maintain REPLICATE.md for reproducibility (files, scripts, manual edits)

**Script execution:**
- PROGRESS.md specifies which scripts to run at each step
- Run numbered scripts in sequence as directed by PROGRESS.md
- Invoke selector subagents (from `agents/` folder) when PROGRESS.md indicates
- Update Excel workbooks with AI selections via update scripts

**User communication:**
- Keep user informed with data samples and summaries after running scripts
- Report what you're doing and why before each action
- Announce files created with locations

## Progress Tracking

**When starting or completing a PROGRESS.md step:**
1. Mark status as "In Progress" or "Complete"
2. Note the date

**Update REPORT.md:**
- Fill in appropriate section at each step
- Include findings, selections, and rationale
- REPORT.md starts as boilerplate template; you populate it

**Update REPLICATE.md:**
- Document files added (with size and last modified date)
- List scripts to run in sequence
- Note any manual edits to auto-generated files (with reasoning)
- Should enable reproduction without AI assistance

## User Communication

**Keep user informed:**
- Report what you're doing and why before each action
- Show data samples and summaries after running Python scripts
- Announce files created with locations
- Applies in all interaction modes

**User input by mode:**
- **Pause for Selections:** Pauses after LDF selections and after ultimate selections for user review
- **Fully Automatic:** Only data format confirmation (Step 3 in PROGRESS.md)

**Ask for interaction mode preference** using exact option names from PROGRESS.md during project setup
