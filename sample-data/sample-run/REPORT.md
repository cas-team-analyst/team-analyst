# Reserving Analysis — Working Draft

**Analysis:** Sample Run
**Valuation Date:** [To be confirmed from data]
**Draft Version:** v0.1 — In Progress
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

- **What this analysis covers:** Workers Compensation reserve analysis for AYs 2001–2024 (24 accident years), using Chain Ladder and Bornhuetter-Ferguson methods on paid loss, incurred loss, and reported count triangles. Selected ultimate loss = $48.3M; total unpaid = $6.6M.
- **What changed since last review:** First analysis — no prior estimate available.
- **Where I want the most scrutiny:** (1) Negative IBNR in 4 mature AYs — implies case redundancy; (2) BF selections for AYs 2019–2024 — thin development, a priori rates are fallback approximations; (3) Paid loss tail factor at 1.0039 — poor exponential curve fit.
- **Open questions for reviewer:** See Section 11

---

## 1. Purpose and Scope

### 1.1 Purpose of the Analysis
Sample reserving analysis run using the TeamAnalyst plugin workflow to demonstrate end-to-end chain ladder and Bornhuetter-Ferguson reserve estimation.

### 1.2 Scope
| Item | Detail |
|---|---|
| Segment(s) / LOB | Workers Compensation (WC) — clerical, low-hazard |
| Accident / Underwriting years | 2001–2024 (24 accident years) |
| Coverages | Paid Loss, Incurred Loss, Reported Count |
| Basis | Gross (assumed) |
| Currency | USD |
| Geography | Not specified in source data |

### 1.3 Intended Internal Users
Internal actuarial team. This draft is not intended for external distribution in its current form.

---

## 2. Summary of Indications

| Segment | Paid to Date | Case Reserves | IBNR | Total Unpaid | Ultimate |
|---|---|---|---|---|---|
| Loss (WC) | $41,767,854 | $1,848,541 | $4,721,077 | $6,569,618 | $48,337,472 |
| Count (Reported) | 9,716 | — | 22 | 22 | 9,738 |

**Comparison to prior estimate:**

Not applicable — no prior estimate available for comparison.

**Key drivers of change:** Not applicable.

---

## 3. Data

### 3.1 Data Used
| Data Element | Source | As-of Date | Notes |
|---|---|---|---|
| Paid loss triangle | Triangle Examples 1.xlsx / Paid 1 | Latest diagonal: AY 2024 age 11 | 24 AYs (2001–2024), dev ages 11–287 months, 300 data points |
| Incurred loss triangle | Triangle Examples 1.xlsx / Inc 1 | Latest diagonal: AY 2024 age 11 | 24 AYs (2001–2024), dev ages 11–287 months, 300 data points |
| Reported count triangle | Triangle Examples 1.xlsx / Ct 1 | Latest diagonal: AY 2024 age 11 | 24 AYs (2001–2024), dev ages 11–287 months, 300 data points |
| Exposure (payroll) | Triangle Examples 1.xlsx / Exposure | 2024 | Payroll growing at 2% per year from 2001 base of $316M |
| Expected loss rates | Not provided | N/A | BF/IE will use fallback approximation (diagonal loss ÷ exposure, 3-yr rolling avg) |
| Prior selections | Not provided | N/A | No prior analysis available |

### 3.2 Data Reconciliation
- Not reconciled — data accepted as provided by source file (Triangle Examples 1.xlsx).

### 3.3 Data Quality Observations
- Dev ages are non-standard (11, 23, 35… months — i.e., 12n−1 pattern) but internally consistent across all triangles; no adjustment made.
- AY 2007 paid loss shows a notable upward spike in mid-development (age 59–95), peaking at $3.15M vs. neighbors in the $1–1.5M range — possible large loss or cat event.
- AY 2015 paid loss also shows elevated development in the 47–107 month range ($2.1M–$2.9M range vs. cohort average), potentially a second large-loss year.
- AY 2001 paid loss shows a slight decline from age 71→83 (paid decreased from $2,283,776 to $2,261,773) — minor negative development, not material.
- No material data quality issues requiring exclusion.

### 3.4 Data Limitations
- No closed count data — unable to estimate closure rates or calculate closed count CDF.
- No expected loss rate file provided — Initial Expected method uses fallback approximation (3-year rolling average of diagonal loss per payroll dollar).
- No prior selections available — no prior LDF benchmark for comparison.
- Valuation date not explicitly stated in source data; inferred from triangle shape as approximately year-end 2024.

---

## 4. Methodology

