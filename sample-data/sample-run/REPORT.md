# Reserving Analysis — Working Draft

**Analysis:** Sample Run
**Valuation Date:** 11/30/2024 (AY 2024 at 11 months)
**Draft Version:** v0.1 — Work in Progress
**Prepared by:** Bryce
**Submitted to:** [Reviewing Actuary Name]
**Draft Date:** 04/29/2026

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
- [Appendices](#appendices-in-accompanying-workbook)

---

## 0. Reviewer Quick-Start

*A short orientation so the reviewer can get into the work quickly.*

- **What this analysis covers:** Workers Compensation reserve analysis for AY 2001–2024 using Chain Ladder, BF, and IE methods on Paid Loss, Incurred Loss, and Reported Count triangles. Total selected ultimate: ~$51.2M loss, ~9,751 counts.
- **What changed since last review (if applicable):** No prior estimate available — first run.
- **Where I want the most scrutiny:** (1) AY 2007 large-loss treatment, (2) IE/BF ELR quality for immature years 2019-2024, (3) Paid Loss tail factor selection.
- **Open questions for reviewer:** See Section 11

---

## 1. Purpose and Scope

### 1.1 Purpose of the Analysis
Sample actuarial reserving analysis for a Workers Compensation book using the TeamAnalyst workflow. Methods applied include Chain Ladder, Bornhuetter-Ferguson, and Initial Expected Loss ratio projections across Paid Loss, Incurred Loss, and Reported Count triangles.

### 1.2 Scope
| Item | Detail |
|---|---|
| Segment(s) / LOB | Workers Compensation |
| Accident / Underwriting years | 2001–2024 |
| Coverages | Paid Loss, Incurred Loss, Claim Counts |
| Basis | Not specified (data as provided) |
| Currency | USD |
| Geography | Not specified |

### 1.3 Intended Internal Users
Internal reserving team. This draft is not intended for external distribution in its current form.

---

## 2. Summary of Indications

*Placeholder numbers — subject to review.*

| Segment | Paid to Date | Case | IBNR | Total Unpaid | Ultimate |
|---|---|---|---|---|---|
| Loss (Incurred, all AYs) | 43,616,395 | 1,848,541 | 7,579,576 | 9,428,117 | 51,195,971 |
| Count (Reported, all AYs) | 9,716 | — | 35 | 35 | 9,751 |
| **Total** | | | | | |

**Comparison to prior estimate:**

| Segment | Prior Ultimate | Current Ultimate | Change | % |
|---|---|---|---|---|
| N/A | — | — | — | — |

**Key drivers of change:** Not applicable — no prior estimate available for comparison.

---

## 3. Data

### 3.1 Data Used
| Data Element | Source | As-of Date | Notes |
|---|---|---|---|
| Paid Loss triangles | Triangle Examples 1.xlsx (Paid 1 tab) | 11/30/2024 | AY 2001-2024, 24 dev ages (11-287 mo) |
| Incurred Loss triangles | Triangle Examples 1.xlsx (Inc 1 tab) | 11/30/2024 | AY 2001-2024, 24 dev ages (11-287 mo) |
| Claim counts (reported) | Triangle Examples 1.xlsx (Ct 1 tab) | 11/30/2024 | AY 2001-2024, 24 dev ages (11-287 mo) |
| Payroll / exposure | Triangle Examples 1.xlsx (Exposure tab) | 11/30/2024 | 2001 base $316M, 2% annual growth |
| Rate change history | N/A | N/A | Not provided |
| Closed count | N/A | N/A | Not provided |

### 3.2 Data Reconciliation
- Not reconciled - data accepted as provided by Triangle Examples 1.xlsx.

### 3.3 Data Quality Observations
*Per ASOP No. 23 — flag anything unusual.*

- AY 2007 exhibits notably elevated paid loss development (~$4.8M ultimate vs. peer AYs in the $1M-$2M range), consistent with a large-loss year.
- Exposure sheet uses Excel formulas (=B2*1.02); values computed programmatically using 2% annual growth from 2001 base.
- Reported Count triangle classifed as Reported Count per default assumption (counts stabilize quickly at most maturities).
- No negative development, coding anomalies, or structural breaks identified beyond the AY 2007 outlier.

### 3.4 Data Limitations
- No closed count data available; closure rate analysis not possible.
- No expected loss rate file provided; IE and BF methods used fallback approximation (smoothed diagonal loss rate per exposure, 3-year rolling average).
- No prior year selections available for comparison.
- Valuation date inferred as 11/30/2024 based on AY 2024 being at 11 months of development.

---

## 4. Methodology

### 4.1 Methods Applied
| Method | Segments Applied | Why Selected |
|---|---|---|
| Incurred LDF (Chain Ladder) | Incurred Loss, AY 2001-2024 | Primary loss method; selected via rules-based framework with AI cross-check |
| Paid LDF (Chain Ladder) | Paid Loss, AY 2001-2024 | Secondary loss method; cross-check on incurred |
| Reported LDF (Chain Ladder) | Reported Count, AY 2001-2024 | Count development; essentially complete by 23 months |
| Initial Expected (IE) | Incurred Loss, Paid Loss, Reported Count | Fallback ELR from smoothed diagonal loss rate; used in BF blending |
| Bornhuetter-Ferguson | Incurred Loss, Paid Loss, Reported Count | Weighted with CL for immature accident years |
| Frequency-Severity | N/A | Not applied |

### 4.2 Method Weighting / Selection Logic
LDF selections made using a 14-criteria rules-based framework applied independently per measure and interval, with an open-ended AI cross-check. For mature accident years (AY 2001-2015), Incurred Chain Ladder is the primary selection given high percent-developed (>85%). For immature years (AY 2016-2024), BF blends the Chain Ladder indication with the fallback ELR to moderate sensitivity to immature development. Ultimate selections default to Incurred CL per rules-based framework across all 24 accident years.

### 4.3 LAE Treatment
**Not applicable.** This analysis assumes loss triangles include LAE (loss and allocated loss adjustment expense combined), or LAE is not being estimated separately. If LAE needs to be estimated separately, that is outside the scope of this workflow.

- **DCC / ALAE:** Not separately estimated
- **A&O / ULAE:** Not separately estimated

---

## 5. Key Assumptions

### 5.1 Development Patterns
- **Selection basis:** Volume-weighted averages with windows from 3-year to all-year. Rules-based framework selected optimal window per development interval based on stability (CV), volume, and slope diagnostics.
- **Tail factors:** Incurred Loss = 1.0103 (double exponential decay, cutoff age 203, R²=0.978); Paid Loss = 1.0039 (Bondy, cutoff age 203 — tail immaterial); Reported Count = 1.0000 (Bondy, cutoff age 143 — fully developed).

### 5.2 Expected Loss Ratios (for B-F and ELR methods)
| AY | ELR | Basis |
|---|---|---|
| | | |

### 5.3 Trend Assumptions
**Not implemented in this analysis.** The current workflow does not include trend selection or application. Loss development methods (Chain Ladder, BF, IE) rely on historical development patterns without explicit trending adjustments.

| Segment | Frequency | Severity | Pure Premium |
|---|---|---|---|
| N/A | N/A | N/A | N/A |

### 5.4 Other Assumptions
- **Rate change:** Not explicitly modeled in this analysis
- **Case reserve adequacy:** Assumed stable (no adjustments applied)
- **Settlement rate / claim closing patterns:** Patterns emerge from historical triangle development; no explicit assumptions
- **Mix / law / tort environment:** Not explicitly modeled

### 5.5 Assumption Rationale
**Material assumptions in this analysis:**
- **LDF selections:** Based on volume-weighted averages with rule-based framework (14 criteria) and AI cross-check. See Section 4.2 and LDF selection workbooks for detailed reasoning.
- **Tail factors:** Based on curve fitting (Bondy, Exponential Decay, etc.) with leave-one-out validation. See tail selection workbook for detailed reasoning.
- **Expected loss ratios:** Derived from fallback approximation — diagonal incurred loss per dollar of payroll exposure, smoothed with a 3-year rolling average and applied as the IE a priori rate. See Section 5.2 for detail by accident year.

*Any assumption primarily judgment-driven should be flagged in Section 11.*

---

## 6. Results by Segment

*Detailed exhibits live in the accompanying workbook; summarize selections and rationale here.*

### 6.1 Loss (Incurred + Paid)
- Selected ultimates: See Ultimates.xlsx Losses sheet and Analysis.xlsx Loss Selection tab
- Method weighting: Incurred CL selected for all 24 AYs; BF and IE provided cross-checks. Mature years (2001-2015) at 85-99% development; immature years (2016-2024) carry more IBNR uncertainty.
- Notable judgment calls: AY 2007 elevated development (~$4.8M) absorbed into selections — no separate large-loss adjustment applied.

### 6.2 Count (Reported)
- Selected ultimates: See Ultimates.xlsx Counts sheet and Analysis.xlsx Count Selection tab
- Method weighting: Reported CL selected for all 24 AYs. Count development essentially complete by 35 months; very low IBNR (35 total across all AYs).
- Notable judgment calls: Slight negative IBNR for 9 accident years (within tolerance) — reflects count triangles plateauing at or slightly above CL ultimate estimate.

---

## 7. Diagnostics and Reasonableness Checks

- [x] Loss ratios by AY — Reviewed; reasonable progression. AY 2007 elevated (large-loss year).
- [x] Frequency / severity trends — Tech review flagged YoY severity spikes in development periods 3, 4, 6 (46%, 103%, 231%); consistent with early accident-year maturation pattern in WC, not an anomaly.
- [x] Implied paid and reported development — Consistent with LDF selections.
- [ ] Actual vs. expected emergence — Not applicable; no prior estimate available.
- [ ] Comparison to independent benchmark — Not performed.
- [ ] Hindsight test on prior ultimates — Not performed (no prior selections).
- [x] Ratio of IBNR to case reserves — Total IBNR ($7.6M) vs. case reserves ($1.8M) ratio of ~4:1; consistent with Workers Compensation long-tail pattern.

**Anomalies to investigate:**
- Tech review WARN: YoY severity spikes of 46%, 103%, 231% in development periods 3, 4, 6 (incremental, not AY-to-AY — expected in WC maturation)
- Tech review WARN: Frequency spike >2x median in 5 periods (likely early-stage AYs with partial-year exposure)
- Tech review WARN: Slight negative IBNR on count for 9 AYs (within rounding tolerance; counts plateau at CDF=1.0)
- Tech review FAIL on null Selected Ultimate: False positive — affects only blank separator and Total rows, not accident year data rows.

---

## 8. Sensitivity and Uncertainty

### 8.1 Sensitivity to Key Assumptions
**Not implemented in this analysis.** Sensitivity testing would require re-running projections with varied assumptions. This can be added in future iterations.

| Assumption | Change | Impact on Total Ultimate |
|---|---|---|
| Tail factor | ± (not tested) | (not tested) |
| ELR | ± (not tested) | (not tested) |
| LDF selections | ± (not tested) | (not tested) |

### 8.2 Sources of Uncertainty
*Per ASOP No. 43 — discuss the risks that could cause actuals to differ from estimate.*

- **Process risk:** Workers Compensation inherently long-tail; early-stage accident years (2019-2024) carry substantial IBNR uncertainty given limited development history.
- **Parameter risk:** Tail factor uncertainty — Paid Loss tail (Bondy 1.0039) was deemed immaterial, but alternative exponential methods ranged up to 1.084; this could shift paid reserve by ~$350K. LDF selection uncertainty greatest at 11-23 month interval (CV ~0.33 for incurred).
- **Model risk:** CL vs. BF choice for immature years (2020-2024) is a key driver; BF credibility depends heavily on ELR quality, which here is a smoothed approximation rather than a pricing-derived rate.
- **Systemic risk:** AY 2007 large-loss year not separately estimated; if additional latent claims re-open this could impact ultimate. No explicit IBNR loading for potential large losses in recent years.

---

## 9. Reliance on Others

| Source | Information Relied Upon |
|---|---|
| Triangle Examples 1.xlsx | Paid Loss, Incurred Loss, Reported Count triangles; Payroll exposure |
| No external sources | All data derived from the single provided input file |

---

## 10. Information Date and Subsequent Events

- **Information Date:** November 30, 2024 (inferred — AY 2024 at 11 months of development)
- **Subsequent events considered:** None known as of 04/29/2026 (analysis run date).

---

## 11. Open Questions for Reviewer

*The key section — where you flag judgment calls you want a second opinion on.*

1. AY 2007 large-loss year is not separately estimated. The elevated development (~$4.8M ultimate) is absorbed into LDF averages. Should a large-loss exclusion and separate IBNR load be applied for this year?
2. IE/BF expected loss rates are derived from a smoothed fallback approximation, not from independent pricing data. Do you have a preferred ELR source for these accident years?
3. Tail factor for Paid Loss (1.0039, Bondy) is based on immateriality. Should a longer tail assumption be considered given WC severity trends?

**Items I'm flagging as low-confidence:**
- IE/BF ELR for immature AYs (2019-2024) — fallback approximation may not reflect true a priori expectation
- Paid Loss tail factor — exponential alternatives ranged widely (1.0-1.084); Bondy selected on immateriality grounds

**Items I think should be escalated to [Chief Actuary / Committee]:**
- [ ]

---

## 12. ASOP Self-Check (for reviewer)

| Standard | Addressed In | Notes |
|---|---|---|
| ASOP 23 (Data Quality) | §3 | |
| ASOP 25 (Credibility) | §4, §5 | |
| ASOP 41 (Communications) | Throughout | Draft — not a final communication |
| ASOP 43 (Unpaid Claim Estimates) | §4, §5, §8 | |
| ASOP 56 (Modeling) | §4 | If applicable |

---

## 13. Peer Review Log

*Reviewer fills this in; analyst responds and updates the draft.*

| # | Date | Reviewer Comment | Analyst Response | Status |
|---|---|---|---|---|
| 1 | | | | Open / Addressed / Deferred |
| 2 | | | | |

**Sign-off checklist (to be completed before moving to final):**
- [ ] All reviewer comments addressed or deferred with rationale
- [ ] Numbers reconcile to supporting workbook
- [ ] Exhibits match narrative
- [ ] Open questions closed or escalated
- [ ] Version history updated

---

## 14. Version History

| Version | Date | Author | Summary of Changes |
|---|---|---|---|
| v0.1 | 04/29/2026 | Bryce | Initial draft |
| v0.2 | | | |

---

## Appendices (in accompanying workbook)

- A. Triangles (paid, reported, counts)
- B. Development factor selections
- C. Method indications by segment / AY
- D. Diagnostic exhibits
- E. Data reconciliation worksheet

---

*End of working draft.*