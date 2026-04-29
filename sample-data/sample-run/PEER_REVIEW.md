# Peer Review — Workers Compensation (WC), AYs 2001–2024

**Analysis folder:** C:\Users\super\Documents\actuarial\cas-rfp\spec-only\team-analyst\sample-data\sample-run
**Review date:** 04/29/2026
**Status:** Advisory — no selections were modified

**Files reviewed:**
- Analysis.xlsx
- Tech Review.xlsx
- REPORT.md
- REPLICATE.md

---

## Summary

This is a well-structured first analysis with clear documentation of methodology, assumptions, and open questions. The headline reserve ($6.6M unpaid, $48.3M selected ultimate) is plausible for a WC book of this size and development history. However, three issues warrant resolution before this analysis is finalized: (1) method labels in the selection JSON files are inconsistent with the actual values used for approximately nine accident years, creating a reproducibility gap; (2) the open-ended selector produces $3.2M more reserve than the rules-based selector for AYs 2023–2024 alone, and that divergence is not fully resolved in the narrative; and (3) the Technical Review was run against the wrong file (values-only export), causing 11 of 17 check groups to be skipped entirely.

---

## High-Priority Findings

1. **Method label inconsistency — rules-based JSON vs. actual values** (§Diagnostic Consistency, §Documentation Quality): For nine accident years labeled "Paid CL" in the rules-based selector JSON, the numerical selection value matches Paid BF, not Paid CL. The REPORT.md and REPLICATE.md narrative ("Paid CL for AYs 2001–2018") does not reflect what was actually computed. This is an ASOP 41 documentation gap and a REPLICATE.md reproducibility issue. See Proposed Alternatives §1.

2. **AY 2023–2024 RB vs. OE divergence — $3.2M total** (§Cross-Method Consistency, §Recent Year Stability): The rules-based selector (BF) produces $1,846,681 and $1,224,415 for AYs 2023 and 2024; the open-ended selector (CL) produces $3,546,476 and $2,755,833 — a combined difference of $3,230,233 on a total selected IBNR of $4,721,077. This is the largest single uncertainty driver in the analysis and deserves explicit scenario discussion.

3. **Technical Review ran against values-only file** (§Technical Review Diagnostics): `7-tech-review.py` was run against `Analysis.xlsx` (values-only export). Eleven of seventeen check groups were marked WARN/skipped for this reason, including paid-to-incurred ratio checks, case reserve reasonableness, severity/frequency trends, development factor validation, and closure rate checks. These checks were not actually performed.

---

## Detailed Findings

### Cross-Method Consistency

**Paid CL < Incurred CL across 14 of 24 accident years.** The analysis shows Paid CL ultimate is systematically lower than Incurred CL ultimate for AYs 2001–2012 (all but AY 2010 and 2013) and AY 2024. The shortfall ranges from $15K (AY 2003) to $174K (AY 2012). This pattern is unusual: paid development factors at most age intervals exceed incurred factors (as expected), so the paid CDF should generally be larger or roughly equal to the incurred CDF at any given age. The consistent reversal at the cumulative level warrants investigation.

One likely explanation is that the paid tail factor (1.0039) is materially lower than the incurred tail (1.0119), creating a structural bias toward lower paid ultimates despite paid LDFs being higher at most individual intervals. For a WC line with long-tail characteristics, it may be worth considering whether 1.0039 for paid is too light relative to the line's characteristics. (The open-ended tail selector agreed on 1.0039 for paid, but chose 1.0251 for incurred — a larger gap.) See Proposed Alternatives §3.

**Method bias — BF vs. development:** The BF ultimates are consistently lower than Paid CL for AYs 2016–2024 (ranges from −2% for AY 2016 to −55% for AY 2024). For AYs 2001–2015, BF and Paid CL are broadly consistent. The a priori rates driving BF (fallback rolling-average ELRs) appear to anchor toward moderate development scenarios. This may be appropriate given the thin data at recent ages, but the asymmetry in the BF vs. CL direction for immature years should be explicitly acknowledged in the report.

**AY 2017 — paid CL below incurred CL by $61K:** AY 2017 is labeled in the JSON as "Paid CL" but the selected value ($1,708,556) matches Paid BF, not Paid CL ($1,494,051). If the selection truly is BF, the paid CL < incurred CL anomaly does not apply to this year.

### Paid vs. Incurred Ultimate Reasonability

