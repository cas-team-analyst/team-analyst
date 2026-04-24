# Replication Instructions

This document provides step-by-step instructions to reproduce the analysis results. A reviewer can follow these steps to validate the analysis without AI assistance.

---

## Overview

**Analysis:** Sample Reserving Analysis — Test Data  
**Valuation Date:** 01/01/2026  
**Prepared by:** Bryce  
**Date:** 04/24/2026

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

**Folders created:** raw-data/, processed-data/, selections/, scripts/, ultimates/

**Input data:** Triangle Examples 1.xlsx copied to raw-data/

---

## Step 2: Data Intake

**Input files used:**
- `raw-data/Triangle Examples 1.xlsx` — WC paid loss, incurred loss, reported count triangles (24 AYs × 24 ages, 2001–2024), plus payroll exposure by AY (sheets: Paid 1, Inc 1, Ct 1, Exposure)

**Scripts run:**
1. `scripts/1a-prep-data.py` — Read raw data and create canonical triangle format
   - **Customizations made:**
     - Sheet `Paid 1` and `Inc 1`: `header_row=2` (row 1 is label "Age of Evaluation"; row 2 is the ages row)
     - Sheet `Ct 1`: `header_row=1` (ages on first row directly)
     - Float-to-int cleanup for period labels (`2001.0` → `2001`) and age labels (`11.0` → `11`)
     - Exposure read via custom two-column parser (AY, Payroll); assigned to first dev age `11` for format compatibility
     - No closed count in source data; `Closed Count` measure omitted
   - **Output:** `processed-data/1_triangles.parquet` (924 rows: 300 Paid, 300 Incurred, 300 Count, 24 Exposure)

2. `scripts/1b-enhance-data.py` — Add LDFs, incremental values, cumulative data
   - **Output:** `processed-data/2_enhanced.parquet`

3. `scripts/1c-diagnostics.py` — Calculate diagnostic triangles (paid-to-incurred, severity, etc.)
   - **Output:** `processed-data/3_diagnostics.parquet`

4. `scripts/1d-averages-qa.py` — Calculate LDF averages (simple, weighted, exclude high/low)
   - **Output:** `processed-data/4_ldf_averages.parquet` (69 rows: 3 measures × 23 intervals)

**Data validation:** User confirmed data format on 04/24/2026

---

## Step 3: Chain Ladder LDF Selections

**Scripts run:**
1. `scripts/2a-chainladder-create-excel.py` — Create LDF selection workbook and per-measure context files
   - **Output:** `selections/Chain Ladder Selections - LDFs.xlsx`
   - **Context files exported:** `selections/chainladder-context-paid_loss.md`, `chainladder-context-incurred_loss.md`, `chainladder-context-reported_count.md`

**AI Selection Process:**
- Rules-based AI selector invoked 3 times (once per measure):
  - → `selections/chainladder-ai-rules-based-paid_loss.json` (23 selections)
  - → `selections/chainladder-ai-rules-based-incurred_loss.json` (22 selections)
  - → `selections/chainladder-ai-rules-based-reported_count.json` (23 selections)
- Open-ended AI selector invoked 3 times (once per measure):
  - → `selections/chainladder-ai-open-ended-paid_loss.json` (23 selections)
  - → `selections/chainladder-ai-open-ended-incurred_loss.json` (22 selections)
  - → `selections/chainladder-ai-open-ended-reported_count.json` (23 selections)

2. `scripts/2b-chainladder-update-selections.py` — Insert AI selections into Excel workbook
   - Populated "Rules-Based AI Selection" rows (68 total selections across 3 measures)
   - Populated "Open-Ended AI Selection" rows (68 total selections across 3 measures)

**USER ACTION - Manual Selections:**
- User reviewed on 04/24/2026. No manual overrides made.
- **All selections are from the Rules-Based AI Selection row.**

**To replicate:** Extract final LDF selections from the "User Selection" row in `selections/Chain Ladder Selections - LDFs.xlsx`. If blank, use "Rules-Based AI Selection" row. Do not re-run the AI selector.

---

## Step 4: Tail Factor Selections

**Scripts run:**
1. `scripts/2c-tail-methods-diagnostics.py` — Fit tail curves and generate diagnostics
   - **Output:** `processed-data/tail-scenarios.parquet` (29 scenarios across 3 measures)
   - Methods evaluated: Bondy, Modified Bondy (double dev, square ratio), Exp Dev Quick, Exp Dev Product, Double Exponential, McClenahan, Skurnick

