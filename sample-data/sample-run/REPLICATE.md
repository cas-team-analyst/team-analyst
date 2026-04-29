# Replication Instructions

This document provides step-by-step instructions to reproduce the analysis results. A reviewer can follow these steps to validate the analysis without AI assistance.

---

## Overview

**Analysis:** Sample Run  
**Valuation Date:** [To be confirmed from data]  
**Prepared by:** Bryce  
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

**Interaction mode selected:** Fully Automatic

---

## Step 2: Data Intake

**Input files used:**
- `raw-data/Triangle Examples 1.xlsx` — Source triangle file containing Paid Loss (sheet "Paid 1"), Incurred Loss (sheet "Inc 1"), Reported Count (sheet "Ct 1"), and Exposure/Payroll (sheet "Exposure"). WC line, AY 2001–2024, dev ages 11–287 months.

**Scripts run:**
1. `scripts/1a-load-and-validate.py` — Read raw data and create canonical triangle format
   - **Customizations made:** Implemented `read_triangle_data()` for wide-to-long conversion; handled 2-row header layout (Paid/Incurred) vs. 1-row (Count); classified Ct 1 as Reported Count; exposure loaded via pandas data_only. No outlier exclusions.
   - **Output:** `processed-data/1_triangles.parquet` (924 rows)

2. `scripts/1b-calculate-ldfs.py` — Add LDFs, incremental values, cumulative data
   - **Output:** `processed-data/2_enhanced.parquet` (828 rows with LDFs)

3. `scripts/1c-diagnostics.py` — Calculate diagnostic triangles (paid-to-incurred, severity, etc.)
   - **Output:** `processed-data/3_diagnostics.parquet`

4. `scripts/1d-ldf-averages.py` — Calculate LDF averages (simple, weighted, exclude high/low)
   - **Output:** `processed-data/4_ldf_averages.parquet`

**Data validation:** User confirmed data format on 04/29/2026

---

## Step 3: Chain Ladder LDF Selections

**Scripts run:**
1. `scripts/2a-chainladder-create-excel.py` — Create LDF selection workbook
   - **Output:** `selections/Chain Ladder Selections - LDFs.xlsx`

**AI Selection Process:**
- Rules-based AI selector made selections for all 3 measures (23 intervals each) → `selections/chainladder-ai-rules-based-incurred_loss.json`, `-paid_loss.json`, `-reported_count.json`
- Open-ended AI selector independently made selections → `selections/chainladder-ai-open-ended-incurred_loss.json`, `-paid_loss.json`, `-reported_count.json`

2. `scripts/2b-chainladder-update-selections.py` — Insert AI selections into Excel workbook
   - Populated "Rules-Based AI Selection" rows (69 selections across 3 measures)
   - Populated "Open-Ended AI Selection" rows (69 selections across 3 measures)

**If no manual overrides:** All selections are from the Rules-Based AI Selection row.

**To replicate:** Extract final LDF selections from the "User Selection" row in `selections/Chain Ladder Selections - LDFs.xlsx`. If blank, use "Rules-Based AI Selection" row. Do not re-run the AI selector.

---

## Step 4: Tail Factor Selections

**Scripts run:**
1. `scripts/2c-tail-methods-diagnostics.py` — Fit tail curves and generate diagnostics
   - **Output:** `processed-data/tail-scenarios.parquet`

2. `scripts/2d-tail-create-excel.py` — Create tail selection workbook
   - **Output:** `selections/Chain Ladder Selections - Tail.xlsx`

**Tail selections (rules-based):** Incurred Loss 1.0119 (Bondy, age 143), Paid Loss 1.0039 (Bondy, age 143), Reported Count 1.0000 (age 143)
**Tail selections (open-ended):** Incurred Loss 1.0251 (double-exp, age 143), Paid Loss 1.0039 (Bondy, age 143), Reported Count 1.0000 (age 143)

3. `scripts/2e-tail-update-selections.py` — Insert AI selections into Excel workbook (3 rules-based + 3 open-ended)

**If no manual overrides:** All selections are from the Rules-Based AI Selection row.