Four accident years show selected ultimate below current incurred losses — AY 2001 ($3,054,160 selected vs. $3,163,774 incurred), AY 2002 ($2,216,837 vs. $2,327,734), AY 2006 ($1,509,390 vs. $1,517,637), and AY 2012 ($1,290,267 vs. $1,363,753). These are flagged as a FAIL in Tech Review.xlsx and documented in REPORT.md Section 11. The reviewer agrees these should be resolved before booking.

For AY 2001 and 2002, the case redundancy implied ($109K and $111K respectively) is meaningful relative to the selected IBNR ($12K and $17K). The paid development at age 275–287 months is minimal, suggesting these claims are effectively closed — making the case reserve balance unexplained. This is most consistent with redundant case reserves on a small number of open claims.

For AY 2012, the gap is $73K (selected $1.29M vs. incurred $1.36M). The Incurred CL ultimate is $1,463,664, substantially higher than both Paid CL ($1,290,267) and Paid BF ($1,311,347). The incurred actual is between these, suggesting case reserves have been partially released but not yet matched by paid. The BF ($1,311,347) may be a more defensible selection here, as it avoids the paid CL < incurred actual result.

### Recent Year Loss Ratio / Loss Rate Stability

Implied loss rates (selected ultimate ÷ payroll exposure) by maturity band:

| Band | Loss Rate (avg) | Notes |
|---|---|---|
| AYs 2001–2005 | 0.64% | Includes AY 2007 large-loss year slightly; ex-large-loss band avg ~0.55% |
| AYs 2010–2014 | 0.35% | Lower, possible shift in WC frequency |
| AYs 2020–2024 | 0.32% | BF-selected; may be dampened by a priori rates |

The 2020–2024 BF-selected loss rates (0.25–0.38%) are in a similar range to the 2010–2014 experience (0.33–0.37%) after removing large-loss years, which is plausible. However, AY 2019 at 0.68% using BF is a notable spike vs. its neighbors. This may reflect the fallback a priori ELR for AY 2019 anchoring to a high observed diagonal, rather than a true trend. Consider whether the AY 2019 BF a priori is reasonable or whether the three-year rolling average is distorted by AY 2018's elevated development.

The two large-loss years (2007 at 1.39%, 2015 at 0.85%) are significantly above all other years. The fact that AY 2007 is fully developed ($4.94M selected at age 215 months) gives high confidence in that ultimate. AY 2015 is at 88% developed with $443K IBNR remaining — this selection ($3.56M BF) is below the Paid CL ultimate ($3.81M), which may be appropriate given uncertainty but represents a conservative stance on a year that may still have development to emerge.

### ASOP Compliance

**ASOP 23 (Data Quality):** Reasonable for scope. The analyst notes the data was not reconciled to financial records ("accepted as provided"). This is appropriate to disclose but limits confidence in the accuracy of the triangles. The AY 2007 and AY 2015 large-loss spikes are identified but not confirmed against claims data. Consideration: request confirmation from the data provider that AY 2007's $3.15M spike at age 95 is attributable to a specific claim event and is not a data error before booking.

**ASOP 25 (Credibility):** The BF a priori rates are derived from a fallback approximation (3-year rolling average of diagonal loss per payroll). This is disclosed, but the source and reasonableness of the complement are not independently validated. For a first analysis without an ELR file, this is acceptable, but the BF results for AYs 2019–2024 depend heavily on this approximation. The analyst correctly flags this in Section 11.

One concern: the BF method is applied to paid losses using CDFs derived from the same paid triangle. This means the paid BF complement (a priori expected) and the CDF weight are from the same data source, reducing the independence that BF is intended to provide. An alternative complement — such as an industry benchmark or the incurred BF — would increase independence.

**ASOP 36 (Statements of Actuarial Opinion):** This document is not a Statement of Actuarial Opinion. No compliance issues under ASOP 36 at this stage.

**ASOP 41 (Actuarial Communications):** Several gaps require resolution before this becomes a final communication:

1. The REPORT.md header shows "Valuation Date: [To be confirmed from data]" — this placeholder was never filled in. The body correctly infers "approximately 12/31/2024" but the header remains blank.
2. Section 5.5 (Assumption Rationale) contains unfilled placeholder text: "[Fill in source if BF/IE methods were used, otherwise note 'Not applicable - CL only']." The BF method WAS used; this section should be completed.
3. The method description in Section 4.2 ("Paid CL for years ≥95 months developed") is inconsistent with the actual selections for AYs 2015–2018, which show BF values. Either the description or the values need to be reconciled.

