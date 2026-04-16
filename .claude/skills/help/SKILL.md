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
- **LDF selections** — review age-to-age factors and make development factor selections
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
- **"View selection logic"** — triggers `/selection-logic` to review the actuarial LDF selection criteria and diagnostic rules used during chain-ladder selections
- **"Peer review my analysis"** — triggers `/peer-review` to review a completed reserving analysis against cross-method consistency checks and ASOP standards (13, 23, 25, 36, 41, 43); produces an advisory findings report without modifying selections

Mention the three interaction levels available during analysis:
1. **Careful** — step-by-step review at each stage, full user control over every decision
2. **Selections Only** — automated data prep and calculations, user input only for LDF selections
3. **Fully Automated** — end-to-end execution with no manual intervention

Wait for the user's response and guide them to the appropriate skill by explaining the way that they can invoke that skill.
