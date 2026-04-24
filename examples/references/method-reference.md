# Actuarial Reserving Method Reference

## Key Concepts

### Loss Development Triangle
A matrix showing cumulative loss amounts (or claim counts) by accident period (rows)
and development age (columns). Older accident periods have more columns filled in because
more time has elapsed. The upper-right portion is empty — those are the values we're
trying to estimate.

### Age-to-Age Factor (ATA / LDF)
The ratio of a value at one development age to the value at the prior age:
```
LDF(12→24) = Value@24 / Value@12
```
An LDF > 1 means claims grew between those ages. These ratios form a "development pattern"
that we can apply to immature accident periods.

### Cumulative Development Factor (CDF)
The product of all remaining LDFs from a given age to ultimate:
```
CDF@age = LDF(age→next) × LDF(next→next2) × ... × tail
```
CDF represents the total remaining development. CDF = 1.0 means fully developed.

### % Developed
```
% developed = 1 / CDF
```
How far along an accident period is toward its ultimate value. Used in BF method
as the credibility weight.

### Tail Factor
Development beyond the last observed age. Usually close to 1.000 for mature triangles.

---

## Methods

### Chain Ladder (CL)
**Idea:** Project ultimates by applying selected LDFs to the latest observed values.

```
Ultimate = Latest Actual × CDF
IBNR     = Ultimate - Latest Actual
```

**Strengths:** Relies entirely on the data's own development pattern. Good for stable,
mature lines of business.

**Weaknesses:** High leverage for immature periods — a single early observation gets
multiplied by a large CDF. Sensitive to anomalies in recent data.

### Initial Expected (IE)
**Idea:** Estimate ultimate losses using prior expectations, independent of the
triangle's own development.

```
IE Ultimate (Losses) = ELR × Exposure
IE Ultimate (Counts) = Expected Frequency × Exposure
```

Where ELR and Expected Frequency come from pricing, industry data, or judgment.

**Strengths:** Not affected by random fluctuations in early development.
Provides an independent benchmark.

**Weaknesses:** Only as good as the ELR assumption. Doesn't respond to actual experience.

### Bornhuetter-Ferguson (BF)
**Idea:** Blend CL and IE using % developed as the credibility weight.

```
BF Ultimate = Actual + (1 - % developed) × IE Ultimate
```

- For mature periods (high % developed), BF ≈ CL
- For immature periods (low % developed), BF ≈ IE

**Strengths:** Balances responsiveness to data with stability from prior expectations.
The most commonly used method for immature accident years.

**Weaknesses:** Still depends on the IE assumption for immature years.

---

## Method Comparison

| Aspect | CL | IE | BF |
|--------|----|----|-----|
| Data reliance | 100% actual | 0% actual | Blended |
| Prior expectation | None | Full | Partial |
| Immature years | High leverage | Stable | Balanced |
| Mature years | Reliable | May over/under-state | ≈ CL |
| Common use | Primary for mature | Benchmark/floor | Primary for immature |

---

## Selection Guidance

The agent should consider these factors when selecting final ultimates:

1. **% Developed**: Higher = more confidence in CL; lower = more weight to BF/IE
2. **CL convergence**: If Incurred CL ≈ Paid CL, both methods agree and CL is reliable
3. **IE reasonableness**: Does the ELR × Exposure result make sense given the data?
4. **BF smoothness**: BF tends to produce smoother patterns across accident years
5. **Trend consistency**: Ultimate severity, loss rate, frequency should trend sensibly