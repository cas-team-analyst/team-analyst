# Reserving Analysis — Working Draft

**Analysis:** Sample Run — Workers Compensation
**Valuation Date:** ~November 30, 2024 (AY 2024 at 11 months of development)
**Draft Version:** v0.1 — Initial Draft
**Prepared by:** Bryce
**Submitted to:** Reviewing Actuary
**Draft Date:** 2026-04-30

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

- **What this analysis covers:** Workers Compensation reserve analysis for AY 2001–2024 using Chain Ladder (Paid and Incurred), Bornhuetter-Ferguson, and Initial Expected methods. Evaluation date approximately November 30, 2024. Selected ultimate loss: **$46.8M** with total IBNR of **$3.2M**.
- **What changed since last review:** Initial analysis — no prior estimate for comparison.
- **Where I want the most scrutiny:** (1) AY 2007 selected ultimate — paid diagonal is ~2–3× peer years, likely driven by a large loss; (2) immature year selections (2022–2024) where CL tail factors are large and BF/IE weighting choices matter most; (3) ELR fallback assumption — no actual pricing ELRs were available.
- **Open questions for reviewer:** See Section 11

---

## 1. Purpose and Scope

### 1.1 Purpose of the Analysis
Sample reserving analysis of Workers Compensation losses using the TeamAnalyst AI workflow. This analysis is intended to demonstrate the end-to-end reserving process using CAS-style triangle data.

### 1.2 Scope
| Item | Detail |
|---|---|
| Segment(s) / LOB | Workers Compensation — clerical / low-hazard payroll |
| Accident / Underwriting years | 2001–2024 (24 years) |
| Coverages | Loss (paid + incurred); Reported count; Payroll exposure |
| Basis | Direct (gross) |
| Currency | USD |
| Geography | Not specified |

### 1.3 Intended Internal Users
Internal actuarial team and reviewing actuary. This draft is not intended for external distribution in its current form.

---

## 2. Summary of Indications

*Placeholder numbers — subject to review.*

| Segment | Paid to Date | Case Reserves | IBNR | Total Unpaid | Ultimate |
|---|---|---|---|---|---|
| Loss (WC) | $41,767,854 | $1,848,541 | $3,200,946 | $5,049,487 | $46,817,341 |
| Count (Reported) | 9,716 | — | 36 | 36 | ~9,752 |
| **Total (Loss)** | **$41,767,854** | **$1,848,541** | **$3,200,946** | **$5,049,487** | **$46,817,341** |

**Comparison to prior estimate:**

| Segment | Prior Ultimate | Current Ultimate | Change | % |
|---|---|---|---|---|
| Loss (WC) | N/A | $46,817,341 | N/A | N/A |

**Key drivers of change:** Not applicable — no prior estimate available for comparison. This is the initial analysis.

---

## 3. Data

### 3.1 Data Used
| Data Element | Source | As-of Date | Notes |
|---|---|---|---|
| Paid loss triangles | Triangle Examples 1.xlsx — Sheet "Paid 1" | ~Nov 30, 2024 | 24 AYs × 24 ages (11–287 months) |
| Incurred loss triangles | Triangle Examples 1.xlsx — Sheet "Inc 1" | ~Nov 30, 2024 | 24 AYs × 24 ages (11–287 months) |
| Reported claim counts | Triangle Examples 1.xlsx — Sheet "Ct 1" | ~Nov 30, 2024 | 24 AYs × 24 ages; generic "Ct" header, classified as Reported Count |
| Payroll exposure | Triangle Examples 1.xlsx — Sheet "Exposure" | 2024 | Annual payroll by AY; 2002–2024 computed as 2001 × 1.02^n |
| Case reserves | Not provided separately | — | Implicitly available as Incurred − Paid |
| Rate change history | Not provided | — | Not used in this analysis |
| Expected loss rates | Not provided | — | Fallback: 3-year rolling average of empirical loss rates used for BF |

