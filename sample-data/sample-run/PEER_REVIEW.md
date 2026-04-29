# Peer Review — Workers Compensation / Sample Run

**Analysis folder:** C:\Users\super\Documents\actuarial\cas-rfp\spec-only\team-analyst\sample-data\sample-run  
**Review date:** 2026-04-29  
**Status:** Advisory — no selections were modified

**Files reviewed:**
- Analysis.xlsx (values-only workbook)
- Tech Review.xlsx
- REPORT.md
- REPLICATE.md

---

## Summary

The analysis is well-structured and covers the full chain ladder / BF / IE workflow for a Workers Compensation book (AY 2001–2024). The documentation in REPORT.md is substantive and the analyst has pre-identified the key judgment calls in Section 11. The most material concern is the tail factor relationship: the paid tail (1.0039) is lower than the incurred tail (1.0103), which is analytically unusual for long-tail WC and inconsistent with the open-ended AI selector's independent view (1.0841 exponential). A second concern is the uniform selection of Incurred CL across all 24 accident years, including AY 2023 and AY 2024 where BF indications diverge by 32–39%; most practitioners would weight BF more heavily for immature years. These two issues drive the "Proposed Alternatives" section and should be the primary focus of reviewer dialogue before the report moves to a final draft.

---

## High-Priority Findings

