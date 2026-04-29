# Replication Instructions

This document provides step-by-step instructions to reproduce the analysis results. A reviewer can follow these steps to validate the analysis without AI assistance.

---

## Overview

**Analysis:** Sample Run  
**Valuation Date:** [To be confirmed from data]  
**Prepared by:** John Doe  
**Date:** 04/29/2026

**Key principle:** This analysis used AI selectors to make actuarial selections. Manual overrides were applied where noted. To replicate, extract the final selections from the Excel files rather than re-running the AI selection process.

---

## Step 1: Project Setup

**Folders created:**
- `raw-data/` — Original input files
- `processed-data/` — Cleaned triangles and diagnostics
- `selections/` — Selection workbooks and JSON files
- `scripts/` — Python scripts
- `ultimates/` — Method-specific ultimate outputs
- `output/` — Final analysis workbooks

**Standard documents:**
- `PROGRESS.md` — Workflow checklist
- `REPLICATE.md` — This document
- `REPORT.md` — Actuarial report

**Interaction mode selected:** Pause for Selections

---

## Step 2: Data Intake

**Input files used:**
- `raw-data/Triangle Examples 1.xlsx` — WC triangle file; sheets: Paid 1, Inc 1, Ct 1, Exposure, Tri 1 (metadata). 36 KB, last modified 04/29/2026.

**Scripts run:**
1. `scripts/1a-load-and-validate.py` — Read raw data and create canonical triangle format
   - **Customizations made:** Implemented `read_triangle_data()` to handle two Excel header formats (Paid/Incurred have an extra "Age of Evaluation" label row; Count sheet does not). Ages read as integer months and stored as string ordered categoricals. Exposure extracted from 2-column sheet using `data_only=True`. Count triangle classified as Reported Count. Fixed truncated `read_and_process_expected_loss_rates()` return statement.
   - **Output:** `processed-data/1_triangles.parquet` (924 rows: 300 Paid Loss, 300 Incurred Loss, 300 Reported Count, 24 Exposure)

2. `scripts/1b-calculate-ldfs.py` — Add LDFs, incremental values, cumulative data
   - **Output:** `processed-data/2_enhanced.parquet` (924 rows, 828 with LDFs)

3. `scripts/1c-diagnostics.py` — Calculate diagnostic triangles (paid-to-incurred, severity, etc.)
   - **Output:** `processed-data/3_diagnostics.parquet`

4. `scripts/1d-ldf-averages.py` — Calculate LDF averages (simple, weighted, exclude high/low)
   - **Output:** `processed-data/4_ldf_averages.parquet` (69 summary rows across 3 measures × 23 intervals)

**Data validation:** User confirmed data format on 04/29/2026

**ELR approach:** Fallback approximation — diagonal loss per dollar of exposure, 3-year rolling average. No prior LDF or tail factor selections available.

---

## Step 3: Chain Ladder LDF Selections

**Scripts run:**
1. `scripts/2a-chainladder-create-excel.py` — Created LDF selection workbook and exported per-measure context files
   - **Output:** `selections/Chain Ladder Selections - LDFs.xlsx`
   - Context files exported: `selections/chainladder-context-incurred_loss.md`, `chainladder-context-paid_loss.md`, `chainladder-context-reported_count.md`

**AI Selection Process:**
- Rules-based selector read all 3 context files, applied the rules-based framework, wrote: `selections/chainladder-ai-rules-based-incurred_loss.json`, `-paid_loss.json`, `-reported_count.json` (69 total selections across 3 measures × 23 intervals)
- Open-ended selector independently read all 3 context files, wrote: `selections/chainladder-ai-open-ended-incurred_loss.json`, `-paid_loss.json`, `-reported_count.json` (57 selections — stops at 227 month cutoff vs. 275 for rules-based)
- Bug fix applied to `2b-chainladder-update-selections.py`: added skip for cutoff marker records (no `selection` key) in both `update_sheet()` and `update_ai_sheet()`

2. `scripts/2b-chainladder-update-selections.py` — Populated "Rules-Based AI Selection" and "Open-Ended AI Selection" rows in all 3 measure sheets

**USER ACTION - Manual Selections:**
All selections are from Rules-Based AI Selection row — no manual overrides recorded as of 04/29/2026. User review in progress.
- **Measure:** [name], **Interval:** [age-age], **Selected LDF:** [value], **Reason:** [explanation]
- [Additional manual overrides...]
- **If no manual overrides:** All selections are from the Rules-Based AI Selection row.

**To replicate:** Extract final LDF selections from the "User Selection" row in `selections/Chain Ladder Selections - LDFs.xlsx`. If blank, use "Rules-Based AI Selection" row. Do not re-run the AI selector.

---

## Step 4: Tail Factor Selections

**Scripts run:**
1. `scripts/2c-tail-methods-diagnostics.py` — Fit tail curves and generate diagnostics
   - **Output:** `processed-data/tail-scenarios.parquet`