### 3.2 Data Reconciliation
Not reconciled — data accepted as provided by the source file (Triangle Examples 1.xlsx). No prior valuation or financial system available for comparison.

### 3.3 Data Quality Observations
- **AY 2007 (age 215) — elevated paid loss:** Paid diagonal value of $4.791M is materially higher than neighboring years (~$1–2M range). Consistent with a large-loss year. Incurred shows similar elevation. LDF patterns for AY 2007 will be examined closely.
- **AY 2015 (age 119) — elevated paid loss:** Diagonal of $3.364M also above trend for years at similar maturity. Possible large claim or adverse development year.
- **Non-standard initial age:** Development ages begin at 11 months (not the typical 12), consistent with a November 30 evaluation date convention. All scripts handle this correctly.
- **Negative development (Incurred):** Some incurred values show slight negative development in mature periods, indicating prior case reserve redundancy. No adjustments made; patterns will be reflected in LDF selections.
- No material data quality issues requiring exclusion or restatement were identified.

### 3.4 Data Limitations
- No ELR file provided — using 3-year rolling average of empirical loss rates as fallback for Initial Expected / BF methods.
- No closed count data — unable to estimate closure rates or use Closed Count chain ladder.
- No prior LDF or tail factor selections available for comparison.
- Payroll exposure for 2002–2024 is formula-derived (2001 × 1.02^n); actual payroll history not confirmed.

---

## 4. Methodology

### 4.1 Methods Applied
| Method | Segments Applied | Why Selected |
|---|---|---|
| Incurred LDF (Chain Ladder) | WC Loss | Primary method for mature years (95%+ developed); stable incurred patterns |
| Paid LDF (Chain Ladder) | WC Loss | Cross-check and primary for years where paid/incurred converge |
| Initial Expected (IE) | WC Loss, Count | Fallback for immature years; uses empirical ELR approximation |
| Bornhuetter-Ferguson | WC Loss, Count | Blend of CL and IE; primary for years 30–70% developed |
| Reported Count CL | WC Count | Only count measure available; no Closed Count data provided |
| Frequency-Severity | Not applicable | Not implemented in this analysis |

### 4.2 Method Weighting / Selection Logic
LDF selections were made by a 14-criteria rules-based AI framework applied to each development interval independently, with an open-ended AI providing an independent cross-check. The framework weights volume-weighted averages, evaluates coefficient of variation, identifies outlier periods, and applies maturity-based averaging windows.

Ultimate selections blend methods by accident year maturity: mature years (96+ months, 98%+ developed) use Incurred CL as primary; mid-maturity years use BF with Incurred ELR; immature years (2022–2024) weight BF more heavily due to thin CL data. AY 2007 carries elevated paid development consistent with a large-loss year and was selected using Incurred CL after review of the elevated diagonal.

### 4.3 LAE Treatment
**Not applicable.** This analysis assumes loss triangles include LAE (loss and allocated loss adjustment expense combined), or LAE is not being estimated separately. If LAE needs to be estimated separately, that is outside the scope of this workflow.

- **DCC / ALAE:** Not separately estimated
- **A&O / ULAE:** Not separately estimated

---

## 5. Key Assumptions

### 5.1 Development Patterns
- **Selection basis:** Volume-weighted averages evaluated over multiple averaging windows (3-year, 5-year, all-year) with outlier exclusion. Rules-based framework selected the optimal window per interval based on stability, volume, CV, and trend diagnostics. Open-ended AI provided a cross-check; both selectors showed close agreement on most intervals.
- **Tail — Paid Loss:** `exp_dev_product` method selected (cutoff age 263); implied tail factor 1.0023. Both selectors agreed. Bondy also considered (tail 1.0076) — product form preferred for gap compliance.
- **Tail — Incurred Loss:** `exp_dev_product` method selected (cutoff age 263); implied tail factor 1.0004. Rules-based and open-ended selectors agreed on product form; minimal tail development expected given case reserve finalization.
- **Tail — Reported Count:** `exp_dev_product` method selected (cutoff age 275); tail factor 1.0000. Count fully developed by cutoff — tail is immaterial.

