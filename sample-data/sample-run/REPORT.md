# Reserving Analysis — Working Draft

**Analysis:** Sample Run — Workers Compensation
**Valuation Date:** 12/31/2024
**Draft Version:** v0.1 — Working Draft
**Prepared by:** Bryce
**Submitted to:** [Reviewing Actuary Name]
**Draft Date:** 04/25/2026

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

- **What this analysis covers:** Workers Compensation sample run (CAS example data), AYs 2001–2024, as of 12/31/2024. Paid LDF, Incurred LDF, IE (fallback ELR), and BF methods applied.
- **What changed since last review:** First-time analysis — no prior.
- **Where I want the most scrutiny:** (1) Paid Loss tail factor divergence (1.004 vs. 1.047 between selectors); (2) AYs 2023–2024 ultimate selections — very green with CDFs of 2.7× and 7.1×; (3) Paid ultimate exceeding incurred for AYs 2017, 2021–2023; (4) IE fallback ELR producing negative IBNR in several AYs.
- **Open questions for reviewer:** See Section 11

---

## 1. Purpose and Scope

### 1.1 Purpose of the Analysis
This is a sample/test run using CAS example Workers Compensation triangle data. The purpose is to produce sample analysis output using the TeamAnalyst reserving workflow, not to support a specific reserving or pricing decision.

### 1.2 Scope
| Item | Detail |
|---|---|
| Segment(s) / LOB | Workers Compensation — lots of clerical, relatively low hazard |
| Accident / Underwriting years | 2001–2024 (24 accident years) |
| Coverages | Loss (Paid and Incurred) |
| Basis | Direct / Gross |
| Currency | USD |
| Geography | Not specified (sample data) |

### 1.3 Intended Internal Users
[e.g., Chief Actuary, Reserving Committee, CFO]. This draft is not intended for external distribution in its current form.

---

## 2. Summary of Indications

*Placeholder numbers — subject to review.*

| Measure | Paid to Date | Case Reserves | IBNR | Total Unpaid | Ultimate |
|---|---|---|---|---|---|
| Paid LDF | $41,768K | $1,849K | $5,091K | $6,940K | $48,708K |
| Incurred LDF | $41,768K | $1,849K | $7,073K | $8,921K | $50,689K |
| **Selected (Paid)** | **$41,768K** | **$1,849K** | **$5,091K** | **$6,940K** | **$48,708K** |

**Comparison to prior estimate:**

| Segment | Prior Ultimate | Current Ultimate | Change | % |
|---|---|---|---|---|
| [ ] | | | | |

**Key drivers of change:** [Brief narrative — emergence vs. expected, assumption changes, new data, etc.]

---

## 3. Data

### 3.1 Data Used
| Data Element | Source | As-of Date | Notes |
|---|---|---|---|
| Paid loss triangles | Triangle Examples 1.xlsx — Sheet: Paid 1 | 12/31/2024 | 24 AYs × 24 dev ages (11–287 months); upper triangle |
| Incurred loss triangles | Triangle Examples 1.xlsx — Sheet: Inc 1 | 12/31/2024 | Same structure as paid |
| Reported claim counts | Triangle Examples 1.xlsx — Sheet: Ct 1 | 12/31/2024 | Same structure as paid/incurred |
| Payroll exposure | Triangle Examples 1.xlsx — Sheet: Exposure | 12/31/2024 | Annual payroll by AY; range $316M–$499M |

### 3.2 Data Reconciliation
- No prior valuation or external financial system to reconcile against; this is a standalone sample analysis using CAS example data.
- Internal triangles are self-consistent: paid ≤ incurred across all AY/age cells.

### 3.3 Data Quality Observations
*Per ASOP No. 23 — flag anything unusual.*

- Paid losses show slight negative development in a few AY/age cells (e.g., AY 2003 ages 59–71 and 71–83), likely reflecting salvage/subrogation or case closures; no adjustment applied as magnitudes are small.
- Incurred losses also show isolated negative development at older ages (maturity convergence), consistent with WC claims nearing closure.
- Claim counts plateau quickly — most AYs reach ultimate count by age 35–47, consistent with a clerical/low-hazard WC book where claims report quickly.
- No obvious coding anomalies, gaps, or data quality issues that require correction.

