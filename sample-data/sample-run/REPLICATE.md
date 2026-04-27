# Replication Instructions

This document provides step-by-step instructions to reproduce the analysis results. A reviewer can follow these steps to validate the analysis without AI assistance.

---

## Overview

**Analysis:** Sample Run  
**Valuation Date:** [To be confirmed from data]  
**Prepared by:** Bryce  
**Date:** April 27, 2026

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
- `raw-data/Triangle Examples 1.xlsx` — WC loss triangles (Paid, Incurred, Reported Count) and payroll exposure. 24 AYs (2001–2024), 24 maturities (11–287 months).

**Scripts run:**
1. `scripts/1a-prep-data.py` — Read raw data and create canonical triangle format
   - **Customizations made:** Added `n_header_rows` parameter to `read_triangle_data()` to handle two header formats (loss sheets use 2 header rows; count sheet uses 1). Implemented `read_and_process_triangles()` to read sheets Paid 1, Inc 1, Ct 1, and Exposure and combine into long format.
   - **Output:** `processed-data/1_triangles.parquet` (924 rows)

2. `scripts/1b-enhance-data.py` — Add LDFs, incremental values, cumulative data
   - **Customizations made:** None
   - **Output:** `processed-data/2_enhanced.parquet`

3. `scripts/1c-diagnostics.py` — Calculate diagnostic triangles (paid-to-incurred, severity, etc.)
   - **Customizations made:** None
   - **Output:** `processed-data/3_diagnostics.parquet`

4. `scripts/1d-averages-qa.py` — Calculate LDF averages (simple, weighted, exclude high/low, 3/5/10yr windows)
   - **Customizations made:** None
   - **Output:** `processed-data/4_ldf_averages.parquet`

**IE/BF approach:** No ELR file provided. User confirmed use of exposure-based fallback (3-year rolling average of paid loss per dollar of payroll) on April 27, 2026.

**Data validation:** User confirmed data format on April 27, 2026.

---

## Step 3: Chain Ladder LDF Selections

**Scripts run:**
1. `scripts/2a-chainladder-create-excel.py` — Create LDF selection workbook
   - **Output:** `selections/Chain Ladder Selections - LDFs.xlsx`

**AI Selection Process:**
- Rules-based AI selector reviewed the workbook and made selections → `selections/chainladder-ai-rules-based.json`
- Open-ended AI selector independently made selections → `selections/chainladder-ai-open-ended.json`

2. `scripts/2b-chainladder-update-selections.py` — Insert AI selections into Excel workbook
   - Populated "Rules-Based AI Selection" rows with values from `chainladder-ai-rules-based.json`
   - Populated "Open-Ended AI Selection" rows with values from `chainladder-ai-open-ended.json`

**USER ACTION - Manual Selections:**
[If user made manual selections, list them here]
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
1. `scripts/6-create-complete-analysis.py` — Create consolidated analysis workbook
   - **Reads:** `ultimates/projected-ultimates.parquet`
   - **Reads:** `selections/Ultimates.xlsx` (User Selection → Rules-Based AI → Open-Ended AI → JSON → method fallback)
   - **Output:** 
     - `output/selected-ultimates.xlsx`
     - `output/post-method-series.xlsx`
     - `output/post-method-triangles.xlsx`
     - `output/complete-analysis.xlsx`

2. `scripts/7-tech-review.py` — Run technical review checks
   - **Output:** `output/tech-review.[format]`
   - **Issues flagged:** [List any warnings or errors, or "None - all checks passed"]

---

## Key Outputs

**Primary deliverables:**
- `REPORT.md` — Actuarial report with methodology, assumptions, results, and diagnostics
- `output/complete-analysis.xlsx` — Consolidated numerical results

**Supporting files:**
- `selections/Chain Ladder Selections - LDFs.xlsx` — LDF selections with reasoning
- `selections/Chain Ladder Selections - Tail.xlsx` — Tail factor selections with reasoning
- `selections/Ultimates.xlsx` — Ultimate selections with method indications
- All scripts in `scripts/` folder can be re-run to reproduce results

---

## Notes

[Add any additional context, special considerations, or known issues]

