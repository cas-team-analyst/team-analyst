# Reserving Analysis — Working Draft

**Analysis:** CAS RFP Demo — Reserving Analysis
**Valuation Date:** 12/31/2024
**Draft Version:** v0.1 — Initial Draft
**Prepared by:** Bryce
**Submitted to:** [Reviewing Actuary Name]
**Draft Date:** 04/21/2026

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

- **What this analysis covers:** [1–2 sentences]
- **What changed since last review (if applicable):** [Bullet the deltas]
- **Where I want the most scrutiny:** [Point the reviewer at the judgment calls]
- **Open questions for reviewer:** See Section 11

---

## 1. Purpose and Scope

### 1.1 Purpose of the Analysis
This analysis is a full actuarial reserve review using the TeamAnalyst plugin workflow. It develops ultimate loss estimates for accident years 2015-2024 using Chain Ladder (Paid and Incurred), Initial Expected Loss Rate, and Bornhuetter-Ferguson methods, and selects final ultimates across methods.

### 1.2 Scope
| Item | Detail |
|---|---|
| Segment(s) / LOB | Single segment (all-lines combined) |
| Accident / Underwriting years | 2015–2024 (10 years) |
| Coverages | Loss |
| Basis | Gross |
| Currency | USD |
| Geography | TBD |

### 1.3 Intended Internal Users
[e.g., Chief Actuary, Reserving Committee, CFO]. This draft is not intended for external distribution in its current form.

---

## 2. Summary of Indications

*Placeholder numbers — subject to review.*

| Segment | Paid to Date | Case | IBNR | Total Unpaid | Ultimate |
|---|---|---|---|---|---|
| [ ] | | | | | |
| [ ] | | | | | |
| **Total** | | | | | |

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
| Incurred loss triangle | canonical-triangles.xlsx (Incurred sheet) | 12/31/2024 | 10 AYs x 10 dev ages, cumulative |
| Paid loss triangle | canonical-triangles.xlsx (Paid sheet) | 12/31/2024 | 10 AYs x 10 dev ages, cumulative |
| Reported claim counts | canonical-triangles.xlsx (Reported sheet) | 12/31/2024 | 10 AYs x 10 dev ages |
| Closed claim counts | canonical-triangles.xlsx (Closed sheet) | 12/31/2024 | 10 AYs x 10 dev ages |
| Exposure | canonical-triangles.xlsx (Exposure sheet) | 12/31/2024 | 10 AYs x 10 dev ages |
| Expected Loss Rate & Frequency | canonical-elrs.xlsx (ELR sheet) | 12/31/2024 | 10 accident periods, used for IE and BF methods |

### 3.2 Data Reconciliation
- No prior valuation provided for reconciliation. This is treated as an initial analysis.
- Data files appear internally consistent; accident year row labels use Excel formulas (`=A2+1` etc.) which are resolved during data intake.

### 3.3 Data Quality Observations
*Per ASOP No. 23 — flag anything unusual.*

- All five triangle measures are complete (10 AYs x 10 dev ages) with a standard upper-left triangular structure; no gaps observed.
- Paid and Incurred losses converge by dev age 120 (consistent with a finite-tailed line).
- Reported and Closed claim count triangles show normal closure patterns.
- Exposure triangle is non-cumulative in shape (policy count / earned units per development period).
- ELR file provides both expected loss rate and expected frequency for all 10 AYs — sufficient for Initial Expected and BF methods.
- No obvious outliers or negative development noted at this stage; further diagnostics will be run in Step 3.

### 3.4 Data Limitations
- No prior LDF or tail factor selections provided; all selections will be made fresh in this analysis.
- No rate change history or trend factors were provided; IE ELRs are taken as given from the input file.
- Accident year labels in source data use Excel formulas — resolved during data intake (Step 3).

---

## 4. Methodology

### 4.1 Methods Applied
| Method | Segments Applied | Why Selected |
|---|---|---|
| Paid Loss LDF | All AYs 2015–2024 | Primary loss development method; stable paid patterns. Selected via rule-based framework + AI cross-check. |
| Incurred Loss LDF | All AYs 2015–2024 | Incurred development provides early-maturity signal. Selected via rule-based framework + AI cross-check. |
| Initial Expected (IE) | All AYs 2015–2024 | ELR file available; used for BF weighting and as cross-check on immature years. |
| Bornhuetter-Ferguson (BF) | All AYs 2015–2024 | Blends LDF and IE methods; particularly useful for immature accident years. |
| Reported Count LDF | Diagnostic only | Used to validate frequency patterns; not used for loss ultimate selection. |
| Closed Count LDF | Diagnostic only | Used to validate closure rate patterns; not used for loss ultimate selection. |

### 4.2 Method Weighting / Selection Logic
LDF selections were made using a 14-criteria rules-based framework applied by an AI selector, with an independent open-ended AI selector providing a cross-check. The two selectors agreed within 1.4% on all intervals; the only material divergence was Paid Loss 12-24 (1.8058 vs. 1.8309) and Reported Count 12-24 (1.6816 vs. 1.6631). The Rules-Based AI Selection row is used for all ultimates with no manual overrides. Primary emphasis was placed on volume-weighted averages with window length guided by CV and slope diagnostics: shorter windows (3–5yr) where recent trends were detected, longer windows (all/10yr) where development was stable.

### 4.3 LAE Treatment
- **DCC / ALAE:** [Analyzed with loss / separately / ratio method]
- **A&O / ULAE:** [Paid-to-paid ratio / other]

---

## 5. Key Assumptions

### 5.1 Development Patterns
- **Selection basis:** [e.g., volume-weighted 5-year average with outlier adjustment]
- **Tail:** [Source — curve fit, industry benchmark, judgment]

### 5.2 Expected Loss Ratios (for B-F and ELR methods)
| AY | ELR | Basis |
|---|---|---|
| | | |

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

### 6.1 [Segment A]
- Selected ultimates: [Reference exhibit]
- Method weighting: [Summary]
- Notable judgment calls: [ ]

### 6.2 [Segment B]
- [ ]

---

## 7. Diagnostics and Reasonableness Checks

- [ ] Loss ratios by AY — reasonable progression?
- [ ] Frequency / severity trends — consistent with assumptions?
- [ ] Implied paid and reported development — consistent with patterns?
- [ ] Actual vs. expected emergence since prior review
- [ ] Comparison to independent benchmark (if available)
- [ ] Hindsight test on prior ultimates
- [ ] Ratio of IBNR to case reserves — reasonable?

**Anomalies to investigate:** [List anything the diagnostics flagged]

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

- Process / parameter / model / systemic risk commentary as applicable
- Segment-specific risk factors: [ ]

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
- [ ]

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
| v0.1 | | | Initial draft |
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