**ASOP 43 (Unpaid Claim Estimates):** The analysis selects a single method per accident year without presenting an alternative scenario or range of reasonable estimates for the most uncertain years (2023–2024). While a formal range is not required, the $3.2M divergence between the two AI selectors for just two AYs represents a significant model risk that warrants explicit quantification in Section 8.2. The current Section 8.2 references a potential $4.3M upside if CL were applied uniformly for immature years — this is a useful benchmark and should be connected to the specific AY 2023–2024 scenario.

### Diagnostic Consistency

**Method label inconsistency — the most material diagnostic issue.** Cross-referencing the rules-based selection JSON values against the projected ultimates in `projected-ultimates.parquet`, the following accident years appear to have been selected from Paid BF (not Paid CL) despite being labeled "Paid CL" in the JSON:

| AY | Paid CL | Paid BF | Selected | Label |
|---|---|---|---|---|
| 2005 | $2,301,731 | $2,286,473 | $2,286,473 | "Paid CL" |
| 2006 | $1,502,796 | $1,509,390 | $1,509,390 | "Paid CL" |
| 2010 | $1,358,857 | $1,345,441 | $1,345,441 | "Paid CL" |
| 2011 | $2,029,627 | $1,996,763 | $1,996,763 | "Paid CL" |
| 2014 | $1,555,869 | $1,520,811 | $1,520,811 | "Paid CL" |
| 2015 | $3,807,442 | $3,558,608 | $3,558,608 | "Paid CL" |
| 2016 | $3,013,413 | $2,929,527 | $2,929,527 | "Paid CL" |
| 2017 | $1,494,051 | $1,708,556 | $1,708,556 | "Paid CL" |
| 2018 | $3,079,956 | $2,887,729 | $2,887,729 | "Paid CL" |

The aggregate impact: BF values for these 9 years sum to $19,855,329, while CL values sum to $20,184,746 — a difference of $329,417 in total, which is not material to the aggregate reserve, but the label discrepancy is a reproducibility issue. Anyone following REPLICATE.md and extracting "Paid CL" selections would retrieve the wrong values. Confirm which method was actually intended for each of these years and update both the JSON labels and the REPORT.md narrative accordingly.

**LDF selector divergence at 11–23 month interval for Incurred Loss:** The rules-based selector chose 1.6456 while the open-ended selector chose 2.5200 — a 53% divergence on the earliest and most leveraged interval. This interval drives AY 2024 incurred development materially. Since the ultimate selection uses Paid BF (not Incurred CL) for AY 2024, this divergence does not flow into the selected ultimate, but it is a signal that the incurred triangle at early ages has significant parameter uncertainty. Document this in Section 11 or Section 8.2.

**AY 2007 large-loss exclusion:** The $3.15M paid spike at age 95 is identified but not excluded from LDF averages in adjacent development intervals. For intervals 83–95 and 95–107, this observation drives a significantly elevated paid LDF that would not be representative of normal WC development. The analyst may want to confirm the LDF selection workbook excludes AY 2007 from the high/low exclusion or volume-weighted average at those intervals, and document the decision explicitly.

### Documentation Quality

**REPORT.md:** Generally strong narrative with appropriate caveats. The Reviewer Quick-Start (Section 0) is particularly useful. Items requiring attention before finalization:

- Section 1 header: "Valuation Date: [To be confirmed from data]" — fill in "12/31/2024 (inferred from triangle structure)"
- Section 5.5: Replace the bracketed placeholder with "BF a priori rates derived from 3-year rolling average of diagonal loss per payroll exposure — not independently benchmarked; see Section 11 for limitations"
- Section 4.2: Reconcile the description of maturity-based method selection with the actual methods applied (see Diagnostic Consistency section above)

**REPLICATE.md:** Solid reproducibility document. The Notes section at the end remains blank ("Add any additional context...") — at minimum, note the method label issue so that a future replicator understands which JSON values to trust. The mapping of AY → method (CL vs. BF) should be listed explicitly, given the current inconsistency.

### Technical Review Diagnostics

The technical review run produced 1 FAIL and multiple WARNs, but the most significant finding is structural: because the review script ran against `Analysis.xlsx` (the values-only export) rather than `complete-analysis.xlsx` (the full output with diagnostic and CL triangle sheets), 11 of 17 check groups were marked WARN/skipped. Specifically, the following checks were not performed:

