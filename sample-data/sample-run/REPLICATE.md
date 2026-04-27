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

2. `scripts/3-ie-ultimates.py` — Calculate Initial Expected ultimates
   - **Status:** Ran — used exposure-based fallback ELR (3-year rolling average of incurred loss per payroll; confirmed April 27, 2026)
   - **Output:** Added `ultimate_ie`, `ibnr_ie` columns to `ultimates/projected-ultimates.parquet`

3. `scripts/4-bf-ultimates.py` — Calculate Bornhuetter-Ferguson ultimates
   - **Status:** Ran — used CL ultimates and IE expected rates from above
   - **Output:** Added `ultimate_bf`, `ibnr_bf` columns to `ultimates/projected-ultimates.parquet`

---

## Step 6: Ultimate Selections

**Scripts run:**
1. `scripts/5a-ultimates-create-excel.py` — Create ultimates selection workbook
   - **Output:** `selections/Ultimates.xlsx` (sheets: Losses, Counts)
   - **Context files exported:** `selections/ultimates-context-loss.md`, `selections/ultimates-context-count.md`

**AI Selection Process:**
- Rules-based AI selector reviewed both context files → `selections/ultimates-ai-rules-based-loss.json`, `selections/ultimates-ai-rules-based-count.json`
- Open-ended AI selector independently reviewed both context files → `selections/ultimates-ai-open-ended-loss.json`, `selections/ultimates-ai-open-ended-count.json`
- Both selectors agree on AYs 2001–2022 (Paid CL for Loss; Reported Count CL for Count)
- Divergence on 2023 and 2024 (Loss only): Rules-Based selected Paid CL (higher); Open-Ended selected a lower BF-based ultimate. Difference: ~$1.5M on 2023, ~$1.4M on 2024.

2. `scripts/5b-ultimates-update-selections.py` — Insert AI selections into Excel workbook
   - Populated Rules-Based AI Selection columns (48 updates across Loss + Count sheets)
   - Populated Open-Ended AI Selection columns (48 updates across Loss + Count sheets)

**USER ACTION - Manual Selections:**
[If user made manual selections, list them here]
- **Category:** [Loss/Count], **Period:** [year], **Selected Ultimate:** [value], **Reason:** [explanation]
- **If no manual overrides:** All selections are from the Rules-Based AI Selection column.

**To replicate:** Extract final ultimates from the "User Selection" column in `selections/Ultimates.xlsx`. If blank, use "Rules-Based AI Selection" column. Do not re-run the AI selector.


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
1. `scripts/6-create-complete-analysis.py` — Create consolidated analysis workbook (run April 27, 2026)
   - **Reads:** `ultimates/projected-ultimates.parquet`
   - **Reads:** `selections/Ultimates.xlsx` (User Selection → Rules-Based AI; 48 selections loaded)
   - **Reads:** `selections/Chain Ladder Selections - LDFs.xlsx`, `selections/Chain Ladder Selections - Tail.xlsx`
   - **Reads:** `processed-data/2_enhanced.parquet`, `processed-data/4_ldf_averages.parquet`
   - **Output:**
     - `output/Analysis.xlsx` — Full workbook with cross-sheet formulas (open in Excel)
     - `output/Analysis - Values Only.xlsx` — Plain computed values (safe for programmatic reads)
   - **Headline indications:** Total unpaid $5,090,086 (IBNR $3,241,545 + case $1,848,541); total ultimate $48,706,481

2. `scripts/7-tech-review.py` — Run technical review checks (run April 27, 2026)
   - **Output:** `output/Tech Review.xlsx`
   - **Result:** 17 PASS / 18 WARN / 1 FAIL
   - **Expected FAIL:** Measure sheets (Incurred Loss, Paid Loss, etc.) not present in Values Only file — by design; see Analysis.xlsx for full sheets.
   - **Key warnings:** (1) Negative IBNR on 5 mature AYs — case reserve takedown artifact, no action needed. (2) AY 2007 severity outlier — large-loss year, flagged for reviewer. (3) X-to-Ult reversals in Incurred (31) and Count (6) — normal for WC case reserve reductions and count reopenings. (4) AYs 2023–2024 method divergence — documented in REPORT.md Section 11.

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