### 3.4 Data Limitations
- No expected loss rate or ELR file was provided; Initial Expected and Bornhuetter-Ferguson methods will use a fallback approximation (3-year rolling average of paid loss per dollar of payroll exposure).
- No prior LDF or tail factor selections available; AI selectors will make first-time selections without a prior-period benchmark.
- Exposure (payroll) is provided as a single annual figure per AY — used as a proxy for earned exposure in BF calculations.

---

## 4. Methodology

### 4.1 Methods Applied
| Method | Segments Applied | Why Selected |
|---|---|---|
| Paid LDF | All AYs 2001–2024 | Selected via rule-based framework + AI cross-check |
| Incurred LDF | All AYs 2001–2024 | Selected via rule-based framework + AI cross-check |
| Reported Count LDF | All AYs 2001–2024 | Selected via rule-based framework + AI cross-check |
| Paid B-F | All AYs 2001–2024 | Ran — ELR from fallback (3-yr rolling avg of incurred per payroll) |
| Incurred B-F | All AYs 2001–2024 | Ran — ELR from fallback (3-yr rolling avg of incurred per payroll) |
| Initial Expected | All AYs 2001–2024 | Ran — same ELR as BF; IE provides pure a priori benchmark |

### 4.2 Method Weighting / Selection Logic
LDF selections used a 14-criteria rule-based framework applied independently to each measure, with a parallel open-ended AI selector providing an independent cross-check. The framework evaluates volume-weighted and simple averages over 3-year and 5-year windows, flags high CV intervals, applies convergence overrides where averages cluster within ±2%, and uses sparse-data caution at late maturities. Divergences between the rule-based and open-ended selections are noted in Section 11.

### 4.3 LAE Treatment
- **DCC / ALAE:** [Analyzed with loss / separately / ratio method]
- **A&O / ULAE:** [Paid-to-paid ratio / other]

---

## 5. Key Assumptions

### 5.1 Development Patterns
- **Selection basis:** Volume-weighted and simple averages over 3-year and 5-year windows; convergence overrides applied where averages cluster within ±2%; sparse-data caution applied at maturities where fewer than 3 observations exist.
- **Tail:** Curve fitting via Bondy, modified Bondy, double exponential (log-quadratic), exp_dev, McClenahan, and Skurnick methods. Leave-one-out diagnostics used to assess stability. Final selections: Paid Loss = 1.0039 (Bondy, rules-based) / 1.0472 (exp_dev_quick_exact_last, open-ended); Incurred Loss = 1.0216 (double_exp, age 203, both selectors); Reported Count = 1.0000 (both selectors — counts fully developed by age 35–47).

### 5.2 Expected Loss Ratios (for B-F and ELR methods)
No ELR file was provided. Fallback method: for each AY, incurred loss per dollar of payroll from the diagonal, smoothed with a 3-year rolling average and rounded to 3 decimals. This is the default fallback in `3-ie-ultimates.py`.

| Measure | Total IE Ultimate | Basis |
|---|---|---|
| Incurred Loss | $46.0M | Fallback ELR × payroll |
| Paid Loss | $46.0M | Same ELR applied to paid |

Note: IE ultimates for AY 2005 are below current diagonal (negative implied IBNR), reflecting that actual 2005 development ran above the smoothed average — a known limitation of the rollling-average fallback for volatile AYs.

### 5.3 Trend Assumptions
| Segment | Frequency | Severity | Pure Premium |
|---|---|---|---|
| | | | |

### 5.4 Other Assumptions
- **Rate change:** [ ]
- **Case reserve adequacy:** [Assumed stable / Adjustment applied]
- **Settlement rate / claim closing patterns:** [ ]
- **Mix / law / tort environment:** [ ]

### 5.5 Assumption Rationale
*For each material assumption, note the rationale and supporting evidence. Flag any that are primarily judgment-driven.*

---

## 6. Results by Segment

*Detailed exhibits live in the accompanying workbook; summarize selections and rationale here.*

### 6.1 Paid Loss
- Selected ultimates: $48,708K total (see `selections/Ultimates.xlsx`)
- Method weighting: Mature AYs (2001–2010) ~70% CL / 20% BF / 10% IE; mid-maturity 40–55% CL; green years (2020+) 80–90% BF
- Notable judgment calls: AYs 2023–2024 rely heavily on BF given CDFs of 2.7× and 7.1× respectively; IE method deprioritized throughout due to negative IBNR signals from fallback ELR