### 4.1 Methods Applied
| Method | Segments Applied | Why Selected |
|---|---|---|
| Paid CL | Loss — all AYs | Primary selection for mature years (2001–2020); stable development factors, closure-certainty advantage over incurred |
| Incurred CL | Loss — cross-check only | Used as cross-check; not selected; higher CDF volatility at younger ages |
| Paid BF | Loss — AYs 2019–2024 | Selected for immature years where CL CDFs are unstable (1.3–7.8×); BF blends prior expectation with emerging paid |
| Reported CL | Count — AYs 2001–2023 | Count development fully converged at age 11+ for most years; CL captures actual closure |
| Reported BF | Count — AY 2024 | Age 11 only; 89.7% developed; BF provides stable estimate at extreme immaturity |
| Initial Expected (IE) | Not selected | Fallback ELR approximation; several AYs produced negative IBNR (stale a priori rates) — used as BF input only |
| Closed Count CL | Not applicable | No closed count data available |
| Frequency-Severity | Not applicable | Not implemented in this workflow |

### 4.2 Method Weighting / Selection Logic
LDF selections used the rules-based 14-criteria framework (CV screening, trend detection, outlier exclusion, asymmetric conservatism) applied independently per measure with an open-ended AI cross-check. Tail factors selected via Bondy method at cutoff age 143 for all measures; Reported Count tail = 1.000 (fully developed at 143 months).

Ultimate selections followed a maturity-based hierarchy: Paid CL for years ≥95 months developed; Paid BF for years <72 months. The fallback IE method (3-year rolling average of diagonal loss per payroll) produced negative IBNRs in several accident years (2001, 2002, 2006, 2012) when compared to current incurred — indicating the a priori rates may be optimistic relative to current case reserve levels in those years. This is flagged in Section 11.

### 4.3 LAE Treatment
**Not applicable.** This analysis assumes loss triangles include LAE (loss and allocated loss adjustment expense combined), or LAE is not being estimated separately. If LAE needs to be estimated separately, that is outside the scope of this workflow.

- **DCC / ALAE:** Not separately estimated
- **A&O / ULAE:** Not separately estimated

---

## 5. Key Assumptions

### 5.1 Development Patterns
- **Selection basis:** Volume-weighted averages with window selection (3-year to all-year) determined per interval by the rules-based framework (CV thresholds, trend detection, outlier exclusion). Asymmetric 40% conservatism applied where downward trends were detected.
- **Tail:** Bondy method at cutoff age 143 months for Paid Loss (1.0039) and Incurred Loss (1.0119). Reported Count tail = 1.0000 (fully developed at age 143). Exponential decay methods rejected for Paid Loss (R²=0.19, below 0.85 threshold); Skurnick method (1.329) rejected as outlier at age 203.

### 5.2 Expected Loss Ratios (for B-F and ELR methods)
ELR file not provided. Fallback method used: diagonal incurred loss ÷ payroll exposure, smoothed with a 3-year rolling average. Applied only for BF calculation on immature years (2019–2024) where CL CDFs are unstable. The a priori ELRs are not shown separately; see `ultimates/projected-ultimates.parquet` column `ultimate_ie` for the implied expected ultimates by AY.

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
- **Expected loss ratios (if used):** [Fill in source if BF/IE methods were used, otherwise note "Not applicable - CL only"]

*Any assumption primarily judgment-driven should be flagged in Section 11.*

---

## 6. Results by Segment

*Detailed exhibits live in the accompanying workbook; summarize selections and rationale here.*

### 6.1 Loss (WC — Paid Loss basis)
- Selected ultimates: See `selections/Ultimates.xlsx`, Losses sheet
- Method weighting: Paid CL for AYs 2001–2018 (mature, 81–100% developed); Paid BF for AYs 2019–2024 (immature, 12–69% developed)
- Notable judgment calls: AY 2007 and 2015 show significantly elevated development (large-loss years); both are well-developed (CL applied). Negative IBNR vs. current incurred in AYs 2001, 2002, 2006, 2012 — see Section 11.

### 6.2 Count (Reported Count basis)
- Selected ultimates: See `selections/Ultimates.xlsx`, Counts sheet
- Method weighting: Reported CL for AYs 2001–2023 (count fully converged for nearly all years); Reported BF for AY 2024 (age 11 only)
- Notable judgment calls: Count development is unusually rapid — most years show 100% development by age 23. Minor negative IBNRs in 15 of 24 AYs (within tolerance, −1 to −2 counts).

---

## 7. Diagnostics and Reasonableness Checks

