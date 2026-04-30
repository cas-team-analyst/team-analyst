# Peer Review — Workers Compensation (Sample Run)

**Analysis folder:** `sample-run/`
**Files reviewed:**
- `Analysis.xlsx` (values-only workbook, 15 sheets)
- `Tech Review.xlsx`
- `REPORT.md`
- `REPLICATE.md`

**Review date:** 2026-04-30
**Status:** Advisory — no selections were modified

---

## Summary

This is a well-structured initial analysis of a Workers Compensation triangle (AY 2001–2024) using Chain Ladder, BF, and Initial Expected methods. Documentation is substantially complete for a working draft, and the analyst has done commendable work flagging known judgment calls in Section 11. The analysis is acceptable for internal review purposes, with three areas that warrant closer attention before the reserve is finalized: the CL-over-BF selection for AY 2022, the choice of Paid BF over Incurred BF for AYs 2023–2024, and the unvalidated ELR fallback that underpins all BF estimates. Several documentation inconsistencies also need correction.

---

## High-Priority Findings

| # | AY(s) | Finding | Section |
|---|---|---|---|
| H1 | 2022 | CL selected at 62% development — BF typically preferred here | Cross-Method Consistency |
| H2 | 2023–2024 | Paid BF chosen over Incurred BF with 20–33% spread; conservative framing not a sufficient ASOP 43 justification | Cross-Method Consistency |
| H3 | 2020–2024 | ELR fallback drives all BF estimates; no validation against underwriting — largest source of parameter risk | ASOP Compliance (ASOP 25) |
| H4 | 2007 | Large-loss year carried at selected ultimate with no separate large-loss analysis; potential for significant adverse development | Paid vs. Incurred Reasonability |
| H5 | All | Tech Review run on values-only workbook — 11 of 16 WARNs are structural/expected; important check groups skipped entirely | Technical Review Diagnostics |

---

## Detailed Findings

### Cross-Method Consistency

**Paid vs. Incurred CL spread — generally acceptable, two years worth flagging.**

For most accident years (2003–2022), Incurred CL and Paid CL ultimates are within ±5%, which is expected for a maturing WC book. Two exceptions warrant attention:

- **AY 2012 (155 months): 12.2% spread.** Incurred CL = $1,402,971; Paid CL = $1,250,085. At this maturity, the $169,516 case reserve outstanding (Incurred – Paid diagonal) is elevated for a WC year that should be approaching finality. The analyst's note of "minor data timing" may be accurate, but consider whether case reserves are being held conservatively on late-developing claims. If paid development accelerates in the next diagonal, the Incurred CL selection would look over-stated. You may want to verify whether any open claims remain in this year and whether the case reserve is appropriately set.

- **AY 2023 (23 months): 11.6% spread; AY 2024 (11 months): 30.9%.** Both are expected given extreme immaturity — not a concern, just noted for completeness.

**AY 2022: CL selected at 62% development — unusual choice.**

At 35 months (62% developed), the analyst selects Incurred CL ($1,332,512) over Incurred BF ($1,190,947) or Paid BF ($1,183,961). The selection reasoning argues that CL "credibility is higher at 62% development" because "CL and BF are close." This framing is circular — closeness of CL and BF in other years does not establish CL credibility for this year. Actuarial practice and ASOP 43 generally prefer BF for years below 70% developed because the a priori assumption dampens the leveraged CDF. The CDF at 35 months is 1.61 (implying 38% of losses are yet to emerge) — more than enough tail to introduce meaningful estimation error in CL alone.

Proposed alternative: select Incurred BF ($1,190,947), reducing the AY 2022 ultimate by approximately $141,565 (–10.6%). See Proposed Alternatives section.

**AY 2023–2024: Paid BF over Incurred BF — rationale needs strengthening.**

The analyst selects Paid BF for AYs 2023 and 2024, citing "conservative positioning." The spread is material:

| AY | Incurred BF | Paid BF | Spread |
|---|---|---|---|
| 2023 | $2,128,807 | $1,771,456 | $357,351 (20%) |
| 2024 | $1,577,300 | $1,190,793 | $386,507 (32%) |

ASOP 43 does not endorse "conservatism" as a standalone selection criterion — the standard requires methods to produce a "reasonable" estimate, not a deliberately low one. At these maturities (23 and 11 months), incurred data is richer: case reserves are set by claims adjusters with direct knowledge of open claims, and incurred development patterns are typically more stable than paid patterns at early ages. The argument that paid BF is preferable because paid CDFs are lower than incurred CDFs at 23 months is somewhat expected and does not by itself make Paid BF the better estimator.

