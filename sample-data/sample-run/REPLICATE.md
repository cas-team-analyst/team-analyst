# Replication Instructions

This document provides step-by-step instructions to reproduce the analysis results. A reviewer can follow these steps to validate the analysis without AI assistance.

---

## Overview

**Analysis:** Sample Run — Workers Compensation  
**Valuation Date:** ~November 30, 2024  
**Prepared by:** Bryce  
**Date:** 2026-04-30

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

**Interaction mode selected:** Fully Automatic

---

## Step 2: Data Intake

**Input files used:**
- `raw-data/Triangle Examples 1.xlsx` — WC loss triangle data file. Sheets: Paid 1 (Paid Loss), Inc 1 (Incurred Loss), Ct 1 (Reported Count), Exposure (Payroll by AY), Tri 1 (metadata). AY 2001–2024, ages 11–287 months.

**Scripts run:**
1. `scripts/1a-load-and-validate.py` — Read raw data and create canonical triangle format
   - **Customizations made:**
     - Implemented `read_triangle_data()` with flexible header detection (handles extra "Age of Evaluation" label row in Paid/Incurred sheets; absent in Count sheet)
     - Ages stored as string labels matching file's non-standard 11-month initial age
     - Count sheet classified as Reported Count (increasing/stabilizing pattern; no "Closed" qualifier)
     - Exposure read via `data_only=True` to resolve Excel formula values
   - **Output:** `processed-data/1_triangles.parquet` (924 rows)

2. `scripts/1b-calculate-ldfs.py` — Add LDFs, incremental values, cumulative data
   - **Customizations made:** None
   - **Output:** `processed-data/2_enhanced.parquet`

3. `scripts/1c-diagnostics.py` — Calculate diagnostic triangles (paid-to-incurred, severity, etc.)
   - **Customizations made:** None
   - **Output:** `processed-data/3_diagnostics.parquet`

4. `scripts/1d-ldf-averages.py` — Calculate LDF averages (simple, weighted, exclude high/low)
   - **Customizations made:** None
   - **Output:** `processed-data/4_ldf_averages.parquet`

**Data validation:** User confirmed data format on 2026-04-30

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

**USER ACTION - Manual Selections:** No manual overrides made. All selections are from the Rules-Based AI Selection row.

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

**Note:** Agent output files were named `tail-ai-rules-based-*.json` / `tail-ai-open-ended-*.json`; copied to `tail-curve-ai-rules-based-*.json` / `tail-curve-ai-open-ended-*.json` to match the pattern expected by `2e-tail-update-selections.py`.

**USER ACTION - Manual Selections:** No manual overrides made. All selections are from the Rules-Based AI Selection row (`exp_dev_product` for all three measures).

**To replicate:** Extract final tail methods from the "User Selection" row in `selections/Chain Ladder Selections - Tail.xlsx`. If blank, use "Rules-Based AI Selection" row. Do not re-run the AI selector.

---

## Step 5: Method Ultimates

**Scripts run:**
1. `scripts/2f-chainladder-ultimates.py` — Calculate Chain Ladder ultimates using selected LDFs and tail factors
   - **Reads:** `selections/Chain Ladder Selections - LDFs.xlsx` (User Selection → Rules-Based AI → Open-Ended AI)
   - **Reads:** `selections/Chain Ladder Selections - Tail.xlsx` (User Selection → Rules-Based AI → Open-Ended AI)
   - **Output:** `ultimates/projected-ultimates.parquet` (includes ultimate_cl, ibnr_cl columns)

2. `scripts/3-ie-ultimates.py` — Calculate Initial Expected ultimates
   - **Status:** Ran — used fallback ELR (3-year rolling average of empirical incurred loss / payroll). No ELR file was provided.
   - **Output:** Added `ultimate_ie`, `ibnr_ie` columns to `ultimates/projected-ultimates.parquet`

3. `scripts/4-bf-ultimates.py` — Calculate Bornhuetter-Ferguson ultimates
   - **Status:** Ran — BF calculated from CL CDFs and IE ELR fallback.
   - **Output:** Added `ultimate_bf`, `ibnr_bf` columns to `ultimates/projected-ultimates.parquet`

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

**USER ACTION - Manual Selections:** No manual overrides made. All selections are from the Rules-Based AI Selection columns.

**To replicate:** Extract final ultimate selections from the "User Selection" column in `selections/Ultimates.xlsx`. If blank, use "Rules-Based AI Selection" column. Do not re-run the AI selector.

---

## Step 7: Final Analysis

**Scripts run:**
1. `scripts/5c-summary-indications.py` — Generate headline indications summary
   - **Output:** `selections/summary-indications.json`

2. `scripts/6-analysis-create-excel.py` — Create consolidated analysis workbook
   - **Reads:** `ultimates/projected-ultimates.parquet`, `selections/Ultimates.xlsx`
   - **Output:** `Analysis.xlsx` (15 sheets: Loss Selection, Count Selection, CL triangles, diagnostics, notes)

3. `scripts/7-tech-review.py` — Run technical review checks
   - **Output:** `Tech Review.xlsx`
   - **Result:** 15 PASS, 16 WARN (all structural/expected), 0 FAIL
   - **Notable WARNs:** AY 2007 Loss ultimate flagged as outlier (>10× median) — confirmed as large-loss year, not an error. Count IBNR slight negatives in 7 mature periods — within tolerance.

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

