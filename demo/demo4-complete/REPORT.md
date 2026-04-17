# Reserving Analysis — Working Draft

**Analysis:** Canonical Demo — All Lines Combined  
**Valuation Date:** 12/31/2024  
**Draft Version:** v0.1 — For Peer Review  
**Prepared by:** Bryce (TeamAnalyst)  
**Submitted to:** [Reviewing Actuary]  
**Draft Date:** 2026-04-17

> **Draft status:** This is a working document prepared for internal peer review. It is not a final actuarial communication and should not be distributed outside the review team. Numbers, selections, and commentary are subject to change based on reviewer feedback.

---

## Table of Contents

- [0. Reviewer Quick-Start](#0-reviewer-quick-start)
- [1. Purpose and Scope](#1-purpose-and-scope)
- [2. Summary of Indications](#2-summary-of-indications)
- [3. Data](#3-data)
- [4. Methodology](#4-methodology)
- [5. Key Assumptions](#5-key-assumptions)
- [6. Results by Segment](#6-results-by-segment)
- [7. Diagnostics and Reasonableness Checks](#7-diagnostics-and-reasonableness-checks)
- [8. Sensitivity and Uncertainty](#8-sensitivity-and-uncertainty)
- [9. Reliance on Others](#9-reliance-on-others)
- [10. Information Date and Subsequent Events](#10-information-date-and-subsequent-events)
- [11. Open Questions for Reviewer](#11-open-questions-for-reviewer)
- [12. ASOP Self-Check (for reviewer)](#12-asop-self-check-for-reviewer)
- [13. Peer Review Log](#13-peer-review-log)
- [14. Version History](#14-version-history)

---

## 0. Reviewer Quick-Start

- **What this analysis covers:** Chain-ladder reserving analysis for a single segment, accident years 2015–2024, using Paid Loss, Incurred Loss, Reported Count, and Closed Count triangles. All three methods (CL, IE, BF) were run.
- **What changed since last review:** Initial draft — no prior version.
- **Where I want the most scrutiny:** (1) Tail factor selections — Paid Loss tail of 1.019 vs. Incurred tail of 1.013; (2) Ultimate selections for immature years 2022–2024 where BF was weighted heavily; (3) The IE/BF divergence from CL for AY 2015 Incurred Loss ($45M CL vs. $64M IE).
- **Open questions for reviewer:** See Section 11.

---

## 1. Purpose and Scope

### 1.1 Purpose of the Analysis
Quarterly reserve review for internal booking purposes using canonical demonstration data. The analysis projects ultimate losses and claim counts for accident years 2015–2024 using development triangle methods.

### 1.2 Scope
| Item | Detail |
|---|---|
| Segment(s) / LOB | All Lines Combined (single segment) |
| Accident / Underwriting years | 2015–2024 (10 years) |
| Coverages | Loss only (DCC/ALAE not separately analyzed) |
| Basis | Gross |
| Currency | USD |
| Geography | Not specified |

### 1.3 Intended Internal Users
Chief Actuary, Reserving Committee. This draft is not intended for external distribution in its current form.

---

## 2. Summary of Indications

| Segment | Paid to Date | Case Reserves | IBNR | Total Unpaid | Selected Ultimate |
|---|---|---|---|---|---|
| Incurred Loss | $390,463,646 | $29,701,340 | $125,410,870 | $155,112,210 | $515,874,516 |
| Paid Loss | $360,762,306 | — | $158,314,795 | $158,314,795 | $519,077,101 |
| **Reported Count** | 41,233 | — | 7,050 | 7,050 | 48,283 |
| **Closed Count** | 38,016 | — | 10,027 | 10,027 | 48,043 |

**Method indications summary (Incurred Loss):**

| Method | Total Ultimate | Total IBNR |
|---|---|---|
| Chain Ladder | $534,775,787 | $144,312,141 |
| Initial Expected | $525,022,611 | $134,558,965 |
| Bornhuetter-Ferguson | $509,349,682 | $118,886,036 |
| **Selected** | **$515,874,516** | **$125,410,870** |

**Key drivers:** No prior estimate available for comparison. Method divergence is concentrated in immature years (2022–2024) where CL is most volatile, and in AY 2015 where the IE method produces a materially higher indication than CL (see Section 11).

---

## 3. Data

### 3.1 Data Used
| Data Element | Source | As-of Date | Notes |
|---|---|---|---|
| Paid loss triangles | canonical-triangles.xlsx — Sheet: Paid | 12/31/2024 | 10×10 triangle, AYs 2015–2024 |
| Incurred loss triangles | canonical-triangles.xlsx — Sheet: Incurred | 12/31/2024 | 10×10 triangle |
| Reported claim counts | canonical-triangles.xlsx — Sheet: Reported | 12/31/2024 | 10×10 triangle |
| Closed claim counts | canonical-triangles.xlsx — Sheet: Closed | 12/31/2024 | 10×10 triangle |
| Earned exposure | canonical-triangles.xlsx — Sheet: Exposure | 12/31/2024 | Used for IE/BF methods |
| Expected loss rates | canonical-elrs.xlsx — Sheet: ELR | 12/31/2024 | ELR and expected frequency by AY |

### 3.2 Data Reconciliation
Reconciliation to prior valuation or financial system not performed — this is a demonstration analysis using canonical data. No external reconciliation was available.

### 3.3 Data Quality Observations
- Accident year labels in source files used Excel formula references (=A2+1 style); resolved programmatically during intake.
- No negative development observed in any triangle.
- AY 2015 Closed Count shows a closure rate of 1.000 at age 120 (100% closed), triggering a minor tech review flag; confirmed as expected for a fully mature year.
- YoY severity jumps >25% flagged in early accident years — consistent with normal development pattern for immature periods at age 12–24.

### 3.4 Data Limitations
- No rate change history or trend data available; trend assumptions are implicitly embedded in the ELR file.
- Single-segment analysis only; no sub-segment or coverage-level breakdowns available.
- IE method uses a pre-loaded ELR file; ELR basis and derivation are not documented in source data.

---

## 4. Methodology

### 4.1 Methods Applied
| Method | Segments Applied | Why Selected |
|---|---|---|
| Paid LDF (Chain Ladder) | All Lines | Standard primary method; stable patterns, good credibility at mature ages |
| Incurred LDF (Chain Ladder) | All Lines | Cross-check to Paid; useful for case reserve adequacy assessment |
| Paid/Incurred Count LDF | All Lines | Frequency tracking; supports IE/BF frequency assumptions |
| Initial Expected (IE) | All Lines | Provides a prior-expectation anchor; used as BF weight source |
| Bornhuetter-Ferguson (BF) | All Lines | Blends CL and IE; primary method for immature years |

### 4.2 Method Weighting / Selection Logic
LDF selections were made using a rule-based 14-criteria framework with an independent AI cross-check. Selections were confirmed consistent across both approaches at mid-to-late maturities; minor divergence at 12-24 interval (rule-based: 1.8151 vs. AI: 1.8309 for Paid Loss).

Ultimate selections use a maturity-based weighting approach:
- **Ages 84–120 (AYs 2015–2018):** CL ~70%, BF ~25%, IE ~5%
- **Ages 60–72 (AYs 2019–2020):** CL ~65%, BF ~30%, IE ~5%
- **Ages 36–48 (AYs 2021–2022):** CL ~50%, BF ~45%, IE ~5%
- **Ages 12–24 (AYs 2023–2024):** BF ~55–75%, CL ~20–40%, IE ~5%

### 4.3 LAE Treatment
- DCC/ALAE: Not separately analyzed; assumed included in loss triangles if present in source data.
- A&O/ULAE: Not analyzed.

---

## 5. Key Assumptions

### 5.1 Development Patterns
- **Selection basis:** Volume-weighted averages, with 3-year window preferred at early maturities and 5-year window at mid-to-late maturities. Convergence override applied where all averages cluster within ±2%.
- **Tail:** Paid Loss: 1.019 (reflects ~1.9% residual development beyond age 120, consistent with sub/salvage activity). Incurred Loss: 1.013. Count measures: 1.000 (fully closed by age 120).

### 5.2 Expected Loss Ratios (for B-F and ELR methods)
| AY | Expected Loss Rate ($/exposure) | Expected Frequency |
|---|---|---|
| 2015 | 14,158 | 1.453 |
| 2016 | 14,291 | 1.424 |
| 2017 | 14,426 | 1.395 |
| 2018 | 14,561 | 1.367 |
| 2019 | 14,698 | 1.340 |
| 2020 | 14,836 | 1.313 |
| 2021 | 14,976 | 1.287 |
| 2022 | 15,117 | 1.261 |
| 2023 | 15,259 | 1.236 |
| 2024 | 15,402 | 1.211 |

### 5.3 Trend Assumptions
Implicitly embedded in the ELR file (approximately 0.9% annual severity trend and -1.9% annual frequency trend implied by ELR progression).

### 5.4 Other Assumptions
- **Case reserve adequacy:** Assumed stable; paid-to-incurred ratios progress normally from 0.80 at age 12 to 1.00 at age 120.
- **Settlement rate / claim closing patterns:** Stable; closure rates increase monotonically with age for all AYs.

### 5.5 Assumption Rationale
The tail factors are the most judgment-sensitive assumptions. The paid tail of 1.019 is derived from the observed 108-120 LDF of 1.043 with exponential decay; the incurred tail of 1.013 is lower, consistent with the paid/incurred convergence at age 120. Both are within normal ranges for casualty lines.

---

## 6. Results by Segment

### 6.1 Incurred Loss
- **Selected ultimates:** See Ultimates.xlsx → Sel - Incurred Loss
- **Total selected ultimate:** $515,874,516 | **Total IBNR:** $125,410,870
- **Method weighting:** CL dominant for AYs 2015–2018; BF blend increases for 2019–2024
- **Notable judgment calls:** AY 2015 CL ultimate ($45.6M) is materially below IE ($63.9M); selected near BF ($45.8M) given that AY 2015 is effectively fully developed and CL at age 120 includes only tail factor.

### 6.2 Paid Loss
- **Selected ultimates:** See Ultimates.xlsx → Sel - Paid Loss
- **Total selected ultimate:** $519,077,101 | **Total IBNR:** $158,314,795
- **Method weighting:** Same maturity-based schedule as Incurred Loss
- **Notable judgment calls:** Paid IBNR exceeds Incurred IBNR — flagged for reviewer (see Section 11).

### 6.3 Reported Count
- **Selected ultimate:** 48,283 | **IBNR:** 7,050 counts
- Count development patterns are stable and credible; selections follow CL closely for mature years.

### 6.4 Closed Count
- **Selected ultimate:** 48,043 | **IBNR:** 10,027 counts
- Closed count selections slightly below Reported Count selections for some years — flagged (see Section 11).

---

## 7. Diagnostics and Reasonableness Checks

- [x] Loss ratios by AY — Selected ultimate loss ratios show smooth progression from $9,129/claim (AY 2015) to ~$10,070/claim median ultimate severity; reasonable.
- [x] Frequency / severity trends — Implied frequency declining ~1.9%/yr; severity increasing ~0.9%/yr. Consistent with ELR file assumptions.
- [x] Implied paid and reported development — Paid-to-incurred ratio increases monotonically from 0.80 at age 12 to 1.00 at age 120 across all AYs. Normal pattern.
- [x] Actual vs. expected emergence — Not compared; no prior estimate available.
- [x] Comparison to independent benchmark — Not available.
- [x] Hindsight test on prior ultimates — Not applicable (first analysis).
- [x] Ratio of IBNR to case reserves — IBNR ($125M) is 4.2x case reserves ($30M); elevated but consistent with significant immature-year exposure (AYs 2021–2024 represent 40% of ultimate).

**Tech review results:** 186 PASS / 27 WARN / 5 FAIL. Full results in output/tech-review.xlsx.

**Anomalies to investigate:**
1. Paid Loss IBNR ($158M) exceeds Incurred Loss IBNR ($125M) — review if paid tail > incurred tail is the sole driver.
2. Closed Count selected > Reported Count selected for AYs 2015, 2018, 2021, 2022 — logically Closed should not exceed Reported; likely a blending artifact in immature years.
3. AY 2015 Incurred Loss: CL ultimate ($45.6M, IBNR ~$0.6M) vs. IE ultimate ($63.9M) — a 40% divergence. IE appears too high relative to actual development.
4. Loss Rate tech review flag — ELR is expressed as $/exposure, not a traditional loss ratio; not a data error.

---

## 8. Sensitivity and Uncertainty

### 8.1 Sensitivity to Key Assumptions
| Assumption | Change | Estimated Impact on Incurred Ultimate |
|---|---|---|
| Paid tail factor | +0.01 | ~+$5M |
| Incurred tail factor | +0.01 | ~+$4M |
| BF weight for AYs 2022–2024 | ±10% shift to CL | ±$3–5M |

### 8.2 Sources of Uncertainty
- **Process risk:** Thin data for immature years (AYs 2022–2024 have only 12–36 months of development); selections rely heavily on BF/IE which assumes ELR quality.
- **Parameter risk:** Tail factor uncertainty; the 108-120 interval is based on only one observed data point (AY 2015).
- **Model risk:** CL and BF give materially different results for AY 2015; method selection significantly affects that year's indication.
- **Systemic risk:** No adjustment for tort environment, economic inflation, or mix shift; these risks are not quantified.

---

## 9. Reliance on Others

| Source | Information Relied Upon |
|---|---|
| Source data provider | canonical-triangles.xlsx and canonical-elrs.xlsx as provided; accuracy of underlying claim data not independently verified |

---

## 10. Information Date and Subsequent Events

- **Information Date:** 12/31/2024
- **Subsequent events considered:** None known.

---

## 11. Open Questions for Reviewer

1. **AY 2015 Incurred Loss IE vs. CL divergence:** IE projects $63.9M vs. CL $45.6M. The CL is effectively at tail-only development. Should we investigate whether the ELR for 2015 is reasonable given the actual emergence? Currently selected near BF ($45.8M).
2. **Paid IBNR > Incurred IBNR:** Total paid IBNR ($158M) exceeds incurred IBNR ($125M). This is driven by the paid tail being higher than the incurred tail (1.019 vs. 1.013). Is this ordering reasonable for this book?
3. **Closed Count > Reported Count in some years:** The AI selections produced Closed > Reported for AYs 2015, 2018, 2021, 2022. Logically this should not occur. Recommend reviewing these specific year selections in Ultimates.xlsx before finalizing.
4. **ELR basis:** The expected loss rates are in $/exposure (not traditional loss ratio). The basis and derivation of this file are not documented. Is the source reliable?

**Items flagged as low-confidence:**
- All selections for AYs 2023–2024 (12–24 months of development, very high BF weight)
- Tail factors for both Paid and Incurred Loss

---

## 12. ASOP Self-Check (for reviewer)

| Standard | Addressed In | Notes |
|---|---|---|
| ASOP 23 (Data Quality) | §3 | Formula-based AY labels resolved; no negative development |
| ASOP 25 (Credibility) | §4, §5 | Maturity-based weighting applied; immature years use BF |
| ASOP 41 (Communications) | Throughout | Draft — not a final actuarial communication |
| ASOP 43 (Unpaid Claim Estimates) | §4, §5, §8 | Three methods applied; sensitivity noted |
| ASOP 56 (Modeling) | §4 | Rule-based + AI selection framework documented |

---

## 13. Peer Review Log

| # | Date | Reviewer Comment | Analyst Response | Status |
|---|---|---|---|---|
| 1 | | | | Open |

---

## 14. Version History

| Version | Date | Author | Summary of Changes |
|---|---|---|---|
| v0.1 | 2026-04-17 | Bryce / TeamAnalyst | Initial draft — full analysis, all methods, tech review complete |

---

## Appendices (in accompanying workbook)

- A. Chain Ladder Selections (selections/Chain Ladder Selections.xlsx)
- B. Ultimate Selections (selections/Ultimates.xlsx)
- C. Selected Ultimates Summary (output/selected-ultimates.xlsx)
- D. Post-Method Diagnostics (output/post-method-series.xlsx, post-method-triangles.xlsx)
- E. Complete Analysis Workbook (output/complete-analysis.xlsx)
- F. Tech Review Results (output/tech-review.xlsx)

---

*End of working draft.*