You may want to consider whether Incurred BF is a better anchor for these two years, with Paid BF retained as a reasonable lower bound. A disclosed blend (e.g., 50/50 at 23 months) could also be defensible. The aggregate reserve impact of switching both years to Incurred BF would be approximately +$744K, shifting total IBNR from $3.20M to roughly $3.94M.

**BF vs. CL consistency — appropriate for most years.**

For 2001–2019, the pattern of Incurred CL as primary method for mature years is sensible. The shift to BF for 2020–2022 is directionally right. The switch back to CL for AY 2022 at 62% development is the outlier discussed above.

---

### Paid vs. Incurred Reasonability

**No paid ultimate falls below incurred losses** — the fundamental paid/incurred sanity check passes across all 24 AYs. This is a positive finding.

**AY 2007 — large-loss year carried without separate analysis.**

Paid and Incurred diagonals for AY 2007 are $4.79M and $4.81M respectively — approximately 3× peer years at comparable maturity. The Incurred CL ultimate of $4,878,544 implies only $67,769 IBNR (1.4%) at 215 months, which is consistent with high maturity. However:

- No separate identification or capping of the large loss has been performed.
- If a single large claim is still open in AY 2007 (possible at 215 months for a WC permanent disability case), further development could materially shift the ultimate.
- The analyst has appropriately flagged this for escalation to chief actuary/committee. This reviewer concurs that AY 2007 and AY 2015 (similarly elevated) warrant verification of open-claim status before the reserve is finalized.

**AY 2001 and AY 2002 — elevated loss rates.**

The implied loss rate (loss per dollar of payroll) for AY 2001 is approximately 1.00% — roughly 2–3× most other years in the 2003–2022 range. AY 2002 is 0.72%, also elevated. These are the most mature years and fully settled, so the observation is informational rather than actionable. It may reflect a different book composition in early accident years, or simply higher industry WC loss rates in 2001–2002. No restatement is needed, but a brief note in the report acknowledging this pattern (rather than readers inferring it from the loss rate column) would improve transparency.

---

### Recent Year Loss Rate Stability

The implied loss rates (ultimate loss / payroll) by recent accident year are:

| AY | Age (mo) | Selected Ultimate | Loss Rate | Method |
|---|---|---|---|---|
| 2017 | 95 | $1,303,581 | 0.30% | Incurred CL |
| 2018 | 83 | $2,595,631 | 0.59% | Incurred CL |
| 2019 | 71 | $3,093,231 | 0.68% | Incurred CL |
| 2020 | 59 | $1,414,067 | 0.31% | Paid BF |
| 2021 | 47 | $1,394,937 | 0.30% | Incurred BF |
| 2022 | 35 | $1,332,512 | 0.28% | Incurred CL |
| 2023 | 23 | $1,771,456 | 0.36% | Paid BF |
| 2024 | 11 | $1,190,793 | 0.24% | Paid BF |

Two patterns worth noting:

1. **AY 2019 stands out at 0.68% vs. the 0.28–0.59% range of neighboring years.** At 71 months with a CDF of 1.19 (84% developed), the CL ultimate is being leveraged. It is possible that AY 2019 is a legitimately adverse year — but the magnitude of the jump from AY 2018 (0.59%) and subsequent drop to AY 2020 (0.31%) suggests that the Incurred CL for 2019 may be over-leveraging a period of elevated diagonal development. The BF indication ($2,960,229) is materially lower by 5.3%. You may want to consider whether BF deserves more weight for AY 2019 given this pattern.

2. **The AY 2019–2020 drop from 0.68% to 0.31%** is dramatic and likely partly attributable to COVID-19 effects on payroll and claim activity in 2020. The report does not mention this possible explanation. Adding a brief comment under Section 8.2 or Section 3.3 noting that 2020–2022 loss rates may reflect pandemic-era claim suppression would help a reviewer understand the pattern.

---

### ASOP Compliance

**ASOP 23 (Data Quality):** Disclosed appropriately. Data is accepted as-is from Triangle Examples 1.xlsx with no financial reconciliation; this limitation is clearly stated. The formula-derived payroll exposure (2001 × 1.02^n) is documented. One item: the report does not describe what reasonableness checks were performed on the raw triangle values themselves (e.g., verification of non-negative diagonals, sign checks, monotonicity). For an internal analysis this is acceptable, but a sentence in Section 3.2 confirming basic data integrity checks were performed (even implicitly by the data validation step) would strengthen ASOP 23 compliance.

