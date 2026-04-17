# Peer Review — Commercial Auto Liability (All AYs, 2015–2024)

**Analysis file:** output/complete-analysis.xlsx  
**Review date:** 2026-04-17  
**Status:** Advisory — no selections were modified

---

## Summary

The analysis employs a well-structured chain-ladder / BF / initial-expected (IE) weighted blend with sensible maturity-based credibility shifts, and the LDF selections are internally consistent and well-reasoned for most accident years. Two significant concerns warrant attention before the work is finalized: (1) the Initial Expected (a priori) loss ratios used in the BF method are not sourced or documented anywhere in the workbook, and for several accident years they diverge dramatically from emerging experience, and (2) AY 2021 displays a cluster of anomalous diagnostic signals — extremely elevated early case reserves, an atypical closure-rate trajectory, and an incurred ultimate selection that *exceeds* the paid ultimate selection — that together suggest the incurred development for that year may be over-leveraged. Prior-period comparisons are entirely absent, limiting independent assessment of reserve movement.

---

## High-Priority Findings

1. **IE/a priori source undocumented; IE/CL divergences extreme for several AYs** — The BF method anchors on an Initial Expected that appears to follow a smooth ~0.9%/year trend of ~$14,158/exposure-unit in 2015 to ~$15,402 in 2024, but no source (pricing, prior study, benchmark) is disclosed. For AY 2015 (age 120), IE = $63.9M vs. CL = $45.6M (IE is 1.40× CL on a 10-year-old accident year). For AY 2017 (age 96), IE = $59.5M vs. CL = $37.8M (1.58×). For AY 2021 (age 48), IE = $46.2M vs. CL = $77.7M (0.60×). For AY 2024 (age 12), IE = $36.6M vs. CL = $64.9M (0.57×). An undocumented a priori that diverges this widely from observed development calls into question the reliability of the BF complement at every age, and fails the ASOP 25 documentation standard for credibility complements.

2. **AY 2021 anomalous pattern — incurred selection exceeds paid** — Several diagnostics for AY 2021 are outliers versus all other accident years: average case reserve at age 12 = $39,109 (versus $4,062–$14,835 for all other years, a 3–9× premium); claim closure rate at age 12 = 0.953 (highest in the dataset, vs. 0.763–0.891 for all other years); and the closure rate *declines* through age 48 (0.953 → 0.885), the only accident year showing this monotonically decreasing pattern. The incurred CL of $77.7M at 48 months is extrapolating a factor-chain through case-reserve-heavy incurred data that has been releasing reserves rather than developing upward. The result is that the incurred selected ($72.0M) *exceeds* the paid selected ($69.3M) — a reversal of the normal ordering for a long-tail line. For every other accident year, paid selected > incurred selected. The incurred method may be over-leveraged for 2021, and the analyst may want to consider shifting weight further toward BF or paid for this year.

3. **No prior-period selections present** — The "Prior Selection" and "Prior Reasoning" columns are blank for all accident years on every selection sheet. Under ASOP 41 and 43, material changes in methods or assumptions from prior analyses must be identified and their effect discussed. Without prior selections it is impossible to determine whether this is an initial analysis, and any reserve movement since the last evaluation cannot be evaluated.

---

## Detailed Findings

### Cross-Method Consistency

**LDF ordering (paid > incurred) — satisfied throughout.** Across all nine development intervals, the selected paid LDF exceeds the selected incurred LDF, which is the expected relationship. The paid tail (1.019) also exceeds the incurred tail (1.0125). No violations found here.

**BF vs. CL relationship — generally appropriate.** For early maturities (ages 12–48) where CL is highly leveraged, the BF generally acts as a moderating influence, and the CL-to-BF weights shift appropriately from 50/45 at mid-maturity to 20/75 at age 12. This is methodologically sound.

**AY 2021 incurred/paid reversal — flagged.** As noted in High-Priority Finding #2, AY 2021 is the sole accident year where the incurred selection ($72.0M) exceeds the paid selection ($69.3M) by $2.7M (3.9%). For long-tail casualty, the paid ultimate should meet or exceed the incurred ultimate because paid development must still "catch up" to all incurred losses including those in case reserves. The analyst may want to consider whether the 50% CL weight applied to incurred AY 2021 at 48 months — where CDF is ~1.41 and case reserve patterns are anomalous — is appropriate, or whether the paid selection of $69.3M provides a more reliable ceiling. AY 2024 at 12 months also shows incurred ($47.5M) slightly exceeding paid ($46.8M) by 1.5%, which is immaterial but consistent with the same directional concern at the early maturity.

---

### Paid vs. Incurred Reasonability

The paid-to-incurred diagonal ratios follow a plausible and internally consistent pattern for most accident years, rising from ~0.79–0.87 at age 12 toward ~0.96–1.00 at age 120. No year shows a materially aberrant trajectory in isolation — except AY 2021, which has a lower paid-to-incurred ratio at each observed age (0.841 at 12, 0.811 at 24, 0.823 at 36, 0.836 at 48) than comparable accident years at the same ages. The consistently lower ratio reflects a book where incurred is running high relative to paid — consistent with the elevated initial case reserves — and means the incurred CL projects a larger ultimate than paid CL ($77.7M vs. $76.1M), both substantially above the selected values.