2. `scripts/2d-tail-create-excel.py` — Create tail selection workbook
   - **Output:** `selections/Chain Ladder Selections - Tail.xlsx`

**AI Selection Process:**
- Rules-based AI selector reviewed curve fits and made tail selections → `selections/tail-ai-rules-based.json`
- Open-ended AI selector independently made tail selections → `selections/tail-ai-open-ended.json`

3. `scripts/2e-tail-update-selections.py` — Insert AI selections into Excel workbook
   - Populated "Rules-Based AI Selection" row with values from `tail-ai-rules-based.json`
   - Populated "Open-Ended AI Selection" row with values from `tail-ai-open-ended.json`

**USER ACTION - Manual Selections:**
[If user made manual selections, list them here]
- **Measure:** [name], **Cutoff Age:** [age], **Tail Factor:** [value], **Method:** [curve type], **Reason:** [explanation]
- [Additional manual overrides...]
- **If no manual overrides:** All selections are from the Rules-Based AI Selection row.

**To replicate:** Extract final tail factors from the "User Selection" row in `selections/Chain Ladder Selections - Tail.xlsx`. If blank, use "Rules-Based AI Selection" row. Do not re-run the AI selector.

---

## Step 5: Method Ultimates

**Scripts run:**
1. `scripts/2f-chainladder-ultimates.py` — Calculate Chain Ladder ultimates using selected LDFs and tail factors
   - **Reads:** `selections/Chain Ladder Selections - LDFs.xlsx` (User Selection → Rules-Based AI → Open-Ended AI)
   - **Reads:** `selections/Chain Ladder Selections - Tail.xlsx` (User Selection → Rules-Based AI → Open-Ended AI)
   - **Output:** `ultimates/projected-ultimates.parquet` (includes ultimate_cl, ibnr_cl columns)

2. `scripts/3-ie-ultimates.py` — Calculate Initial Expected ultimates (if ELR file provided)
   - **Status:** [Ran / Skipped - reason]
   - **Output:** Added ultimate_ie column to `ultimates/projected-ultimates.parquet`

3. `scripts/4-bf-ultimates.py` — Calculate Bornhuetter-Ferguson ultimates (if ELR file provided)
   - **Status:** [Ran / Skipped - reason]
   - **Output:** Added ultimate_bf column to `ultimates/projected-ultimates.parquet`

---

## Step 6: Ultimate Selections

**Scripts run:**
1. `scripts/5a-ultimates-create-excel.py` — Create ultimates selection workbook
   - **Output:** `selections/Ultimates.xlsx`

**AI Selection Process:**
- Rules-based AI selector reviewed method indications and made ultimate selections → `selections/ultimates-ai-rules-based.json`
- Open-ended AI selector independently made ultimate selections → `selections/ultimates-ai-open-ended.json`

2. `scripts/5b-ultimates-update-selections.py` — Insert AI selections into Excel workbook
   - Populated "Rules-Based AI Selection" columns with values from `ultimates-ai-rules-based.json`
   - Populated "Open-Ended AI Selection" columns with values from `ultimates-ai-open-ended.json`

**USER ACTION - Manual Selections:**
[If user made manual selections, list them here]
- **Measure:** [name], **Period:** [AY], **Selected Ultimate:** [value], **Reason:** [explanation]
- [Additional manual overrides...]
- **If no manual overrides:** All selections are from the Rules-Based AI Selection columns.

**To replicate:** Extract final ultimate selections from the "User Selection" column in `selections/Ultimates.xlsx`. If blank, use "Rules-Based AI Selection" column. Do not re-run the AI selector.

---

## Step 7: Final Analysis

**Scripts run:**
1. `scripts/6-analysis-create-excel.py` — Create consolidated analysis workbook
   - **Reads:** `ultimates/projected-ultimates.parquet`
   - **Reads:** `selections/Ultimates.xlsx` (User Selection → Rules-Based AI → Open-Ended AI → JSON → method fallback)
   - **Output:** 
     - `selected-ultimates.xlsx`
     - `post-method-series.xlsx`
     - `post-method-triangles.xlsx`
     - `Complete Analysis.xlsx`

2. `scripts/7-tech-review.py` — Run technical review checks
   - **Output:** `tech-review.[format]`
   - **Issues flagged:** [List any warnings or errors, or "None - all checks passed"]

---

## Key Outputs

**Primary deliverables:**
- `REPORT.md` — Actuarial report with methodology, assumptions, results, and diagnostics
- `Complete Analysis.xlsx` — Consolidated numerical results

**Supporting files:**
- `selections/Chain Ladder Selections - LDFs.xlsx` — LDF selections with reasoning
- `selections/Chain Ladder Selections - Tail.xlsx` — Tail factor selections with reasoning
- `selections/Ultimates.xlsx` — Ultimate selections with method indications
- All scripts in `scripts/` folder can be re-run to reproduce results

---

## Notes

[Add any additional context, special considerations, or known issues]