### 5.2 Expected Loss Ratios (for B-F and ELR methods)
ELR derived from 3-year rolling average of diagonal incurred loss per dollar of payroll exposure (fallback approximation — no pricing ELR file provided). Key ELRs by selected AY period:

| AY | Approx. ELR (Incurred / Payroll) | Basis |
|---|---|---|
| 2001–2005 | ~0.007–0.010 | Empirical rolling average |
| 2006–2015 | ~0.004–0.008 | Empirical rolling average |
| 2016–2024 | ~0.002–0.005 | Empirical rolling average |

Full ELR table available in `processed-data/` output files.

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
- **LDF selections:** Based on volume-weighted averages with 14-criteria rules-based framework and open-ended AI cross-check. Per-interval reasoning documented in `selections/Chain Ladder Selections - LDFs.xlsx` (purple AI Selection rows with embedded rationale).
- **Tail factors:** `exp_dev_product` selected for all three measures based on gap compliance and fit diagnostics. Skurnick and exact-last variants produced unreasonable tails (2.9×, 1.9×) and were excluded. Full diagnostics in `selections/Chain Ladder Selections - Tail.xlsx`.
- **Expected loss ratios:** Empirical fallback — 3-year rolling average of diagonal incurred loss per payroll exposure. This is less forward-looking than a pricing ELR and should be reviewed against underwriting expectations (flagged in Section 11).
- **Count tail:** Reported count fully developed by age 275 for all years; tail = 1.000 with high confidence.

*Any assumption primarily judgment-driven is flagged in Section 11.*

---

## 6. Results by Segment

*Detailed exhibits live in the accompanying workbook; summarize selections and rationale here.*

### 6.1 Loss (Workers Compensation)
- **Selected ultimate:** $46,817,341 across AY 2001–2024
- **Paid to date:** $41,767,854 | **Case reserves:** $1,848,541 | **IBNR:** $3,200,946
- **Method weighting:** Incurred CL primary for AYs 2001–2019 (high maturity, stable patterns); BF primary for AYs 2020–2024 (immature, CL tail amplifies uncertainty). See `selections/Ultimates.xlsx` Loss sheet for per-AY selections and reasoning.
- **Notable judgment calls:** AY 2007 — elevated paid diagonal ($4.8M vs. ~$1–2M peer years). Incurred CL selected; large-loss year consistent with WC clerical book. AY 2015 also elevated; Incurred CL confirmed reasonable. Immature years (2022–2024) rely on BF/IE which are sensitive to ELR fallback quality.

### 6.2 Count (Reported Claims)
- **Selected ultimate:** ~9,752 reported claims across AY 2001–2024
- **Reported to date:** 9,716 | **IBNR count:** 36 (concentrated in 2023–2024)
- **Method weighting:** Reported Count CL used throughout — count development is essentially complete by age 35 for most years. Minor negative IBNR in several periods (2005–2022) reflects slight over-reporting at early ages; within tolerance.
- **Notable judgment calls:** No Closed Count data available, so closure rate analysis was not possible.

---

## 7. Diagnostics and Reasonableness Checks

- [x] Loss ratios by AY — reasonable progression. AY 2007 and 2015 show elevated incurred loss ratios consistent with identified large-loss years; remaining years within expected range for low-hazard clerical WC.
- [x] Frequency / severity trends — count stabilizes quickly (by age 35); severity patterns consistent with long-tail WC development.
- [x] Implied paid and reported development — patterns consistent with chain ladder selections; paid development longer than incurred as expected.
- [ ] Actual vs. expected emergence since prior review — Not applicable; no prior estimate available.
- [ ] Comparison to independent benchmark — Not performed; no external benchmark data available.
- [ ] Hindsight test on prior ultimates — Not performed; no prior ultimates available.
- [x] Ratio of IBNR to case reserves — IBNR ($3.2M) is ~1.7× case reserves ($1.85M), which is reasonable for a mature WC book with most years well-developed.

