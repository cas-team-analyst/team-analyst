# Replication Instructions

**Purpose:** This document is a human replication guide. An auditor can follow these instructions to reproduce all analysis results from scratch — without any AI assistance. The AI-assisted workflow that produced this analysis is not required to replicate it; only the data, scripts, and recorded selections below are needed.

_Filled in progressively as the analysis proceeds._

---

## Overview

| Field | Value |
|---|---|
| Analysis name | |
| Line of business / segment | |
| Valuation date | |
| Prepared by | |
| Draft date | |
| Interaction mode | |

---

## Prerequisites

- Python 3.x with packages listed in `scripts/requirements.txt`. Install with: `pip install -r scripts/requirements.txt`
- Input data files in `raw-data/` (listed in Step 2 below)
- No AI agent required

---

## Phase 1: Project Setup

**Directory structure to recreate:**

```
<project-folder>/
  raw-data/       ← input data files
  processed-data/ ← script outputs, including projected ultimates
  selections/     ← Excel workbooks (human review)
  selections/agent-logic/ ← JSON/MD selection inputs and outputs, saved selector agent specs
  scripts/        ← numbered Python scripts and modules/
```

**Input data files placed in raw-data/:**

_(list files here)_

---

## Phase 2: Data Extraction and Processing

**Script execution order:**

1. `scripts/1a-load-and-validate.py`
2. `scripts/1b-calculate-ldfs.py`
3. `scripts/1c-diagnostics.py`
4. `scripts/1d-ldf-averages.py`

**Customizations made to `1a-load-and-validate.py`:**

_(Record all non-default changes with enough detail to reproduce: column name mappings, data transformations, outlier handling decisions.)_

**Output files produced in `processed-data/`:**

_(list files here)_

**Data validation confirmed:** _(date)_

---

## Phase 4: Chain Ladder LDF Selections

**Script execution order:**

1. `scripts/2a-chainladder-create-excel.py` — creates `selections/Chain Ladder Selections - LDFs.xlsx`
2. Enter the final LDF selections below into the **User Selection** row of each sheet in the workbook.
3. `scripts/2b-chainladder-update-selections.py` — reads the workbook and writes combined selection files.

**Final LDF selections to enter manually:**

> These are the selections an auditor must enter into `Chain Ladder Selections - LDFs.xlsx`. Source: User Selection row if the analyst overrode the AI; otherwise the Framework AI Selection row.

| Measure | Development interval | Final selected LDF | Override? | Reasoning (if override) |
|---|---|---|---|---|
| | | | | |

---

## Phase 5: Tail Curve Method Selections

**Script execution order:**

1. `scripts/2c-tail-methods-diagnostics.py` — fits tail curves and generates diagnostics
2. `scripts/2d-tail-create-excel.py` — creates `selections/Chain Ladder Selections - Tail.xlsx`
3. Enter the final tail curve method selections below into the **User Selection** row of each sheet.
4. `scripts/2e-tail-update-selections.py` — reads the workbook and writes combined selection files.

> Note: `2f-chainladder-ultimates.py` (Step 6) reads the selected curve method and generates fitted LDFs beyond the cutoff automatically. The auditor does not need to fit curves manually.

**Final tail curve method selections to enter manually:**

| Measure | Final selected method | Override? | Reasoning (if override) |
|---|---|---|---|
| | | | |

---

## Phase 6: Calculate Method Projections

**Script execution order:**

1. `scripts/2f-chainladder-ultimates.py` — reads LDF selections and tail method; produces `processed-data/projected-ultimates.csv`
2. `scripts/3-ie-ultimates.py` — _(ran / skipped: state reason if skipped)_
3. `scripts/4-bf-ultimates.py` — _(ran / skipped: state reason if skipped)_

---

## Phase 7: Ultimate Selections

**Script execution order:**

1. `scripts/5a-ultimates-create-excel.py` — creates `selections/Ultimates.xlsx` with Losses and Counts sheets
2. Enter the final ultimate selections below into the **User Selection** column of each sheet.
3. `scripts/5b-ultimates-update-selections.py` — reads the workbook and writes combined selection files.
4. `scripts/5c-summary-indications.py` — computes headline indications from the selected ultimates.

**Final ultimate selections to enter manually:**

> Source: User Selection column if the analyst overrode the AI; otherwise the Framework AI Selection column.

**Losses:**

| Accident year | Final selected ultimate | Override? | Reasoning (if override) |
|---|---|---|---|
| | | | |

**Counts:**

| Accident year | Final selected ultimate | Override? | Reasoning (if override) |
|---|---|---|---|
| | | | |

---

## Phase 8: Build Analysis Workbook

**Script to run:**

```
scripts/6-analysis-create-excel.py
```

Reads: `processed-data/projected-ultimates.csv`, `selections/Ultimates.xlsx`

**Expected output files:**

- `selections/selected-ultimates.xlsx`
- `output/post-method-series.xlsx`
- `output/post-method-triangles.xlsx`
- `output/complete-analysis.xlsx`

---

## Phase 9: Technical Review

**Script to run:**

```
scripts/7-tech-review.py
```

**Issues flagged (or "None — all checks passed"):**

_(list any FAIL or WARN items here)_

**Known issues or deviations an auditor should be aware of:**

_(list here, or "None")_

---

## Key Outputs

| File | Description |
|---|---|
| `REPORT.md` | Primary narrative deliverable |
| `output/complete-analysis.xlsx` | Primary numerical deliverable |
| `selections/Ultimates.xlsx` | Ultimate selections by category and accident year |
| `selections/Chain Ladder Selections - LDFs.xlsx` | LDF selections by measure |
| `selections/Chain Ladder Selections - Tail.xlsx` | Tail curve method selections |
