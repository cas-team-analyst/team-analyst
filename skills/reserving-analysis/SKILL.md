---
name: reserving-analysis
description: Actuarial reserving analysis workflow. Do NOT use for peer review (separate skill exists).
---

# Reserving Analysis Workflow

## Initial Setup

**Identify working directory:**
1. Identify and mount the plugin folder (if applicable) 
2. Identify and mount (if applicable) the project folder
3. Check for existing `PROGRESS.md` file and use it to understand what the next step is
4. If no `PROGRESS.md` exists:
   - Copy PROGRESS.md, REPORT.md, and REPLICATE.md from `assets/` to project directory
   - Start steps in PROGRESS.md

**Confirm interaction mode:**
- Ask user to choose: **Pause for Selections** or **Fully Automatic**
- Use exact option names from PROGRESS.md
- Track chosen mode for subsequent user interaction points

**Overview:** PROGRESS.md contains the detailed step-by-step workflow. Follow that file for execution. This skill provides supporting context and principles.

## CoWork Agent Guidelines

**File operations:** Copy files with `cp {BASE_DIRECTORY}/{skill_path} {PROJECT_FOLDER}/{target_path}`. Mount skill folder first. DO NOT use `create_file` for templates. Convert Windows paths to Unix: `C:\Users\...` → `/mnt/c/Users/...`

**Template guardrails:** If copy fails, STOP and debug. Fix bugs with targeted edits AFTER copying - never rewrite entire files (loses tested logic).

**Other:** Cache out of date? Suggest close/reopen CoWork. Never use unicode symbols in commands.

## Quick Reference

**Sections in this skill:**
- [Workflow Structure](#workflow-structure)
- [Supporting Files](#supporting-files)
- [Key Principles](#key-principles)
- [Progress Tracking](#progress-tracking)
- [User Communication](#user-communication)

---

## Workflow Structure

High-level phases (detailed steps in PROGRESS.md):
1. Initial Setup → Project folder setup and interaction mode selection
2. Progress Tracking → PROGRESS.md, REPORT.md, and REPLICATE.md management
3. Data Preparation → Load, validate, and prepare triangle data
4. Chain Ladder Development → LDF calculation and selection
5. Tail Factor Selection → Tail analysis and selection
6. Alternative Methods → IE and BF calculations
7. Ultimate Selection → Final ultimate selections
8. Finalization → Consolidation and technical review

## Supporting Files

**Skill folder structure:**
- `assets/` - Templates (PROGRESS.md, REPORT.md, REPLICATE.md, welcome message) and selection framework guide
- `scripts/` - Numbered Python workflow scripts (1a-7) and modules/ subdirectory with shared utilities
- `agents/` - Selector subagents for LDF, tail factor, and ultimate selections (rules-based and open-ended variants)

## Key Principles

**File handling:**
- Copy template files from `assets/` using command line - never create from scratch
- Copy Python scripts from `scripts/` to project folder before running
- Fix bugs with targeted edits AFTER copying - never rewrite entire files

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