- Paid-to-Incurred ratio diagnostics (Group 12)
- Case reserve reasonableness (Group 13)
- Closure rate checks (Group 14 — closed count not available, so this skip is valid)
- Severity / frequency trend checks (Group 15)
- Development factor validation (Group 11)
- X-to-Ult triangle integrity (Group 7)
- Average IBNR/Unpaid reasonableness (Group 8)

The analyst's REPORT.md Section 7 states "Frequency / severity trends — consistent with historical patterns" as checked, but the technical review system did not actually run this check. This should be corrected in REPORT.md Section 7 to note that the automated trend check was not executed, and the statement should be supported by manual review of the diagnostics exhibits.

The one FAIL (negative IBNR in AYs 2001, 2002, 2006, 2012) is well-documented and appropriately flagged. The Loss extreme outlier WARN (AY 2007 at >10× median ultimate) is expected given the known large-loss year. The Count extreme outlier WARN (1 period >10× median at 346) likely reflects AY 2001 (700 claims) against the median of approximately 340 — plausible for an old, closed year but should be confirmed.

---

## Proposed Alternatives

### §1 — Resolve method label inconsistency (AYs 2005, 2006, 2010, 2011, 2014–2018)

The reviewer would ask the analyst to explicitly document, for each of the nine affected accident years, whether the intent was to use Paid CL or Paid BF, then update the JSON labels and REPORT.md accordingly. No change to the numerical selections is proposed. If BF was the intent for all nine years (values match BF in each case), then the REPORT.md should be updated to read: "Paid CL for AYs 2001, 2003, 2004, 2007–2009, 2012–2013; Paid BF for AYs 2005–2006, 2010–2011, 2014–2024."

**Impact on aggregate reserve:** Changing all nine AYs from BF values to CL values would increase aggregate Loss ultimate by $329,417 ($20,184,746 CL vs. $19,855,329 BF for those nine years). This is not material to the total selected ultimate of $48.3M.

### §2 — AYs 2023 and 2024: Consider presenting a CL scenario alongside the BF selection

The reviewer would not override the BF selection — it is a reasonable choice for years at 34% and 13% development, where the paid CL CDF is 2.96× and 7.76× respectively. However, the $3.2M difference between BF and CL for just these two years represents 68% of total selected IBNR ($4.7M). The reviewer would propose adding a scenario table to REPORT.md Section 8 showing:

| AY | BF (selected) | CL (alternative) | Difference |
|---|---|---|---|
| 2023 | $1,846,681 | $3,546,476 | +$1,699,795 |
| 2024 | $1,224,415 | $2,755,833 | +$1,531,418 |
| **Total** | **$3,071,096** | **$6,302,309** | **+$3,231,213** |

This quantifies the upside risk if development accelerates beyond the BF a priori expectation, satisfying ASOP 43 uncertainty disclosure requirements.

### §3 — Paid tail factor: consider whether 1.0039 is appropriate for WC

The open-ended tail selector and rules-based selector agree on 1.0039 for paid loss (Bondy method), noting that exponential methods were rejected due to poor R² (0.19). For Workers Compensation, paid tails are typically non-trivial — 1.0% to 5.0% is a common range depending on injury type and jurisdiction. A tail of 0.39% at age 143 months is at the low end.

| Measure | RB Selected | OE Selected | Common WC range |
|---|---|---|---|
| Paid Loss tail | 1.0039 | 1.0039 | 1.005–1.030+ |
| Incurred Loss tail | 1.0119 | 1.0251 | 1.005–1.015 |

The reviewer would suggest sensitivity-testing a paid tail of 1.010 (consistent with the incurred tail selected by the open-ended selector) to quantify the reserve impact. A 1.0% tail applied to the paid ultimate base of ~$44M suggests a potential upside of approximately $0.6M if the true paid tail is closer to 1.0% than 0.4%.

### §4 — AY 2012: consider Paid BF over Paid CL

The analyst selected Paid CL ($1,290,267) for AY 2012, producing a FAIL (ultimate < incurred actual of $1,363,753). The Paid BF for AY 2012 is $1,311,347 — still below incurred actual but by a smaller margin ($52K vs. $74K). The Incurred CL for this year is $1,463,664, suggesting the incurred case reserves have not yet fully run off. The reviewer would consider Paid BF ($1,311,347) as an alternative, noting it is more conservative than Paid CL while remaining below current incurred — which still requires explanation of the implied case redundancy.

---

*This peer review is advisory only. All selections remain as originally determined by the analyst. The reviewer recommends the analyst respond to items §1, §2, and the Technical Review scope gap before this analysis is used for booking purposes.*
