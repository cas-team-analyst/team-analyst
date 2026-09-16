# Replication Instructions

**Purpose:** This document is a human replication guide. An auditor can follow these instructions to reproduce all analysis results from scratch — without any AI assistance. The AI-assisted workflow that produced this analysis is not required to replicate it; only the data, scripts, and recorded selections below are needed.

_Filled in progressively as the analysis proceeds._

---

## Overview

| Field | Value |
|---|---|
| Analysis name | Triangle Examples 1 Reserve Review |
| Line of business / segment | To be confirmed from triangle data (Phase 2) |
| Valuation date | To be confirmed from triangle data (Phase 3) |
| Prepared by | Bryce (AI-assisted, reserving-analysis workflow) |
| Draft date | 08/30/2026 |
| Interaction mode | Fully Automatic |

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

- `Triangle_Examples_1.xlsx` (uploaded by user)

---

## Phase 2: Data Extraction and Processing

**Script execution order:**

1. `scripts/1a-load-and-validate.py`
2. `scripts/1b-calculate-ldfs.py`
3. `scripts/1c-diagnostics.py`
4. `scripts/1d-ldf-averages.py`

**Customizations made to `1a-load-and-validate.py`:**

- `Paid 1` and `Inc 1` sheets: row 1 is a label row ("Age of Evaluation"), row 2 is the real header (Accident Year + ages in months: 11, 23, 35, ..., 287), row 3+ is data. Parsed accordingly.
- `Ct 1` sheet: row 1 is the header directly (Accident Year + ages), row 2+ is data. Parsed accordingly.
- `Ct 1` (claim counts) classified as **Reported Count** per the default assumption rule (no explicit "Closed"/"Settled" label in the source workbook). User confirmed this during the Phase 3 data validation review.
- `Exposure` sheet (Accident Year, Payroll) loaded as a simple period→value table with `age=None`, `unit_type="Dollars"`.
- No column renames or outlier exclusions were needed beyond the layout parsing above — all values loaded as-is.

**Output files produced in `processed-data/`:**

- `1_triangles.csv` — 924 rows: Paid Loss (300), Incurred Loss (300), Reported Count (300), Exposure (24)
- `2_enhanced.csv` — triangle values with calculated LDFs (828 rows with LDFs)
- `3_diagnostics.csv` — diagnostic columns (reported claims, severity, paid-to-incurred ratio, case reserves, loss rates, frequency)
- `4_ldf_averages.csv` — 69 rows of LDF averages (weighted/simple/exclude-high-low across all/3yr/5yr/10yr windows) and QA metrics (CV, slope) by measure and development interval

**Data validation confirmed:** 08/30/2026 (user replied "looks good")

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
| Paid Loss | 11-23 | 2.5525 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 23-35 | 1.4435 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 35-47 | 1.1327 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 47-59 | 1.0978 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 59-71 | 1.1192 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 71-83 | 1.1298 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 83-95 | 1.0328 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 95-107 | 1.0164 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 107-119 | 1.0847 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 119-131 | 1.0083 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 131-143 | 1.0189 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 143-155 | 1.0175 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 155-167 | 1.0134 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 167-179 | 1.0143 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 179-191 | 1.0156 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 191-203 | 1.0115 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 203-215 | 1.0021 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 215-227 | 1.0047 | No | Framework AI selection (final cutoff at 239mo) |
| Paid Loss | 227-239 | 1.0025 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 11-23 | 1.6456 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 23-35 | 1.212 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 35-47 | 1.0948 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 47-59 | 1.0367 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 59-71 | 1.1027 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 71-83 | 1.087 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 83-95 | 1.0065 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 95-107 | 1.0146 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 107-119 | 1.0485 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 119-131 | 1.0082 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 131-143 | 1.035 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 143-155 | 1.0022 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 155-167 | 1.0004 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 167-179 | 1.0211 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 179-191 | 1.0036 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 191-203 | 1.0076 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 203-215 | 1.002 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 215-227 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Incurred Loss | 227-239 | 1.0089 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 11-23 | 1.118 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 23-35 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 35-47 | 1.0008 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 47-59 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 59-71 | 0.9992 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 71-83 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 83-95 | 0.9993 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 95-107 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 107-119 | 0.9977 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 119-131 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 131-143 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 143-155 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 155-167 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 167-179 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 179-191 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 191-203 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 203-215 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 215-227 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |
| Reported Count | 227-239 | 1.0 | No | Framework AI selection (final cutoff at 239mo) |

---

## Phase 5: Tail Curve Method Selections

**Script execution order:**

1. `scripts/2c-tail-methods-diagnostics.py` — fits tail curves and generates diagnostics
2. `scripts/2d-tail-create-excel.py` — creates `selections/Chain Ladder Selections - Tail.xlsx`
3. Enter the final tail curve method selections below into the **User Selection** row of each sheet.
4. `scripts/2e-tail-update-selections.py` — reads the workbook and writes combined selection files.

> Note: `2f-chainladder-ultimates.py` (Step 6) reads the selected curve method and generates fitted LDFs beyond the cutoff automatically. The auditor does not need to fit curves manually.