The analyst may want to consider that for AY 2021 specifically, the paid triangle ($46.2M actual at 48 months, CL = $76.1M, BF = $64.3M, selected = $69.3M) reflects a more "arms-length" view of development uncontaminated by case-reserving practices that appear to have been unusual at early ages.

---

### Recent Year Stability

**Implied ultimate loss rates show high volatility with a rising trend.** The diagnostic sheet reports ultimate loss rates (selected ultimate / exposure) as follows:

| AY | Loss Rate/Exp | Frequency | Severity |
|----|--------------|-----------|---------|
| 2015 | $10,315 | 1.111 | $9,288 |
| 2016 | $13,961 | 1.129 | $12,368 |
| 2017 | $9,492 | 1.201 | $7,906 |
| 2018 | $16,346 | 1.338 | $12,221 |
| 2019 | $13,419 | 1.385 | $9,686 |
| 2020 | $13,671 | 1.515 | $9,026 |
| 2021 | $23,323 | 1.616 | $14,430 |
| 2022 | $13,616 | 1.421 | $9,584 |
| 2023 | $15,361 | 1.469 | $10,455 |
| 2024 | $19,966 | 1.649 | $12,109 |

Several observations worth considering:

Frequency trends upward persistently from 1.11 in 2015 to 1.65 in 2024 (a ~49% increase over the period). This is a large cumulative shift. The analysis does not appear to include a standalone discussion of whether the ultimate frequency assumptions for recent AYs have been calibrated against this trend. Under ASOP 13, a significant change in loss frequency should be evaluated for whether it represents a permanent shift rather than being extrapolated mechanically via development factors.

Severity is highly volatile with no clear monotone trend: the range spans $7,906 (2017) to $14,430 (2021), a ratio of 1.83:1. AY 2017 is particularly low ($7,906) and AY 2021 particularly high ($14,430) relative to neighbors. This volatility, combined with the lack of a stable severity trend, raises the question of whether the a priori loss ratios — which follow a smooth low-growth curve — adequately capture the environment for recent AYs. The implied IE severity ($14,158–$15,402/exposure, essentially flat) appears calibrated to neither the AY 2017 low-loss environment nor the AY 2021 high-loss environment. Under ASOP 25, the complement of credibility should "share risk characteristics with" the subject experience; a flat trend assumption may not satisfy this when frequency has increased by nearly half over the period.

AY 2024 at 12 months shows an unusually high reported count (1,712 — the highest of any 12-month period in the triangle) coupled with a lower-than-average closure rate (0.763). This combination means AY 2024 is developing more open claims than prior years. The analyst may want to consider whether this represents an emerging frequency acceleration that warrants additional weight on count-based development for the most recent year.

---

### ASOP Compliance

**ASOP No. 23 — Data Quality**

The analysis contains at least one data anomaly that should be disclosed. AY 2015 at age 120 shows a closed count of 4,931 exceeding the reported count of 4,930, resulting in a computed open-count of −1 and a closure rate of 1.0002. Closed claims cannot exceed reported claims without an error in the data (likely a re-opened claim that was closed without being re-counted as reported, or a coding discrepancy). Per ASOP 23, known defects in data must be disclosed; this should be noted in any actuarial communication.

More broadly, the workbook contains no documented reconciliation of the triangle data to an external source (accounting, carrier report, etc.), no record of minimum/maximum/negative-value scans, and no notation of when the data was received or from whom. The source and as-of date of each data element should be stated.

**ASOP No. 25 — Credibility Procedures**

The BF complement (IE/Initial Expected) uses an a priori series that follows a smooth geometric trend in loss-per-exposure (approximately 0.94%/year). The source of this expected series is not documented anywhere in the workbook. ASOP 25 requires disclosure of the complement of credibility and the rationale for selecting it. A reviewer cannot determine whether this is derived from pricing, a prior actuarial study, an industry benchmark, or internal management estimates. For years where the IE diverges greatly from both CL and BF (e.g., AY 2017 where IE is 57% above CL), the undocumented a priori drives the BF materially; that influence should be explained.

**ASOP No. 36 — Statements of Actuarial Opinion**

The workbook does not contain formal SAO language and may not be intended to support one at this stage. However, if it does support or will support an actuarial opinion, the analyst should note: (a) the large divergence between IE and CL for several AYs creates a wide implied range of reasonable estimates (e.g., for AY 2024 incurred, CL = $64.9M vs. BF = $43.6M — a $21M spread before any weighting); (b) the AY 2021 anomalous pattern represents identifiable risk of adverse development; and (c) without prior comparisons, any RMAD discussion would be incomplete.