- [x] Loss ratios by AY — reasonable progression overall; AY 2007 and 2015 elevated (large-loss years flagged during EDA)
- [x] Frequency / severity trends — consistent with historical patterns; no systematic severity spikes beyond 2007/2015
- [x] Implied paid and reported development — patterns consistent with LDF selections
- [ ] Actual vs. expected emergence since prior review — Not applicable (no prior estimate)
- [ ] Comparison to independent benchmark — Not performed
- [ ] Hindsight test on prior ultimates — Not performed (no prior ultimates available)
- [x] Ratio of IBNR to case reserves — reviewed; IBNR ($4.7M) vs. case ($1.8M) = 2.5× ratio; reasonable for WC with long-tail immature years

**Anomalies to investigate:**
- **Tech review FAIL:** Negative IBNR (Ultimate < Current Incurred) in AYs 2001, 2002, 2006, 2012 — Paid CL selected ultimate is below current incurred; implies case reserves may be redundant or incurred development reversed. Warrants reviewer scrutiny on case reserve adequacy.
- **Tech review WARN:** AY 2007 selected ultimate is the outlier at >10× median, driven by known large-loss development in that year ($3.15M paid at age 95 vs. cohort average ~$1.2M). No adjustment made — large loss appears fully developed.
- **Tech review WARN:** 15 count AYs show minor negative IBNR (−1 to −2 counts); within tolerance; reflects slight reopenings in otherwise fully-developed years.

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
- **Process risk:** Thin data at recent AYs (2021–2024 have only 1–4 development periods); actual emergence could differ materially from BF projections. One additional large-loss year could shift recent-year ultimates significantly.
- **Parameter risk:** Tail factor uncertainty for Paid Loss — curve fits had poor R² (0.19 for exponential decay); Bondy selected as conservative baseline (1.0039). If true tail is closer to 1.02–1.04, aggregate reserve could increase by $0.4–$0.8M. LDF selections for early intervals (11–35 months) have high CV across years.
- **Model risk:** CL vs. BF choice for immature years (2019–2024) drives material reserve differences. If CL were applied uniformly, IBNR would be ~$10.9M (Paid CL total) vs. selected $6.6M — a $4.3M upside risk if development accelerates.
- **Systemic risk:** The a priori ELRs used for BF are based on a fallback rolling average; if underlying loss trends have shifted (e.g., post-COVID claim severity changes), these rates may not be appropriate. No explicit trend adjustment was made.

---

## 9. Reliance on Others

| Source | Information Relied Upon |
|---|---|
| Source of Triangle Examples 1.xlsx | Paid loss, incurred loss, reported count triangles and payroll exposure for AYs 2001–2024 |

No external sources or benchmarks relied upon beyond the input data file.

---

## 10. Information Date and Subsequent Events

- **Information Date:** Triangle data through latest diagonal; most recent accident year AY 2024 at age 11 months. Inferred valuation date approximately 12/31/2024.
- **Subsequent events considered:** None known as of 04/29/2026.

---

## 11. Open Questions for Reviewer

*The key section — where you flag judgment calls you want a second opinion on.*

1. **Negative IBNR in mature years (AYs 2001, 2002, 2006, 2012):** Selected Paid CL ultimates are below current incurred in these years. This implies the current case reserves are redundant vs. the paid development pattern. Is this consistent with your understanding of case reserve adequacy for this segment?

2. **AY 2007 large-loss year:** Paid development spikes to $3.15M at age 95 — roughly 2.5× neighboring years. The selected ultimate ($3.0M via Paid CL) is fully developed at age 287. Does this match known claim history? Should this be excluded from LDF averages for the adjacent intervals?

3. **AY 2015 elevated development:** Similar elevated pattern through ages 47–107 ($2.1–2.9M). Is this a second large-loss year or a systemic change?

4. **BF a priori rates for 2019–2024:** The fallback rolling-average ELR may not be appropriate if there were exposure or trend changes post-2019. Recommend reviewer confirm these rates are reasonable before finalizing recent-year selections.

5. **Tail factor — Paid Loss at 1.0039:** With poor exponential fit (R²=0.19), this selection relies on Bondy extrapolation. For WC, tail can be material — is 0.39% tail appropriate given the line and risk type?

**Items I'm flagging as low-confidence:**
- AY 2019–2024 ultimate selections (BF-dependent, very thin development)
- Tail factor for Paid Loss (poor curve fit diagnostics)

**Items I think should be escalated:**
- Resolution of negative IBNR in AYs 2001, 2002, 2006, 2012 before finalizing reserve booking

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