1. **Paid tail factor (1.0039) is lower than incurred tail factor (1.0103) — analytically inconsistent with WC behavior.** For Workers Compensation, paid loss carries more remaining cash-flow uncertainty than incurred loss, so the paid tail should materially exceed the incurred tail. The open-ended AI selector independently selected 1.0841 for paid (exponential, cutoff age 143). The difference adds approximately $340K–$1.6M to paid reserve depending on which method is used. See [Cross-Method Consistency](#cross-method-consistency).

2. **Paid CL ultimate falls below the current incurred diagonal for AYs 2001, 2002, 2006, and 2012.** A paid CL ultimate below the incurred diagonal implies the paid method projects that outstanding case reserves will never be fully paid — a mathematical inconsistency. AY 2012 is the most extreme (Paid CL $1.265M vs. incurred diagonal $1.364M; P/I ratio 0.876). See [Paid vs Incurred Reasonability](#paid-vs-incurred-reasonability).

3. **Incurred CL selected for AYs 2023 and 2024 where BF is 32–39% lower.** At 23 and 11 months of development (CDF 1.874 and 2.837), the CL method leverages very early case data with a multiplier of nearly 3×. The BF indications ($2.108M and $1.536M) are materially more conservative than the CL selections ($3.095M and $2.526M). ASOP 43 guidance and standard practice suggest BF should be heavily weighted or primary at this immaturity. See [Recent Year Stability](#recent-year-stability).

4. **Section 5.2 ELR table is blank.** The fallback ELR values are material to understanding BF/IE credibility and are required for ASOP 41 and 43 completeness. See [ASOP Compliance](#asop-compliance).

5. **REPLICATE.md contains unfilled placeholders.** Step 2 input files and Step 5 script status are still template text. Another actuary could not fully reproduce the analysis from this document in its current state. See [Documentation Quality](#documentation-quality).

---

## Detailed Findings

### Cross-Method Consistency

**Paid CDF vs. Incurred CDF — systematic inversion at mature ages.**

For all 18 accident years at ages 83–287 months (AY 2001–2018), the incurred CDF exceeds the paid CDF:

| AY | Age | Incurred CDF | Paid CDF | Expected (Paid ≥ Inc) |
|---|---|---|---|---|
| 2001 | 287 | 1.0103 | 1.0039 | FAIL |
| 2006 | 227 | 1.0489 | 1.0268 | FAIL |
| 2012 | 155 | 1.0818 | 1.0591 | FAIL |
| 2018 | 83 | 1.1861 | 1.1675 | FAIL |
| 2019 | 71 | 1.2302 | 1.2410 | OK |
| 2024 | 11 | 2.8373 | 6.3561 | OK |

The relationship correctly reverses for AY 2019–2024 (ages 11–71 months), where paid CDFs substantially exceed incurred. The persistent inversion at mature ages (83+ months) may reflect case reserve releases on older closed claims holding down the incurred development pattern, while paid is nearly done developing. The root cause is worth investigating: if incurred still has material open reserves at 83–287 months, it may indicate case adequacy issues rather than development pattern noise. If the incurred LDF pattern is being driven up by a subset of large open claims, the mature-year incurred CDFs could be overstated.

**Tail factor relationship.**

For WC, paid loss development is expected to run longer than incurred because: (a) cash payments continue after case reserve closure, and (b) incurred losses benefit from case reserve reductions. The current selections — incurred tail 1.0103, paid tail 1.0039 — are inverted relative to this expectation. The open-ended AI selector reached an independent conclusion of 1.0841 for paid (exponential method, cutoff age 143), compared to the rules-based selection of 1.0039 (Bondy, cutoff age 203). The R² for the exponential fit was negative (poorly fit), which is the primary reason the rules-based framework favored Bondy on immateriality grounds. However, the analyst's own uncertainty note in Section 11 is well-placed: "exponential alternatives ranged widely (1.0–1.084)." You may want to consider whether "immateriality" is the right threshold here if the alternative tail adds ~$340K–$1.6M to paid reserve.

**BF vs. CL consistency at mature ages.**

For AYs 2001–2018, incurred BF tracks incurred CL closely (within ±7%), indicating the ELR seed does not introduce material bias at these ages. For AYs 2017 and 2009, incurred BF is 12% and 6.5% above incurred CL respectively — worth noting as mild high-side bias at those ages, possibly reflecting the smoothed ELR over-estimating prior loss rates for below-average years.

**AY 2020 and AY 2021: Paid CL exceeds Incurred CL.**

At ages 59 and 47 months, paid CL ultimates ($1.342M and $1.439M) exceed incurred CL ultimates ($1.273M and $1.382M) by 5.4% and 4.1%. This reversed relationship (paid > incurred at mid-maturity) is consistent with case reserve reductions on these AYs — likely COVID-era claims settling faster than development patterns suggested. The phenomenon is worth a brief note in REPORT.md Section 6.1 to confirm it reflects an observable pattern rather than a data anomaly.

---

### Paid vs Incurred Reasonability

**Four accident years where Paid CL ultimate < Incurred diagonal:**

| AY | Age | Incurred diagonal | Paid CL ultimate | Difference | Case reserves |
|---|---|---|---|---|---|
| 2001 | 287 | 3,163,774 | 3,054,160 | −109,614 | 121,479 |
| 2002 | 275 | 2,327,734 | 2,216,837 | −110,897 | 128,088 |
| 2006 | 227 | 1,517,637 | 1,501,289 | −16,348 | 55,496 |
| 2012 | 155 | 1,363,753 | 1,264,876 | −98,877 | 169,517 |

When paid CL ultimate falls below the incurred diagonal, the paid method is implying those case reserves will result in net negative future cash flows — which is generally not possible unless the insurer expects large recoveries (salvage/subrogation). For AYs 2001 and 2002 the shortfall is moderate (~$110K each) and these AYs are nearly fully developed, so the practical impact is small. AY 2012 at P/I ratio of 0.876 and $169K in open case reserves is more concerning. This likely reflects a specific large case reserve that the paid development pattern cannot "see" in the LDFs. You may want to consider whether AY 2012 warrants a large-case investigation, or whether a slight upward adjustment to the paid-CL ultimate (to at least cover the incurred diagonal) would be appropriate. The Incurred CL selection ($1.475M) avoids this problem and is the better anchored pick for that year.

---

### Recent Year Stability

**Implied loss rates by accident year:**

| AY | Age | Loss rate | Severity | % IBNR in selected |
|---|---|---|---|---|
| 2019 | 71 | 0.0071 | 8,942 | 18.7% |
| 2020 | 59 | 0.0028 | 3,432 | 23.1% |
| 2021 | 47 | 0.0029 | 4,189 | 26.8% |
| 2022 | 35 | 0.0027 | 4,360 | 36.4% |
| 2023 | 23 | 0.0063 | 10,148 | 46.6% |
| 2024 | 11 | 0.0051 | 8,702 | 64.8% |

AY 2020–2022 show notably lower loss rates (0.0027–0.0028) than the portfolio median (~0.005). This may reflect COVID-era claim suppression or improved safety experience; it also means the smoothed-diagonal ELRs for these years likely underestimate true ultimate, which should bleed through into BF indications being higher than CL — consistent with what we observe for AY 2020 (BF $1.405M vs. CL $1.273M).

**AY 2023 and AY 2024: CL selection is aggressive given immaturity.**

AY 2023 (23 months, CDF 1.874): Incurred CL $3.095M vs. Incurred BF $2.108M — a $987K gap (31.9% divergence). The selected Incurred CL is 47% higher than BF and is entirely dependent on a very early case reserve development signal being extrapolated by a factor of nearly 2×. The analyst's reasoning cites "observable case activity," but at 23 months a large case reserve on a single claim could inflate the diagonal and distort the CL indication.

AY 2024 (11 months, CDF 2.837): Incurred CL $2.526M vs. Incurred BF $1.536M — a $990K gap (39% divergence). A CDF of 2.837 means the selected ultimate is based on multiplying 11-month incurred losses by nearly 3×. The IE indication ($998K) rounds out the picture: three methods produce $998K, $1.536M, and $2.526M. Selecting the highest of three very dispersed methods at maximum immaturity without a documented positive outlier reason (e.g., a known specific large claim in AY 2024) is a choice that warrants escalation to the reviewing actuary.

**AY 2015 loss rate (0.0091, severity $11,400) is an unremarked outlier.**

The analyst correctly identifies AY 2007 as a large-loss year. AY 2015 is not specifically flagged in Section 11, yet its severity ($11,400) is the highest in the portfolio other than AY 2007 ($10,592), and its loss rate (0.0091) is materially above surrounding years (AY 2014: 0.0038, AY 2016: 0.0068). You may want to consider adding AY 2015 alongside AY 2007 in the large-loss commentary in Section 6.1 and Section 11.

---

### ASOP Compliance

**ASOP 23 — Data Quality.** Section 3 addresses the major requirements adequately: data source is identified, key limitation (no closed count, no ELR file, no reconciliation to financials) is acknowledged, and the AY 2007 anomaly is noted. The one gap: Section 3.2 states "data accepted as provided" with no reconciliation — this is compliant with ASOP 23 (disclosure is made) but the report should note that data quality reliance is on the provider (Triangle Examples 1.xlsx), which in a client engagement context would need to name a specific responsible party.

**ASOP 25 — Credibility.** The BF/CL blending approach is described at a high level in Section 4.2 but the basis for the blend is not explicit. The report says "immature years blend CL with fallback ELR" without stating what the weights are, how they vary by AY, or on what basis maturity thresholds (2001-2015 = CL, 2016-2024 = BF) were set. You may want to consider adding a brief table in Section 4.2 or 5.5 showing the actual BF credibility weight by AY (which can be derived from the BF formula: % unreported = 1 − 1/CDF). That column is available in the Incurred BF sheet.

**ASOP 41 — Communications.** Three gaps warrant attention before this moves to a final draft:

- Section 5.2 ELR table is blank. The fallback ELR values by accident year (derived from the smoothed diagonal) are a material assumption driving BF and IE ultimates and must be disclosed.
- The intended user description in Section 1.3 is generic ("internal reserving team"). If this report could be relied upon by management, external auditors, or regulators, the scope of reliance should be more specific.
- The report is correctly labeled "Draft — not a final communication," so ASOP 41 obligations are not yet triggered, but the ELR table and credibility weights should be populated before the draft goes out for formal review.

**ASOP 43 — Unpaid Claim Estimates.** The framework broadly meets ASOP 43 requirements. Specific areas to tighten:

- The measurement definition in Section 1.2 does not state whether the estimate represents a mean, central, or modal estimate. ASOP 43 §3.6 requires this to be identified.
- Section 8.1 (Sensitivity) is marked "not implemented." While a full sensitivity study is not required, at minimum a tabular sensitivity for the two highest-uncertainty items (AY 2023/2024 CL vs. BF, and paid tail 1.0039 vs. 1.084) would strengthen the uncertainty discussion and partially satisfy ASOP 43 §3.7.
- The aggregate reasonableness check (Section 7) is solid on loss ratios and IBNR/case ratio, but there is no check comparing total ultimate to a benchmark loss rate or comparison to industry data. Section 7 notes "Comparison to independent benchmark — not performed," which is acceptable to document as a known limitation.

**ASOP 36 — Statement of Actuarial Opinion.** This analysis is a draft, not an SAO, so ASOP 36 does not formally apply. No findings here.

---

### Diagnostic Consistency

The Tech Review passes all structural checks cleanly. The two FAILs ("null Selected Ultimates" in Loss Selection and Count Selection) are confirmed false positives affecting only the blank separator/Total rows, as documented in the REPORT. The WARN items are appropriately addressed in Section 7.

The Summary Diagnostics sheet was also reviewed independently:

- **Loss rate trend:** No clear upward or downward trend through the portfolio, though AY 2007 and AY 2015 are clear outliers. AYs 2020–2022 are depressed (COVID cohort). AY 2023's implied loss rate of 0.0063 at only 23 months of development may inflate when fully matured.
- **Severity trend:** The portfolio runs from ~$1,800 (AY 2004) to ~$11,400 (AY 2015) with no smooth trend — volatile year-to-year. The tech review WARN on severity spikes (46%, 103%, 231% at periods 3/4/6) refers to development-period spikes in the incremental triangle, not calendar-year spikes. The analyst's explanation (expected WC maturation pattern) appears reasonable.
- **Frequency trend:** Declining from ~2.2/million exposure (AY 2001) toward ~0.6/million (AY 2024). This long-run decline is consistent with WC industry experience and is not flagged as an anomaly, but the driver (portfolio growth, safety improvements, exposure changes) is not discussed. For a complete report you may want to consider a one-sentence acknowledgment.

---

### Documentation Quality

**REPORT.md.** The report is substantively populated and materially compliant with the template structure. Three specific gaps before a final draft:

1. Section 5.2 (ELR table) is entirely blank — the smoothed fallback ELRs by AY must be shown.
2. Section 4.2 does not state explicit BF credibility weights; these are derivable and should be included.
3. The intended measure is not stated (mean? central estimate? See ASOP 43 comment above).

**REPLICATE.md.** The document retains several template placeholders that have not been populated:
- Step 2: "Input files used: [List each file in raw-data/ with description]" — not filled in despite raw-data/Triangle Examples 1.xlsx being present.
- Step 5 (Method Ultimates): IE and BF script status lines still read "[Ran / Skipped - reason]."
- Manual selections sections use the boilerplate "[If user made manual selections, list them here]" without confirming whether any overrides occurred.

Another actuary following this document to reproduce the analysis would encounter ambiguity at these steps. You may want to consider filling these in before the analysis is closed.

**Peer Review Log (Section 13).** The table is blank, as expected for a first-pass review. After the analyst responds to this review, findings should be logged there with responses and resolution status.

---

### Technical Review Diagnostics

The automated tech review (Tech Review.xlsx) was examined. Key observations:

- **Two FAILs** flagged: null Selected Ultimates in both Loss Selection and Count Selection (1 null each). These are false positives affecting only the Total/separator row — confirmed by manual inspection of the Loss Selection and Count Selection sheets. No accident year rows have null selections. No action required, but you may want to consider adding a note in the tech review script to suppress this false positive.
- **Severity spike WARNs** (46%, 103%, 231% at periods 3, 4, 6): These refer to development-period incremental severity spikes, not accident-year spikes. The analyst's attribution to normal WC maturation patterns is plausible, but the high spike at period 6 (231%) is worth confirming against the raw triangle data.
- **Multiple tech review groups (6, 7, 8, 10, 11, 12, 13, 14) show WARNs** stating "Not in values file — see complete-analysis.xlsx." These appear to be by-design limitations of the values-only workbook reviewed here. The peer reviewer notes this means certain checks (CL triangle integrity, development factor checks, paid-to-incurred, case reserve, closure rate) were not performed against the values file. If the `Complete Analysis.xlsx` exists, consider running the tech review against that file to pick up all check groups.

---

## Proposed Alternatives

### 1. Paid Tail Factor: 1.0039 (Bondy) → Consider 1.040–1.084 (Exponential)

| | Current | Alt Low | Alt High |
|---|---|---|---|
| Paid tail factor | 1.0039 (Bondy) | 1.040 (midpoint) | 1.0841 (open-ended AI, exponential) |
| Paid reserve impact (approx.) | — | +$340K | +$1.6M |
| Incurred tail for comparison | 1.0103 | — | — |

**Rationale:** For Workers Compensation, the paid tail factor should exceed the incurred tail factor because incurred development peaks earlier (case reserves are set, then released) while paid development continues through final claim closure. A paid tail of 1.0039 below the incurred tail of 1.0103 is inconsistent with this expectation. The open-ended selector independently reached 1.0841 using an exponential fit from cutoff age 143. The rules-based selector chose Bondy at cutoff age 203 on "immateriality" grounds (0.07% of CDF), but that materiality judgment is relative — $340K–$1.6M on a $7.6M IBNR book is not trivial. You may want to consider testing the exponential method at age 203 (not just 143) to find a middle ground that respects the decay pattern without over-extrapolating from the earlier, noisier window.

### 2. AY 2023 Selection: Incurred CL ($3.095M) → Consider Incurred BF ($2.108M) or 50/50 Blend ($2.601M)

| | Current | BF primary | 50/50 blend |
|---|---|---|---|
| AY 2023 selected ultimate | 3,095,495 | 2,108,001 | 2,601,748 |
| AY 2023 IBNR | 1,443,738 | 351,244 | 949,991 |
| Change vs. current | — | −987,494 | −493,747 |

**Rationale:** At 23 months (53.4% developed, CDF 1.874), CL leverage is high. Industry practice and ASOP 43 guidance generally weight BF heavily for AYs below 50% developed. The analyst's reasoning — "observable case activity, high case reserve establishment" — is valid but should be weighed against the risk that a single large open case is distorting the diagonal. If the elevated incurred diagonal at AY 2023 reflects a known specific large claim, the CL selection is supportable; if not, BF is the more defensible primary method.

### 3. AY 2024 Selection: Incurred CL ($2.526M) → Consider Incurred BF ($1.536M) or IE/BF Average ($1.267M)

| | Current | BF | IE/BF average |
|---|---|---|---|
| AY 2024 selected ultimate | 2,525,664 | 1,536,280 | 1,267,035 |
| AY 2024 IBNR | 1,635,509 | 645,970 | 376,880 |
| Change vs. current | — | −989,384 | −1,258,629 |

**Rationale:** At 11 months (35.2% developed, CDF 2.837), the CL method multiplies a very immature diagonal by nearly 3×. All three less-leveraged methods (IE, BF, Paid CL $2.258M) cluster below $2.3M; the Incurred CL is an outlier. Unless there is a specific large claim in AY 2024 known to be escalating (which would support the Incurred CL), the BF indication is materially more stable and appropriate. You may want to consider escalating this selection to the Chief Actuary / Committee given the magnitude of difference.

### 4. AY 2012: Verify Paid CL vs. Case Reserve Relationship

AY 2012 Paid CL ultimate ($1.265M) is $99K below the incurred diagonal ($1.364M), implying the $170K case reserve will not be fully paid. You may want to consider reviewing the claim activity on AY 2012 to confirm whether the open reserve is on a legitimate large case or a data artifact. If a large case exists, the Incurred CL selection ($1.475M) is well-supported. If the case reserve is stale, a paid-CL anchored selection may be more appropriate.

---

*This peer review is advisory only. No selections were modified. All findings are proposed for analyst consideration; the analyst retains final judgment over all selections and disclosures.*
