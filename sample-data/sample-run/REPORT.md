# Reserving Analysis — Working Draft

**Analysis:** Sample Run
**Valuation Date:** [MM/DD/YYYY — to be confirmed from data]
**Draft Version:** v0.1 — Working Draft
**Prepared by:** John Doe
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

- **What this analysis covers:** [1–2 sentences]
- **What changed since last review (if applicable):** [Bullet the deltas]
- **Where I want the most scrutiny:** [Point the reviewer at the judgment calls]
- **Open questions for reviewer:** See Section 11

---

## 1. Purpose and Scope

### 1.1 Purpose of the Analysis
Sample actuarial reserving analysis run using the TeamAnalyst workflow to demonstrate the end-to-end process from triangle data intake through ultimate selections and technical review.

### 1.2 Scope
| Item | Detail |
|---|---|
| Segment(s) / LOB | Workers' Compensation — low hazard clerical |
| Accident / Underwriting years | 2001–2024 (24 years) |
| Coverages | Loss (combined with LAE — not separately estimated) |
| Basis | Gross (assumed — not specified in source data) |
| Currency | USD |
| Geography | Not specified in source data |

### 1.3 Intended Internal Users
Internal actuarial team. This draft is not intended for external distribution in its current form.

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
| Paid loss triangle | Triangle Examples 1.xlsx — sheet "Paid 1" | YE 2024 | AY 2001–2024, ages 11–287 months, 24 accident years × 24 evaluation ages |
| Incurred loss triangle | Triangle Examples 1.xlsx — sheet "Inc 1" | YE 2024 | Same structure as paid |
| Claim count triangle | Triangle Examples 1.xlsx — sheet "Ct 1" | YE 2024 | Reported counts, AY 2001–2024; no closed count triangle available |
| Exposure (payroll) | Triangle Examples 1.xlsx — sheet "Exposure" | YE 2024 | Annual payroll by AY; 2001 = $316M, grows at ~2%/yr to 2024 = $499M |

**Line of business:** Workers' Compensation (low-to-medium hazard clerical — per Tri 1 metadata)

### 3.2 Data Reconciliation
Not reconciled — data accepted as provided by source file "Triangle Examples 1.xlsx".

### 3.3 Data Quality Observations
*Per ASOP No. 23 — flag anything unusual.*

- AY 2007 shows notably elevated paid loss at latest diagonal ($4,790,693) compared to surrounding years ($1.1M–$2.5M range). Potential large loss or mix shift; flagged for review during LDF selections.
- Exposure rows for AY 2002–2024 are formula-driven (=prior year × 1.02) — a 2% annual payroll growth assumption is embedded. Accepted as provided.
- Claim count triangle (Ct 1) uses fractional counts, suggesting blended or weighted count data rather than integer claim counts. No closed count triangle is present.

### 3.4 Data Limitations
- No initial expected loss rate (ELR) file provided. IE and BF methods will use the fallback approximation: diagonal loss per dollar of exposure smoothed with a 3-year rolling average, rounded to 3 decimals.
- No closed count triangle available — only reported counts can be used for count-based projections.
- No prior LDF or tail factor selections available for comparison (new analysis, no prior valuation data).

---

## 4. Methodology

### 4.1 Methods Applied
| Method | Segments Applied | Why Selected |
|---|---|---|
| Paid LDF (Chain Ladder) | WC — all AYs | Primary method; long paid history available through 287 months |
| Incurred LDF (Chain Ladder) | WC — all AYs | Cross-check on paid; incurred converges earlier than paid |
| Reported Count LDF (Chain Ladder) | WC — all AYs | Supports frequency/severity analysis and count-based ultimates |
| Initial Expected (BF fallback) | WC — all AYs | Fallback ELR via 3yr rolling diagonal/exposure average |
| Bornhuetter-Ferguson | WC — all AYs | Blends CL and IE; primary method for immature AYs (< 5 yrs) |

### 4.2 Method Weighting / Selection Logic
LDF selections were made using a rules-based framework with an open-ended AI cross-check. For each development interval the framework evaluated: volume-weighted vs. simple averages across 3-, 5-, and all-year windows; coefficient of variation (CV) to assess stability; slope diagnostics to detect trend; and outlier exclusion (high/low) when CV exceeded 0.10. Recent-year windows were favored where an upward trend was detected; all-year averages were favored in stable, mature intervals. Both AI selectors independently selected LDFs; the rules-based selection is used for ultimates by default.

At early maturities (11-23 months) for Paid Loss, the rules-based selector identified a statistically significant upward slope in recent years (3yr slope = 0.63 vs. all-year = 0.11) and applied asymmetric conservatism. At very late maturities (beyond ~227-275 months depending on measure) data becomes extremely sparse and a tail curve is more appropriate; LDF selections stop at those cutoff points.

### 4.3 LAE Treatment
**Not applicable.** This analysis assumes loss triangles include LAE (loss and allocated loss adjustment expense combined), or LAE is not being estimated separately. If LAE needs to be estimated separately, that is outside the scope of this workflow.

- **DCC / ALAE:** Not separately estimated
- **A&O / ULAE:** Not separately estimated

---

## 5. Key Assumptions

### 5.1 Development Patterns
- **Selection basis:** Volume-weighted averages with windows from 3-year to all-year. Rules-based framework selected the optimal window per interval based on CV stability, volume, slope diagnostics, and data sparsity. Outlier exclusion applied when 5yr CV > 0.10.
- **Tail:** To be selected via curve fitting diagnostics (Bondy, Exponential Decay, McClenahan, Skurnick). LDF selections terminate at the following cutoff ages — beyond these, tail factors from curve fitting will be applied: Paid Loss ~275 months (rules-based) / ~227 months (open-ended); Incurred Loss ~275 months / ~227 months; Reported Count ~275 months / ~227 months.

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
- **Expected loss ratios (if used):** [Fill in source if BF/IE methods were used, otherwise note "Not applicable - CL only"]

*Any assumption primarily judgment-driven should be flagged in Section 11.*

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
**Not implemented in this analysis.** Sensitivity testing would require re-running projections with varied assumptions. This can be added in future iterations.

| Assumption | Change | Impact on Total Ultimate |
|---|---|---|
| Tail factor | ± (not tested) | (not tested) |
| ELR | ± (not tested) | (not tested) |
| LDF selections | ± (not tested) | (not tested) |

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

1. **AY 2007 large loss:** Paid and incurred at latest diagonal are materially elevated vs. surrounding years ($4.8M paid vs. ~$1.1M–$2.5M range). This drives higher LDFs in the 47-107 month intervals. Is there a known large loss or mix shift in AY 2007? Should it be excluded or capped for LDF averaging?
2. **Incurred Loss 11-23 divergence:** Rules-based selector chose 1.5324; open-ended chose 1.6456 (6.9% difference). This is the most volatile interval with high early-period development. Review the AI reasoning in the LDF workbook and confirm which direction feels right.
3. **Paid Loss 23-35 divergence:** Rules-based = 1.3658, open-ended = 1.4435 (5.4% difference). Both identify volatility in this interval; the open-ended selector gave more weight to a recent upward trend. Confirm preferred selection.
4. **Tail cutoff age:** Rules-based selectors suggest a tail attach point of ~275 months; open-ended selectors suggest ~227 months. This will be resolved in the tail factor selection step — flagging here for awareness.

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
| v0.1 | 04/29/2026 | John Doe | Initial draft |
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