**ASOP 25 (Credibility):** The BF ELR is labeled a "fallback approximation" — a 3-year rolling average of empirical incurred loss per dollar of payroll. This is disclosed, which is commendable. However, ASOP 25 requires the complement of credibility (the a priori) to be "related to" the subject experience and for the selection basis to be documented. The report acknowledges the fallback lacks forward-looking pricing grounding and flags it in Section 11. The reviewer would additionally suggest: (a) confirming the 3-year window is appropriate (rather than 5-year or all-year), and (b) adding a brief statement in Section 5.5 describing why this specific window was used. No underwriting ELRs are available, so the fallback is the only practical option; the documentation should say so explicitly.

**ASOP 36 (Statements of Actuarial Opinion):** Not applicable — this is an internal working draft, not a SAO. The report appropriately states draft status and limits the intended audience.

**ASOP 41 (Communications):** The report is clearly labeled as a draft for internal peer review. Intended users are stated (Section 1.3). Methods, assumptions, and data sources are documented, albeit at a summary level. Two gaps to address before finalizing: (a) the actuary's professional qualifications are not stated (not required for a working draft, but should be added before the report becomes a final communication); (b) the information date (Section 10) notes "~November 30, 2024 (inferred)" — the approximate nature of the valuation date should be resolved or confirmed before the report is circulated as a final document.

**ASOP 43 (Unpaid Claim Estimates):** Section 8.1 (Sensitivity) is noted as "not implemented." This is acceptable for a working draft but should be addressed before finalization — even a simple sensitivity table showing reserve impact of ±5% on tail factors and ±10% on ELRs would meet the standard's uncertainty disclosure requirement. The sources of uncertainty discussion in Section 8.2 is well-written and substantive.

**ASOP 13 (Trending):** Not implemented; appropriately noted throughout the report.

---

### Diagnostic Consistency

**LDF selection framework is coherent.** The 14-criteria rules-based approach with open-ended AI cross-check is documented in REPLICATE.md and referenced in the report. The tail selection of `exp_dev_product` for all three measures is consistent with the diagnostics cited (gap compliance; Skurnick and exact-last variants produced unreasonable tails).

**Method indications by AY are internally consistent** with the maturity-based weighting described in Section 4.2. No cases were found where the selected ultimate is outside the range of all method indications for the same year, which is a basic ASOP 43 coherence check.

**AY 2013 appears low relative to peers.** Selected ultimate of $729,197 at 143 months implies a loss rate of 0.18%, the lowest in the entire series by a significant margin. This could reflect a genuinely benign year, a low-claim AY, or an averaging artifact in LDF selection. It warrants a brief comment in the report explaining why AY 2013 is materially lower than its neighbors (AY 2012 at $1.40M, AY 2014 at $1.44M).

---

### Documentation Quality

**REPORT.md is substantially complete** for a working draft. Sections 0–11 are populated with real content rather than boilerplate. The analyst's self-flagging in Section 11 is a positive practice.

**Two documentation inconsistencies to correct:**

1. **Section 7 — Tech Review WARN description for Loss:** The report states "AY 2007 selected ultimate of ~$1.54M flagged as outlier vs. median." The actual AY 2007 selected ultimate is **$4,878,544**, not ~$1.54M. The value $1,539,016 is AY 2006's selected ultimate (which is also shown in the Tech Review detail). This appears to be a copy error — the outlier being flagged by the Tech Review is AY 2007 at $4.88M (approximately 3.2× the median of ~$1.49M), not a ~$1.54M figure. The description should be corrected to reference AY 2007's actual selected value.

2. **Section 5.2 — ELR table uses approximate ranges rather than actual values.** The table shows "~0.007–0.010" etc. ASOP 43 requires disclosure of the assumptions used. The actual per-year ELR values are available in the processed data files — either including them directly in the table or providing a clearer reference to the specific output file (and column) would better satisfy ASOP 41/43 disclosure requirements.

**REPLICATE.md is excellent.** The step-by-step replication log, the explicit notation of "No manual overrides — all selections from Rules-Based AI Selection row," and the "To replicate" instructions for each step are all good practice that would allow an independent actuary to reproduce the analysis. One small gap: the Notes section at the bottom is blank. A sentence noting that the tail JSON output files required renaming (which is already documented in Step 4) could be promoted to the Notes section for visibility.

