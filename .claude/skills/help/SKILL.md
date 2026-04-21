---
name: help
description: Get oriented with the TeamAnalyst plugin and explore available skills. Use when first getting started, checking what analysis capabilities are available, or surveying skills before beginning work. Trigger phrases: "start", "get started", "what can you do", "help", "overview", "show skills".
---

# TeamAnalyst Start

Walk the user through orientation with the TeamAnalyst plugin.

## Step 1: Welcome

Display this welcome message:

```
TeamAnalyst Plugin

Your AI-powered actuarial analyst. This plugin walks you through loss reserving
analysis — from exploring raw data to selecting development factors and
projecting ultimates — entirely through conversation.
```

## Step 2: Survey Available Skills

Describe the plugin's main capability:

The plugin's primary workflow is **Reserving Analysis** (`/reserving-analysis`), which orchestrates the full reserving process end-to-end:

- **Data exploration** — preview Excel files, understand triangle structure, and create standardized file summaries
- **Method execution** — run actuarial reserving methods on your data
- **LDF selections** — review age-to-age factors and make development factor selections (non-tail intervals)
- **Tail factor selections** — fit tail curves (Bondy, Exponential Decay, McClenahan, Skurnick, etc.), review diagnostics, and select tail factors separately from LDF selections
- **Ultimate projections** — project ultimate losses from your selections

Available reserving methods:

| Method | Status | Notes |
|--------|--------|-------|
| **Chain Ladder** | Active | Core method, no additional inputs needed |
| **Initial Expected** | Active | Requires an Expected Loss Rate input file and exposures |
| **Bornhuetter-Ferguson** | Active | Requires Chain Ladder and Initial Expected results; skipped automatically if IE was not run |

## Step 3: Ask How to Help

Ask what the user is working on today. Suggest starting points:

- **"Run a reserving analysis"** — triggers `/reserving-analysis` to set up a project and walk through the full workflow
- **"View selection logic"** — triggers `/selection-logic` to review the actuarial LDF and tail factor selection frameworks used during chain-ladder selections
- **"Peer review my analysis"** — triggers `/peer-review` to review a completed reserving analysis against cross-method consistency checks and ASOP standards (13, 23, 25, 36, 41, 43); produces an advisory findings report without modifying selections

Mention the three interaction levels available during analysis:
1. **Careful** — step-by-step review at each stage, full user control over every decision
2. **Selections Only** — automated data prep and calculations, user input only for LDF selections
3. **Fully Automated** — end-to-end execution with no manual intervention

## Step 4: Explain the Three Standard Documents

Let the user know that every reserving analysis produces three standard markdown documents in the project folder. These are created at the start of the workflow and filled in as the analysis progresses:

- **REPORT.md** — The primary deliverable. A structured actuarial report (purpose, scope, data, methodology, assumptions, results, diagnostics, uncertainty, ASOP self-check, etc.). This is what the user will share with reviewers or stakeholders. It starts as boilerplate and gets filled in at every step of the workflow.
- **PROGRESS.md** — A running checklist of the workflow steps. Tracks what has been completed, what is in progress, and which scripts were produced at each step. Useful for resuming work across sessions and seeing where the analysis stands.
- **REPLICATE.md** — A reproducibility log. Captures the inputs, scripts run, and any manual edits (with reasoning) needed to reproduce the analysis without AI assistance. A reviewer or future analyst should be able to follow REPLICATE.md to arrive at the same results.

Wait for the user's response and guide them to the appropriate skill by explaining the way that they can invoke that skill.
