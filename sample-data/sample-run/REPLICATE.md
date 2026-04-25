# Replication Instructions

This document provides step-by-step instructions to reproduce the analysis results. A reviewer can follow these steps to validate the analysis without AI assistance.

---

## Overview

**Analysis:** Sample Run — Workers Compensation  
**Valuation Date:** 12/31/2024  
**Prepared by:** Bryce  
**Date:** 04/25/2026

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
- `raw-data/Triangle Examples 1.xlsx` — CAS sample WC data; sheets: Paid 1 (paid loss triangle), Inc 1 (incurred loss triangle), Ct 1 (reported count triangle), Exposure (annual payroll by AY)

**Scripts run:**
1. `scripts/1a-prep-data.py` — Read raw data and create canonical triangle format
   - **Customizations made:** (1) File path set to `Triangle Examples 1.xlsx`; (2) Paid/Incurred sheets use header_row=2 (row 1 is 'Age of Evaluation' label, row 2 has ages); Count sheet uses header_row=1 (ages in row 1); (3) `normalize_numeric_labels()` helper added to convert float-string labels ('2001.0'→'2001', '11.0'→'11'); (4) Exposure read with pandas directly (two-column series, not a triangle) and assigned placeholder age='11'
   - **Output:** `processed-data/1_triangles.parquet`

2. `scripts/1b-enhance-data.py` — Add LDFs, incremental values, cumulative data
   - **Output:** `processed-data/2_enhanced.parquet`

3. `scripts/1c-diagnostics.py` — Calculate diagnostic triangles (paid-to-incurred, severity, etc.)
   - **Output:** `processed-data/3_diagnostics.parquet`

4. `scripts/1d-averages-qa.py` — Calculate LDF averages (simple, weighted, exclude high/low)
   - **Output:** `processed-data/4_ldf_averages.parquet`

**Data validation:** Confirmed by Bryce — 04/25/2026

---

## Step 3: Chain Ladder LDF Selections

**Scripts run:**
1. `scripts/2a-chainladder-create-excel.py` — Create LDF selection workbook
   - **Output:** `selections/Chain Ladder Selections - LDFs.xlsx`

**AI Selection Process:**
- Rules-based AI selector: per-measure JSON files at `selections/chainladder-ai-rules-based-{measure}.json`
- Open-ended AI selector: per-measure JSON files at `selections/chainladder-ai-open-ended-{measure}.json`

2. `scripts/2b-chainladder-update-selections.py` — Insert AI selections into Excel workbook
   - Populated "Rules-Based AI Selection" rows with values from `chainladder-ai-rules-based.json`
   - Populated "Open-Ended AI Selection" rows with values from `chainladder-ai-open-ended.json`

**Manual Overrides:** None. All selections are from the Rules-Based AI Selection row.

**To replicate:** Use the Rules-Based AI Selection row in `selections/Chain Ladder Selections - LDFs.xlsx`. Do not re-run the AI selector.

---

## Step 4: Tail Factor Selections

**Scripts run:**
1. `scripts/2c-tail-methods-diagnostics.py` — Fit tail curves and generate diagnostics
   - **Output:** `processed-data/tail-scenarios.parquet`

2. `scripts/2d-tail-create-excel.py` — Create tail selection workbook
   - **Output:** `selections/Chain Ladder Selections - Tail.xlsx`

**AI Selection Process:**
- Rules-based: `selections/tail-ai-rules-based-{measure}.json` (Paid: Bondy 1.0039; Incurred: double_exp 1.0216; Count: Bondy 1.0000)
- Open-ended: `selections/tail-ai-open-ended-{measure}.json` (Paid: exp_dev_quick_exact_last 1.0472; Incurred: double_exp 1.0216; Count: Bondy 1.0000)

3. `scripts/2e-tail-update-selections.py` — Insert AI selections into Excel workbook
   - Populated "Rules-Based AI Selection" row with values from `tail-ai-rules-based.json`
   - Populated "Open-Ended AI Selection" row with values from `tail-ai-open-ended.json`

**Manual Overrides:** None. All selections are from the Rules-Based AI Selection row.

**To replicate:** Use the Rules-Based AI Selection row in `selections/Chain Ladder Selections - Tail.xlsx`. Do not re-run the AI selector.

---

## Step 5: Method Ultimates

**Scripts run:**
1. `scripts/2f-chainladder-ultimates.py` — Calculate Chain Ladder ultimates using selected LDFs and tail factors
   - **Reads:** `selections/Chain Ladder Selections - LDFs.xlsx` (User Selection → Rules-Based AI → Open-Ended AI)
   - **Reads:** `selections/Chain Ladder Selections - Tail.xlsx` (User Selection → Rules-Based AI → Open-Ended AI)
   - **Output:** `ultimates/projected-ultimates.parquet` (includes ultimate_cl, ibnr_cl columns)

2. `scripts/3-ie-ultimates.py` — Calculate Initial Expected ultimates (if ELR file provided)
   - **Status:** Ran — fallback ELR (3-yr rolling avg of incurred per payroll)
   - **Output:** Added ultimate_ie column to `ultimates/projected-ultimates.parquet`

3. `scripts/4-bf-ultimates.py` — Calculate Bornhuetter-Ferguson ultimates
   - **Status:** Ran — used fallback ELR from IE step
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

**Manual Overrides:** None. All selections are from the Rules-Based AI Selection columns.

**To replicate:** Use the Rules-Based AI Selection column in `selections/Ultimates.xlsx`. Do not re-run the AI selector.

---

## Step 7: Final Analysis

**Scripts run:**
1. `scripts/6-create-complete-analysis.py` — Create consolidated analysis workbook
   - **Reads:** `ultimates/projected-ultimates.parquet`
   - **Reads:** `selections/Ultimates.xlsx` (User Selection → Rules-Based AI → Open-Ended AI → JSON → method fallback)
   - **Output:** `output/Complete Analysis.xlsx`, `output/Complete Analysis - Values Only.xlsx`

2. `scripts/7-tech-review.py` — Run technical review checks
   - **Output:** `output/Tech Review.xlsx`
   - **Issues flagged:** 33 warnings, 0 failures. Key items: paid tail divergence (1.004 vs 1.047); paid sel > incurred sel for AYs 2017/2021-2023; AY2010 Paid sel outside method range; IE fallback ELR negative IBNR in volatile AYs; non-monotone severity/frequency trends.

---

## Key Outputs

**Primary deliverables:**
- `REPORT.md` — Actuarial report with methodology, assumptions, results, and diagnostics
- `output/Complete Analysis.xlsx` — Consolidated numerical results (with formulas)
- `output/Complete Analysis - Values Only.xlsx` — Same, values only (for portability)

**Supporting files:**
- `selections/Chain Ladder Selections - LDFs.xlsx` — LDF selections with reasoning
- `selections/Chain Ladder Selections - Tail.xlsx` — Tail factor selections with reasoning
- `selections/Ultimates.xlsx` — Ultimate selections with method indications
- All scripts in `scripts/` folder can be re-run to reproduce results

---

## Notes

[Add any additional context, special considerations, or known issues]