---

### Technical Review Diagnostics

**The Tech Review was run against `Analysis.xlsx` (values only), not the complete analysis workbook.** This is the root cause of 11 of the 16 WARNs, all of which report "Not in values file — see complete-analysis.xlsx (expected)." The following check groups were skipped entirely:

- Paid-to-Incurred raw data checks (WARN: "One or both missing — skipping")
- Case reserve reasonableness checks (WARN: "Incurred Loss and/or Paid Loss missing — skipping")
- Closure rate checks (WARN: "Reported Count and/or Closed Count missing — skipping")
- Severity/frequency trend checks (WARN: "Diagnostics sheet missing — skipping")
- Development factor checks (WARN: "Not in values file")

These are among the most actuarially meaningful checks. It is recommended that `7-tech-review.py` be re-run against the complete analysis workbook (if it exists) or that `Analysis.xlsx` be supplemented with the Diagnostics and Sel- sheets before peer review is finalized. If the complete workbook was not created (the `output/` folder appears to be empty), the analyst may need to re-run `6-analysis-create-excel.py`.

**The three substantive WARNs are adequately addressed:**
- AY 2007 loss ultimate outlier — explained as large-loss year (reasonable)
- Count IBNR slight negatives in 7 mature periods — within tolerance for fully developed years (acceptable)
- Count outlier at AY 2011 (selected = 346) — the 10× median check appears to flag this AY given the small denominator in some diagnostic calculation; the analyst's explanation for the analogous count flag is reasonable

---

## Proposed Alternatives

The following are advisory alternatives where the reviewer would select differently. No changes have been applied.

### Alternative 1: AY 2022 — BF over CL

| | Incurred CL (Analyst) | Incurred BF (Proposed) | Difference |
|---|---|---|---|
| Selected Ultimate | $1,332,512 | $1,190,947 | –$141,565 (–10.6%) |
| IBNR | $505,096 | $363,531 | –$141,565 |

**Rationale:** At 35 months (62% developed), ASOP 43 and standard practice favor BF as the primary method due to the material tail still to be developed. Both Incurred BF and Paid BF agree closely ($1,190,947 and $1,183,961), which provides method support for the BF range. The current CL selection is not unreasonable, but a BF alternative would be better supported by actuarial standards.

---

### Alternative 2: AY 2023 — Incurred BF over Paid BF

| | Paid BF (Analyst) | Incurred BF (Proposed) | Difference |
|---|---|---|---|
| Selected Ultimate | $1,771,456 | $2,128,807 | +$357,351 (+20.2%) |
| IBNR | $119,699 | $477,050 | +$357,351 |

**Rationale:** At 23 months, incurred data includes current case reserves set by claims adjusters and is typically more informative than paid emergence. Selecting Paid BF as "conservative" is not an ASOP 43-supported basis for method selection. Incurred BF better reflects the actual reserve obligation at this maturity. If the analyst is concerned about case adequacy drift, a disclosed blend of Incurred BF and Paid BF (e.g., 50/50) could be an intermediate position.

---

### Alternative 3: AY 2024 — Blend of BF methods

| Method | Ultimate | Difference vs. Analyst |
|---|---|---|
| Paid BF (Analyst) | $1,190,793 | — |
| Incurred BF | $1,577,300 | +$386,507 (+32%) |
| 50/50 Blend | $1,384,047 | +$193,254 (+16%) |

**Rationale:** At 11 months (31% developed), uncertainty is extreme. The 32% spread between Incurred BF and Paid BF reflects this — neither should be treated with false precision. A disclosed 50/50 blend, with a stated uncertainty range bounded by both methods, would more transparently convey the estimation uncertainty at this maturity and better satisfy ASOP 43's uncertainty disclosure requirements.

---

### Alternative 4: AY 2007 — Separate large-loss analysis

No specific alternative ultimate is proposed here (would require claim-level data), but the reviewer recommends obtaining an open-claims listing for AY 2007 and, if any claims above a retention threshold remain open, performing a cap-and-excess analysis or at minimum a deterministic scenario for adverse development. This is consistent with the analyst's own recommendation in Section 11.

---

*This peer review is advisory only. All selections remain the analyst's responsibility. The reviewer proposes alternatives to assist in evaluating the range of reasonable estimates; they are not recommendations to override any specific selection.*