**Final tail curve method selections to enter manually:**

| Measure | Final selected method | Tail factor | Override? | Reasoning (if override) |
|---|---|---|---|---|
| Paid Loss | bondy | 1.0060 | No | Framework AI selection — exp forms rejected (gap_flag=True); materiality anchor satisfied (0.093% of CDF) |
| Incurred Loss | mcclenahan | ≈1.0000 | No | Framework AI selection — exp forms rejected (gap_flag=True); Bondy failed materiality anchor (0.741% of CDF); McClenahan was the only scenario passing both gates. See REPORT.md Section 11 for open question re: divergence from Open-Ended's Bondy (1.017) selection. |
| Reported Count | exp_dev_quick | ≈1.0000 | No | Framework AI selection — R²=1.000, excellent fit, no gap flag |

---

## Phase 6: Calculate Method Projections

**Script execution order:**

1. `scripts/2f-chainladder-ultimates.py` — reads LDF selections and tail method; produces `processed-data/projected-ultimates.csv`. Chain Ladder ultimate totals: Paid Loss $52,820,151 (IBNR $11,052,297); Incurred Loss $51,730,785 (IBNR $8,114,390); Reported Count 9,737 (IBNR 21).
2. `scripts/3-ie-ultimates.py` — **ran**, using the built-in ELR fallback (no pricing ELR file provided; see REPORT.md Section 5.2 for the derived per-AY rates). IE ultimate totals: Paid/Incurred Loss $46,003,887; Reported/Closed Count 10,325.
3. `scripts/4-bf-ultimates.py` — **ran** (both CL and IE were available). BF ultimate totals: Paid Loss $48,572,178 (IBNR $6,804,323); Incurred Loss $48,813,353 (IBNR $5,196,958); Reported Count 9,738 (IBNR 22).

---

## Phase 7: Ultimate Selections

**Script execution order:**

1. `scripts/5a-ultimates-create-excel.py` — creates `selections/Ultimates.xlsx` with Losses and Counts sheets
2. Enter the final ultimate selections below into the **User Selection** column of each sheet.
3. `scripts/5b-ultimates-update-selections.py` — reads the workbook and writes combined selection files.
4. `scripts/5c-summary-indications.py` — computes headline indications from the selected ultimates.

**Final ultimate selections to enter manually:**

> Source: User Selection column if the analyst overrode the AI; otherwise the Framework AI Selection column. Full per-accident-year detail (all 24 years) is in `selections/Ultimates.xlsx`, Framework AI Selection column, and in `selections/agent-logic/ultimates-ai-framework-loss.json` / `-count.json`.

**Losses (totals):** Selected ultimate $49,174,758 | Paid to date $41,767,854 | Case reserves $1,848,541 | IBNR $5,558,363. No manual overrides (Fully Automatic mode) — Framework AI Selection used throughout. See REPORT.md Section 11 for flagged judgment calls (AY2012, AY2020).

**Counts (totals):** Selected ultimate ~9,739 | Reported to date 9,716 | IBNR 23. No manual overrides.

---

## Phase 8: Build Analysis Workbook

**Script to run:**

```
scripts/6-analysis-create-excel.py
```

Reads: `processed-data/projected-ultimates.csv`, `selections/Ultimates.xlsx`

**Output file produced:**

- `Analysis.xlsx` (in the project root) — sheets: Notes, Loss Selection, Incurred CL, Paid CL, Incurred BF, Paid BF, Count Selection, Reported CL, Reported BF, Incurred, Paid, Reported, Exposure, Pre-Method Diagnostics, Post-Method Diagnostics. Verified totals on "Loss Selection" tab match the headline indications above (Selected Ultimate $49,174,758, IBNR $5,558,363.14, Unpaid $7,406,903.66).

---

## Phase 9: Technical Review

**Script to run:**

```
scripts/7-tech-review.py
```

**Issues flagged:** 94 checks run: 64 PASS, 30 WARN, 0 FAIL. See `Tech Review.xlsx` for full detail and REPORT.md Section 7 for grouped commentary. No FAIL results — no data or calculation fix was required before finalizing.

**Known issues or deviations an auditor should be aware of:**
- Link ratio ceiling warnings (96/107/12 for Incurred/Paid/Reported Count) are concentrated at the 11→23mo interval where large early-development WC LDFs naturally exceed the tech review's generic 1.05 ceiling — not a data issue.
- Minor negative development (documented in Phase 2/3) flows into several "non-decreasing" and "IBNR reversal" warnings — already accounted for, not new findings.
- Closure rate checks were skipped (no Closed Count triangle provided) — expected.

---

## Key Outputs

| File | Description |
|---|---|
| `REPORT.md` | Primary narrative deliverable |
| `output/complete-analysis.xlsx` | Primary numerical deliverable |
| `selections/Ultimates.xlsx` | Ultimate selections by category and accident year |
| `selections/Chain Ladder Selections - LDFs.xlsx` | LDF selections by measure |
| `selections/Chain Ladder Selections - Tail.xlsx` | Tail curve method selections |