**Anomalies to investigate:**
- **Tech Review WARN — Loss: 1 period > 10× median ultimate** — AY 2007 selected ultimate of ~$1.54M flagged as outlier vs. median. This is the large-loss year discussed above; selected ultimate reflects actual diagonal, not an error.
- **Tech Review WARN — Count: slight negatives in IBNR** for 7 periods (2005, 2006, 2007, 2012, 2014, 2017, 2022) — values within tolerance; reflect reported count slightly exceeding selected ultimate for mature periods. No restatement required.
- **Tech Review WARN — Count: 1 period > 10× median** — AY 2024 at age 11 has 346 selected count (34 IBNR). Rational for the most immature year; not an error.

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
- **Process risk:** Inherent randomness in claim emergence and settlement; limited development history for AY 2022–2024 increases variance.
- **Parameter risk:** LDF selection uncertainty for mature intervals is low (stable, high-volume patterns). Tail factor uncertainty is moderate — `exp_dev_product` tail of 1.002–1.014 across measures; alternative Bondy tail for paid (1.008) would shift reserve by <$50K. ELR fallback introduces meaningful parameter risk for BF-weighted years.
- **Model risk:** BF vs. CL weighting for immature years (2022–2024) is the key model choice. A pure CL approach would yield higher ultimates (CDF 1.4–3.2× for the youngest years); the BF blend reduces this sensitivity.
- **Systemic risk:** AY 2007 large-loss year has not been separately examined; if a single large claim reopens or escalates, the reserve for that year could change materially. No explicit large-loss loading has been applied.

---

## 9. Reliance on Others

| Source | Information Relied Upon |
|---|---|
| Triangle Examples 1.xlsx (internal data file) | Paid loss, incurred loss, reported count, and payroll exposure triangles — accepted as provided |
| No external sources relied upon | No industry benchmarks, external actuarial data, or third-party information used in this analysis |

---

## 10. Information Date and Subsequent Events

- **Information Date:** ~November 30, 2024 (inferred from 11-month initial development age for AY 2024)
- **Subsequent events considered:** None known as of 2026-04-30.

---

## 11. Open Questions for Reviewer

*The key section — where you flag judgment calls you want a second opinion on.*

1. **AY 2007 large-loss year** — Paid and incurred diagonal is $4.8M, roughly 2–3× peer years at similar maturity. Selected Incurred CL ultimate. Is there a known large claim in this year? Should it be separately capped and loaded?
2. **ELR fallback quality** — BF/IE ELRs are derived from a 3-year rolling average of empirical loss rates, not pricing ELRs. For AY 2022–2024 where BF is the primary method, this approximation drives the result. Do underwriting ELRs exist that should be substituted?
3. **Count IBNR slight negatives** — 7 mature periods show IBNR slightly below zero (actual > selected ultimate by a small amount). This is within tolerance; confirm these periods are considered fully developed and no restatement is needed.
4. **AY 2015 elevated development** — Similar to 2007, AY 2015 shows elevated paid emergence at age 119 ($3.4M). Any known large-loss explanation?

**Items I'm flagging as low-confidence:**
- ELR assumptions for BF method (AY 2020–2024) — dependent on fallback approximation
- AY 2024 ultimate (age 11 only) — extremely immature; BF selection is highly speculative

**Items I think should be escalated to Chief Actuary / Committee:**
- AY 2007 and AY 2015 elevated development — recommend confirming no open large claims before accepting selections

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
| v0.1 | 2026-04-30 | Bryce | Initial draft — data intake, LDF/tail selections, ultimates, tech review complete |

---

## Appendices (in accompanying workbook)

- A. Triangles (paid, reported, counts)
- B. Development factor selections
- C. Method indications by segment / AY
- D. Diagnostic exhibits
- E. Data reconciliation worksheet

---

*End of working draft.*