### 6.2 Incurred Loss
- Selected ultimates: $50,689K total (see `selections/Ultimates.xlsx`)
- Method weighting: Similar maturity-based weighting as paid; incurred CL primary for AYs 2001–2014, BF dominant for 2018+
- Notable judgment calls: IE showed systematic negative IBNR across multiple AYs indicating fallback ELR is understated; CL and BF provided more consistent indications

### 6.3 Reported Count
- Selected ultimates: 9,747 claims (see `selections/Ultimates.xlsx`)
- Method: 100% Chain Ladder — counts fully developed (CDF = 1.0) for AYs 2001–2023; only AY 2024 has residual development (~31 claims)

---

## 7. Diagnostics and Reasonableness Checks

- [x] Loss ratios by AY — reasonable progression: Paid loss rate ranges 0.002–0.014 per payroll dollar; AY 2007 is notably large (likely large-loss year)
- [x] Frequency/severity trends — 13 AYs show >25% YoY severity change; 5 AYs show frequency >2× median. Consistent with small/volatile WC book
- [x] Implied paid/reported development — consistent with patterns; 31 negative link ratio cells in incurred (expected for WC closure activity)
- [ ] Actual vs. expected emergence — no prior valuation to compare against
- [ ] Comparison to independent benchmark — not performed (sample data)
- [ ] Hindsight test — not applicable (first-time analysis)
- [x] IBNR to case ratio — incurred IBNR ($7.1M) vs. case ($1.8M) ~3.8×; elevated ratio reflects young AYs with large IBNR loading

**Anomalies to investigate:**
- AY 2010 Paid Loss selection ($1,359K) falls slightly outside method indication range [$1,134K–$1,350K] — review open-ended selector reasoning
- AYs 2017, 2021–2023: paid selected ultimate exceeds incurred selected — cross-check LDF and tail factor assumptions
- IE method produces negative IBNR in AY 2005, 2007, and several others — fallback ELR may be understated for high-development AYs

---

## 8. Sensitivity and Uncertainty

### 8.1 Sensitivity to Key Assumptions
| Assumption | Change | Impact on Total Ultimate |
|---|---|---|
| Tail factor | ± [ ] | [ ] |
| ELR | ± [ ] | [ ] |
| Severity trend | ± [ ] | [ ] |

### 8.2 Sources of Uncertainty
*Per ASOP No. 43 — discuss the risks that could cause actuals to differ from estimate.*

- **Process risk:** Thin data — 24 AYs with a single risk group; individual large losses can materially shift results
- **Parameter risk:** Tail factor selection uncertainty (1.004–1.047 range for paid); ELR fallback approximation is unvalidated
- **Model risk:** CL and BF both rely on development pattern stability; WC development patterns can shift with medical cost trends or legislative changes
- **Systemic risk:** No external benchmark available for this sample dataset; results should not be interpreted as production reserve estimates

---

## 9. Reliance on Others

| Source | Information Relied Upon |
|---|---|
| [Claims / Underwriting / Finance contact] | [ ] |
| [External benchmark or data source] | [ ] |

---

## 10. Information Date and Subsequent Events

- **Information Date:** [ ]
- **Subsequent events considered:** [None known / Describe]

---

## 11. Open Questions for Reviewer

*The key section — where you flag judgment calls you want a second opinion on.*

1. [Specific question with context — e.g., "AY 2023 paid emergence is 15% below expected; I kept selections unchanged pending more data. Agree?"]
2. [ ]
3. [ ]

**Items I'm flagging as low-confidence:**
- Paid Loss tail: rules-based selected 1.0039 (conservative Bondy — materiality anchor applied given tail < 0.1% of CDF) vs. open-ended 1.0472 (exp_dev_quick_exact_last, R²=0.204). Low R² on the exponential fit suggests curve may be overfitting sparse late-age data. Rules-based selection of 1.0039 is used for ultimates by default.

**Items I think should be escalated to [Chief Actuary / Committee]:**
- Paid Loss tail factor divergence (1.0039 vs. 1.0472) — modest dollar impact but worth flagging given WC long-tail nature.

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
| v0.1 | 04/25/2026 | Bryce | Complete first draft — all steps through tech review |
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