**ASOP No. 41 — Actuarial Communications**

The workbook does not identify the actuary's name, the intended users, the information date, or the date of the communication. No scope section is present describing what is included or excluded (e.g., whether LAE is included, whether the analysis is gross or net of reinsurance, what the claim definition is). There is no uncertainty discussion or range of reasonable estimates. An actuarial report accompanying this workbook should address these items. If the workbook is itself the only deliverable, these disclosures should be added as a cover sheet or notes tab.

**ASOP No. 43 — Property/Casualty Unpaid Claim Estimates**

The analysis uses three methods (CL, IE, BF) and applies credibility-weighted blends sensibly graduated by maturity, which is methodologically appropriate under ASOP 43. However, there is no aggregate reasonableness check exhibited (e.g., comparison of total IBNR to premium, surplus, or prior reserve, or a frequency/severity cross-check against the Diagnostics sheet). The Diagnostics sheet shows total selected ultimate ≈ $515.9M on $390.5M actual incurred, implying ~$125.4M of IBNR. This should be evaluated in aggregate context. Also, there is no discussion of subsequent events between the data date and any delivery date, which ASOP 43 requires.

---

### Diagnostic Consistency

**LDF selections are well-reasoned and internally consistent with the CV/slope diagnostics.** The analyst's reasoning narratives document the rationale for each selection — referencing CV bands, 3yr vs. 5yr weighted averages, incurred-vs.-paid LDF comparisons, and paid-to-incurred diagnostics — in thorough detail. For most intervals, the selections are defensible within the ranges shown.

**One inconsistency worth examining:** The incurred 12–24 interval shows a 3-year slope of −0.042 (recent factors declining), while the paid 12–24 interval shows a 3-year slope of +0.025 (recent factors rising). The analyst correctly selects the 3-year weighted for both (incurred 1.8066, paid 1.8151) with matching reasoning. However, the divergence in direction — incurred development per dollar of incurred loss is falling while paid development per dollar of paid loss is rising — suggests that case reserving practices at early ages may be changing. If recent case reserves at 12 months are being set more conservatively (driving a lower incurred LDF but more paid still to come), this would be internally consistent. The analyst may want to add a brief note confirming this interpretation rather than leaving the directional divergence without commentary.

**Reported count CL vs. selection for mature AYs.** For AY 2015 and 2016 at ages 120 and 108, the CL of reported counts equals the actual count (no further development projected by the factor chain), yet the selections (5,011 and 5,012) exceed both CL and actual counts by ~80 and ~70 additional claims respectively. This occurs because the weighting formula allocates 25% to BF and 5% to IE, and IE (6,554 and 6,321) is far above actual count even at these mature ages. For accident years that are essentially fully developed on a count basis, the analyst may want to consider whether applying BF/IE weight is appropriate or whether CL alone (or CL plus a modest tail factor) is the better selection. The additional ~80 claims baked into 2015's selected count translate directly into implied unreported/IBNR claims at a mature age.

---

## Proposed Alternatives

**AY 2021 Incurred — Reduce CL weight, increase BF weight**

The analyst's selection applies "CL 50% + IE 5% + BF 45%" at age 48, yielding $72.0M. Given the anomalous early case reserve pattern and the incurred-exceeds-paid reversal, consider whether the mid-development CL should receive as much as 50% weight when the case reserve trajectory for this year has been so unusual.

| Alternative | Weights | Selected Incurred |
|------------|---------|-----------------|
| **Current** | CL 50% + IE 5% + BF 45% | **$72.0M** |
| Alt A (BF-heavy) | CL 30% + IE 5% + BF 65% | **$70.2M** |
| Alt B (paid-limited) | $69.3M (capped at paid selection) | **$69.3M** |

*Rationale:* Alt A reduces the CL anchor from 50% to 30%, consistent with the heightened uncertainty about the incurred development pattern for this year. The ~$1.8M reduction is relatively modest on a $72M ultimate. Alt B treats the paid selection as a ceiling, which is the theoretically correct ordering for a long-tail line; the paid CL and BF are arguably more reliable at age 48 for a year with unusual case-reserving history.

**AY 2015 and 2016 Reported Count — Consider CL-only for mature AYs**

At ages 108–120, applying BF with an IE of 6,321–6,554 to a fully-developed CL of 4,930–4,943 pushes the selected count above both actual and projected development. Consider a CL-only (or near-CL) selection:

| AY | Current Sel | CL | Alt (CL-only) |
|----|------------|-----|--------------|
| 2015 (age 120) | 5,011 | 4,930 | 4,930 |
| 2016 (age 108) | 5,012 | 4,943 | 4,943–4,950 |

The impact on ultimate losses depends on the assumed severity per additional claim; however, aligning count selections to CL for mature years would improve internal consistency between the count-based and loss-based ultimates.

---

*All findings above are advisory. No selections in the workbook were modified. The analyst should evaluate each observation in light of data or context not visible in the workbook, and document any decisions taken in response to this review.*