2. `scripts/2d-tail-create-excel.py` — Create tail selection workbook and per-measure context files
   - **Output:** `selections/Chain Ladder Selections - Tail.xlsx`
   - **Context files exported:** `selections/tail-context-paid_loss.md`, `tail-context-incurred_loss.md`, `tail-context-reported_count.md`

**AI Selection Process:**
- Rules-based AI selector invoked 3 times (once per measure):
  - Paid Loss → `selections/tail-ai-rules-based-paid_loss.json` (tail=1.0039, Bondy, age 203)
  - Incurred Loss → `selections/tail-ai-rules-based-incurred_loss.json` (tail=1.0000, McClenahan, age 203)
  - Reported Count → `selections/tail-ai-rules-based-reported_count.json` (tail=1.0000, Bondy, age 143)
- Open-ended AI selector invoked 3 times (once per measure):
  - Paid Loss → `selections/tail-ai-open-ended-paid_loss.json` (tail=1.0181, Exp Dev Product, age 143)
  - Incurred Loss → `selections/tail-ai-open-ended-incurred_loss.json` (tail=1.0812, Double Exp, age 203)
  - Reported Count → `selections/tail-ai-open-ended-reported_count.json` (tail=1.0000, Bondy, age 203)

3. `scripts/2e-tail-update-selections.py` — Insert AI selections into Excel workbook
   - Populated "Rules-Based AI Selection" rows (3 selections)
   - Populated "Open-Ended AI Selection" rows (3 selections)

**USER ACTION - Manual Selections:**
- User reviewed on 04/24/2026. No manual overrides made.
- **All selections are from the Rules-Based AI Selection row.**

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
- User reviewed on 04/24/2026. No manual overrides made.
- **All selections are from the Rules-Based AI Selection columns.**

**To replicate:** Extract final ultimate selections from the "User Selection" column in `selections/Ultimates.xlsx`. If blank, use "Rules-Based AI Selection" column. Do not re-run the AI selector.

---

## Step 7: Final Analysis

**Scripts run:**
1. `scripts/6-create-complete-analysis.py` — Create consolidated analysis workbook
   - **Reads:** `ultimates/projected-ultimates.parquet`
   - **Reads:** `selections/Ultimates.xlsx` (User Selection → Rules-Based AI → Open-Ended AI → JSON → method fallback)
   - **Output:**
     - `output/selected-ultimates.xlsx` — Selected ultimates by accident year and measure
     - `output/post-method-series.xlsx` — Method indications time series
     - `output/post-method-triangles.xlsx` — Post-selection triangle data
     - `output/complete-analysis.xlsx` — Consolidated workbook (4 sheets: Sel-Exposure, Sel-Incurred, Sel-Paid, Sel-Reported)
     - `output/complete-analysis-values.xlsx` — Hard-coded values copy of complete-analysis.xlsx

2. `scripts/7-tech-review.py` — Run technical review checks
   - **Output:** `output/tech-review.xlsx`
   - **Issues flagged:** 2 PASS, 18 WARN (structural — triangle sheets not embedded in complete-analysis.xlsx; expected behavior for current script), 1 FAIL (measure sheets not embedded — structural limitation, not a numerical accuracy issue)

---

## Key Outputs

**Primary deliverables:**
- `REPORT.md` — Actuarial report with methodology, assumptions, results, and diagnostics
- `output/complete-analysis.xlsx` — Consolidated numerical results

**Supporting files:**
- `selections/Chain Ladder Selections - LDFs.xlsx` — LDF selections with AI reasoning
- `selections/Chain Ladder Selections - Tail.xlsx` — Tail factor selections with AI reasoning
- `selections/Ultimates.xlsx` — Ultimate selections with method indications and AI reasoning
- All scripts in `scripts/` folder can be re-run to reproduce results

---

## Notes

- IE (Initial Expected) and BF (Bornhuetter-Ferguson) ultimates were calculated using a fallback ELR derived from a 3-year rolling average of diagonal incurred losses per dollar of payroll exposure. No external ELR file was provided. This produced negative IBNR for 9 Incurred AYs — flagged in REPORT.md §11 for reviewer attention.
- Rules-based AI tail selection for Paid Loss selected Bondy at 1.0039 (age 203); open-ended selector chose Exp Dev Product at 1.0181 (age 143). The divergence is noted in REPORT.md §11 as an open question.
- All AI selectors (LDFs, tail factors, ultimates) used the Rules-Based selection as the final selection; no manual overrides were made.