**To replicate:** Extract final tail factors from the "User Selection" row in `selections/Chain Ladder Selections - Tail.xlsx`. If blank, use "Rules-Based AI Selection" row. Do not re-run the AI selector.

---

## Step 5: Method Ultimates

**Scripts run:**
1. `scripts/2f-chainladder-ultimates.py` — Calculate Chain Ladder ultimates using selected LDFs and tail factors
   - **Reads:** `selections/Chain Ladder Selections - LDFs.xlsx` (User Selection → Rules-Based AI → Open-Ended AI)
   - **Reads:** `selections/Chain Ladder Selections - Tail.xlsx` (User Selection → Rules-Based AI → Open-Ended AI)
   - **Output:** `ultimates/projected-ultimates.parquet` (includes ultimate_cl, ibnr_cl columns)

2. `scripts/3-ie-ultimates.py` — Calculate Initial Expected ultimates
   - **Status:** Ran with fallback ELR (no ELR file provided; used 3-year rolling avg of diagonal loss ÷ payroll)
   - **Output:** Added `ultimate_ie` column to `ultimates/projected-ultimates.parquet`

3. `scripts/4-bf-ultimates.py` — Calculate Bornhuetter-Ferguson ultimates
   - **Status:** Ran (built on CL CDFs + IE a priori rates)
   - **Output:** Added `ultimate_bf` column to `ultimates/projected-ultimates.parquet`

---

## Step 6: Ultimate Selections

**Scripts run:**
1. `scripts/5a-ultimates-create-excel.py` — Create ultimates selection workbook
   - **Output:** `selections/Ultimates.xlsx`

**Rules-based selections:** Paid CL for Loss AYs 2001–2018; Paid BF for Loss AYs 2019–2024; Reported CL for Count AYs 2001–2023; Reported BF for Count AY 2024.
**Open-ended selections:** Paid CL uniformly for all Loss AYs; Reported CL uniformly for all Count AYs.

2. `scripts/5b-ultimates-update-selections.py` — Populated Rules-Based AI and Open-Ended AI columns in Losses and Counts sheets (48 total selections each)

**If no manual overrides:** All selections are from the Rules-Based AI Selection columns.

**To replicate:** Extract final ultimate selections from the "User Selection" column in `selections/Ultimates.xlsx`. If blank, use "Rules-Based AI Selection" column. Do not re-run the AI selector.

---

## Step 7: Final Analysis

**Scripts run:**
1. `scripts/6-analysis-create-excel.py` — Create consolidated analysis workbook
   - **Reads:** `ultimates/projected-ultimates.parquet`, `selections/Ultimates.xlsx`
   - **Output:** `Analysis.xlsx` (Loss Selection, Count Selection, CL triangle sheets, Diagnostics, Notes)

2. `scripts/7-tech-review.py` — Run technical review checks
   - **Output:** `Tech Review.xlsx`
   - **Issues flagged:** 1 FAIL (negative IBNR vs. current incurred in AYs 2001, 2002, 2006, 2012); 1 WARN (AY 2007 large-loss outlier); 1 WARN (minor negative count IBNRs within tolerance)

---

## Key Outputs

**Primary deliverables:**
- `REPORT.md` — Actuarial report with methodology, assumptions, results, and diagnostics
- `Analysis.xlsx` — Consolidated numerical results (Loss/Count selections, CL triangles, diagnostics)

**Supporting files:**
- `selections/Chain Ladder Selections - LDFs.xlsx` — LDF selections with AI reasoning (rules-based + open-ended)
- `selections/Chain Ladder Selections - Tail.xlsx` — Tail factor selections with reasoning
- `selections/Ultimates.xlsx` — Ultimate selections by AY (Losses and Counts sheets)
- `Tech Review.xlsx` — Automated reasonableness checks output
- `ultimates/projected-ultimates.parquet` — All method ultimates by period/measure (CL, IE, BF)
- All scripts in `scripts/` folder can be re-run to reproduce results

---

## Notes

[Add any additional context, special considerations, or known issues]

