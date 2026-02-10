---
name: bornhuetter-ferguson-method
description: Guide for applying the Bornhuetter-Ferguson method for actuarial loss reserving. Use this when asked to calculate ultimate losses using the BF method, blend expected loss ratios with actual loss experience, estimate IBNR using a priori expectations, or when chain ladder alone may be unreliable due to immature data or changing patterns.
---

# Bornhuetter-Ferguson Method

The Bornhuetter-Ferguson (BF) method blends actual loss experience with an a priori expected loss estimate. Particularly useful for immature accident years or when historical development patterns may not be fully credible.

**Core Principle:** Combines Chain Ladder method (actual experience) with Expected Loss Ratio method (external expectations).

## Quick Reference

**Two Algebraically Equivalent Formulas:**

**Formula 1 (Direct):**
```
BF Ultimate = Reported Loss + (Expected Loss × % Unreported)
BF Ultimate = L + (ELR × Exposure × (1 - w))
```

**Formula 2 (Chain Ladder Blend):**
```
BF Ultimate = (Reported Loss × LDF × % Reported) + (Expected Loss × % Unreported)
BF Ultimate = (L × LDF × w) + (ELR × Exposure × (1 - w))  
```

Where:
- `L` = Latest reported (or paid) losses
- `ELR` = Expected Loss Ratio (a priori)
- `Exposure` = Premium or exposure base
- `w` = % reported = 1 / LDF
- `1 - w` = % unreported
- `LDF` = Loss Development Factor to ultimate

**Required Inputs:**
- Loss triangle (reported or paid)
- Loss development factors (from Chain Ladder or external)
- Expected Loss Ratio (a priori estimate)
- Exposure base (earned premium, etc.)

**Python Packages:** `pandas`, `numpy`, `chainladder`

**Advantages:**
- More stable than Chain Ladder for immature years
- Less responsive to random fluctuations
- Incorporates external information (pricing, benchmarks)

**Disadvantages:**
- Requires credible expected loss ratio
- Can be too unresponsive if ELR is wrong
- ELR selection is subjective

---

## Methodology Steps

###Step 1: Data Requirements

**1. Loss Triangle (same as Chain Ladder):**
```
Accident Year | 12 mos | 24 mos | 36 mos | 48 mos | ...
2020          | 10,000 | 12,000 | 13,500 | 14,200 | ...
2021          | 11,000 | 13,200 | 14,850 |        |
```

**2. Loss Development Factors:**
From Chain Ladder analysis, prior analysis, or industry benchmarks

**3. Expected Loss Information:**

Option A - Expected Loss Ratio + Premium:
```
Accident Year | Earned Premium | Expected LR | Expected Ultimate
2020          | 50,000,000     | 65.0%       | 32,500,000
2021          | 55,000,000     | 64.5%       | 35,475,000
```

Option B - Expected Ultimate directly:
```
Accident Year | Expected Ultimate | Source/Notes
2020          | 32,500,000       | Pricing target
2021          | 35,475,000       | Pricing target
```

### Step 2: Python Implementation

**Using chainladder package (recommended):**

```python
import chainladder as cl
import pandas as pd
import numpy as np

# Load loss triangle
triangle = cl.load_sample('raa')  # or load from CSV/Excel

# Fit Chain Ladder to get LDFs
cl_model = cl.Chainladder().fit(triangle)

# Set expected loss ratios (a priori)
expected_lr = 0.65  # Example: 65% expected loss ratio

# Get exposure base (earned premium)
premium = triangle.latest_diagonal.copy()
premium[:] = np.array([50_000_000, 55_000_000, 60_000_000, ...])

# Apply Bornhuetter-Ferguson
bf_model = cl.BornhuetterFerguson(
    apriori=expected_lr,
    apriori_sigma=0.05  # Optional: uncertainty in ELR
).fit(triangle, sample_weight=premium)

# Get results
bf_ultimate = bf_model.ultimate_
bf_ibnr = bf_model.ibnr_

# Compare to Chain Ladder  
cl_ultimate = cl_model.ultimate_
comparison = pd.DataFrame({
    'Latest_Loss': triangle.latest_diagonal.values.flatten(),
    'CL_Ultimate': cl_ultimate.values.flatten(),
    'BF_Ultimate': bf_ultimate.values.flatten(),
    'BF_IBNR': bf_ibnr.values.flatten(),
    'Difference': (bf_ultimate.values - cl_ultimate.values).flatten()
})

print(comparison)
```

**Manual calculation (for transparency):**

```python
def calculate_bf_ultimate(latest_loss, ldf, expected_loss):
    """
    Calculate BF ultimate using Formula 1.
    
    Parameters:
    -----------
    latest_loss : float - Latest reported or paid loss
    ldf : float - Loss development factor to ultimate
    expected_loss : float - A priori expected ultimate loss (ELR × Premium)
    
    Returns: float - BF ultimate loss
    """
    pct_reported = 1 / ldf
    pct_unreported = 1 - pct_reported
    bf_ultimate = latest_loss + (expected_loss * pct_unreported)
    return bf_ultimate

# Example usage
latest = 12_000_000
ldf_to_ult = 1.25  # 80% reported
expected_ult = 15_000_000  # 65% LR × $23M premium

bf_ult = calculate_bf_ultimate(latest, ldf_to_ult, expected_ult)
bf_ibnr = bf_ult - latest

print(f"BF Ultimate: ${bf_ult:,.0f}")
print(f"BF IBNR: ${bf_ibnr:,.0f}")
```

### Step 3: Expected Loss Ratio Selection

**Most critical actuarial judgment in the BF method.**

**Common Sources for Expected LR:**

1. **Pricing Target LR:**
   - From rate filings or business plan
   - **Pros:** Management's best estimate, incorporates latest information
   - **Cons:** May be optimistic, assumes adequate pricing

2. **Historical Average LR:**
   - Calculate average of past accident years (3-yr, 5-yr, 10-yr)
   - Trend to current level if needed
   - **Pros:** Based on actual company experience
   - **Cons:** May not reflect recent changes

3. **Industry Benchmark LR:**
   - From ISO, NCCI, or other industry sources
   - Adjust for company-specific factors
   - **Pros:** External validation
   - **Cons:** May not reflect company's unique characteristics

4. **Blended Approach:**
   - Weight multiple sources by credibility
   - Example: 60% pricing + 40% historical
   - **Pros:** Balances different perspectives
   - **Cons:** Weighting is subjective

**Trending Historical LRs:**
```python
def trend_loss_ratio(historical_lr, years_to_trend, annual_trend):
    """Trend historical loss ratio to current level."""
    return historical_lr * (1 + annual_trend) ** years_to_trend

# Example: Trend 3-year average from mid-2021 to current (4.5 years)
historical_lr_3yr = 0.635
trended_lr = trend_loss_ratio(historical_lr_3yr, years=4.5, annual_trend=0.025)
print(f"Trended LR: {trended_lr:.1%}")  # 65.1%
```

**Documentation Required:**
- All ELR sources considered
- Trending calculations and assumptions
- Final ELR selection with rationale
- Comparison table showing different ELR scenarios
- Sensitivity analysis (test ±5%, ±10%)

### Step 4: Loss Development Factor Selection

**Options:**
1. **Current Chain Ladder Analysis** (most common)
2. **Prior Analysis LDFs** (when current data is unstable)
3. **Industry Benchmark LDFs** (when company data lacks credibility)
4. **Blended LDFs** (credibility weight multiple sources)

**Key Calculation:**
```python
ldf_to_ult = 1.25
pct_reported = 1 / ldf_to_ult  # = 0.80 or 80%
pct_unreported = 1 - pct_reported  # = 0.20 or 20%
```

### Step 5: Calculate BF Results and Compare

```python
# Create comprehensive comparison
results = pd.DataFrame({
    'Accident_Year': accident_years,
    'Latest_Loss': latest_loss,
    'LDF': ldfs,
    'Pct_Reported': 1 / ldfs,
    'Expected_Ultimate': expected_ultimate,
    'BF_Ultimate': bf_ultimate,
    'BF_IBNR': bf_ultimate - latest_loss,
    'CL_Ultimate': cl_ultimate,
    'CL_IBNR': cl_ultimate - latest_loss,
    'Difference': bf_ultimate - cl_ultimate
})

# Export
results.to_excel('output/bf_analysis_results.xlsx', index=False)
```

---

## Actuarial Selections Required

### 1. Expected Loss Ratio Selection

**Decision Points:**
- Which source(s)? (pricing, historical, industry, blend)
- Trending required? What trend rate and period?
- Credibility weighting if blending?
- How does selected ELR compare to actual emerging experience?

**Documentation:**
- ELR source comparison table
- Trending calculations
- Final selection rationale
- Sensitivity to ±5% and ±10%

### 2. Loss Development Factor Selection

**Decision Points:**
- Use current Chain Ladder LDFs?
- Use prior analysis LDFs?
- Use industry benchmark LDFs?
- Blend multiple sources?

**Documentation:**
- LDF source comparison
- Table showing LDFs and % reported by development age
- Rationale for selection

### 3. Exposure Base

**Decision Points:**
- Earned premium at current rate level?
- On-level premium (rate adjusted)?
- Policy count or other exposure measure?
- **Must align with ELR basis**

### 4. Method Weighting by Accident Year

**Decision Points:**
- How much weight to BF vs Chain Ladder for each year?
- More BF weight for immature years
- More CL weight for mature years

**Typical Pattern:**
```
Development Age | CL Weight | BF Weight
12-24 months   | 10-20%    | 80-90%
36-48 months   | 30-50%    | 50-70%
60+ months     | 70-90%    | 10-30%
Very mature    | 100%      | 0%
```

---

## Validation and Reasonability

### Key Checks

1. **Implied Loss Ratios:**
   ```python
   implied_lr = bf_ultimate / premium
   # Should be reasonable vs pricing and actual
   ```

2. **BF vs CL Comparison:**
   - Immature years: BF should differ from CL
   - Mature years: BF and CL should be close
   - Large differences for mature years suggest ELR problem

3. **Sensitivity to ELR:**
   ```python
   # Test impact of ELR changes
   for elr_adj in [-0.10, -0.05, 0, 0.05, 0.10]:
       adjusted_elr = base_elr * (1 + elr_adj)
       # Recalculate BF ultimate
       # Immature years should show high sensitivity
   ```

4. **IBNR Patterns:**
   - IBNR as % of reported should decrease with maturity
   - Should follow logical pattern by accident year

5. **Prior Analysis Comparison:**
   - How do results compare to last analysis?
   - Can changes be explained?

### Red Flags

- BF and CL dramatically different for mature years (check ELR)
- BF shows no response to actual experience (too much ELR weight)
- Mature years highly sensitive to ELR (check LDFs)
- Implied loss ratios unreasonable vs pricing/actual
- Results drastically different from prior without explanation
- Unable to explain BF vs CL differences

### Questions to Ask

1. Do the BF results make business sense?
2. Can we explain differences from Chain Ladder?
3. Can we explain differences from prior analysis?
4. Are implied loss ratios reasonable?
5. Is the method appropriate for each accident year?
6. Are we confident in the expected loss ratio?
7. What's the range of reasonable outcomes?
8. Should BF be primary method or complement to CL?

---

## When to Use BF vs Chain Ladder

### Use Bornhuetter-Ferguson When:

- **Immature accident years** with limited development
- **Volatile experience** with large fluctuations
- **Operational changes** that invalidate historical patterns
- **Small volume** with limited credible data
- **External information available** (strong pricing data)
- As **complement to CL** for method weighting

### Use Chain Ladder When:

- **Mature experience** with sufficient history
- **Stable patterns** and consistent development
- **High credibility** from large volume
- **No external data** or credible expected LRs
- Want method **responsive to emerging experience**

### Typical Method Weighting

```
Accident Year | Dev Age | CL Weight | BF Weight | Reasoning
2018          | 120 mo  | 100%      | 0%        | Fully mature
2020          | 96 mo   | 80%       | 20%       | Mature
2022          | 72 mo   | 60%       | 40%       | Moderately mature
2023          | 60 mo   | 50%       | 50%       | Equal weight
2024          | 48 mo   | 30%       | 70%       | Immature
2025          | 36 mo   | 20%       | 80%       | Very immature
2026          | 24 mo   | 10%       | 90%       | Extremely immature
```

---

## Integration with Overall Study

The BF method is typically one of several estimates:

1. **Run Chain Ladder** → CL ultimate
2. **Run Bornhuetter-Ferguson** → BF ultimate
3. **Compare methods** → Understand differences
4. **Weight by maturity** → More BF for immature years
5. **Document selections** → Method weights and rationale
6. **Create final estimate** → Blended ultimate

**Combining Methods:**

```python
def create_blended_ultimate(cl_ultimate, bf_ultimate, cl_weight):
    """Weight CL and BF methods to create final estimate."""
    return cl_ultimate * cl_weight + bf_ultimate * (1 - cl_weight)

# Example by accident year
results['CL_Weight'] = [1.0, 0.9, 0.8, 0.6, 0.4, 0.2, 0.1]
results['BF_Weight'] = 1 - results['CL_Weight']
results['Selected_Ultimate'] = (
    results['CL_Ultimate'] * results['CL_Weight'] +
    results['BF_Ultimate'] * results['BF_Weight']
)
```

---

## Progress Tracking Template

Copy into PROGRESS.md when working BF method:

```markdown
#### Bornhuetter-Ferguson Method
**Status:** [Not Started / In Progress / Completed]
**Started:** [Date]

##### Data Preparation
- [ ] Obtained loss triangle
- [ ] Obtained/calculated LDFs
- [ ] Gathered exposure data
- [ ] Identified ELR sources
- [ ] Validated data alignment

**Data Sources:**
- Loss triangle: [source]
- LDFs: [Chain Ladder / Prior / Industry / Blend]
- Exposure: [source]
- Expected LR: [Pricing / Historical / Industry / Blend]

##### Expected Loss Ratio Analysis
- [ ] Compiled pricing ELRs
- [ ] Calculated historical LRs (3-yr, 5-yr)
- [ ] Obtained industry benchmarks
- [ ] Trended historical to current level
- [ ] Created ELR comparison table

**ELR Options:**
| Source          | Value | Trended | Notes |
|----------------|-------|---------|-------|
| Pricing        | 65.0% | N/A     | Rate filing |
| Historical 5yr | 63.5% | 66.0%   | +2.5 pts trend |
| Industry       | 67.0% | N/A     | ISO benchmark |

##### LDF Selection
- [ ] Reviewed current CL LDFs
- [ ] Compared to prior analysis
- [ ] Compared to industry (if available)
- [ ] Selected LDF source
- [ ] Documented rationale

**Selected LDFs:**
| Dev Age | LDF   | % Reported | % Unreported |
|---------|-------|-----------|--------------|
| 12      | 1.292 | 77.4%     | 22.6%        |
| 24      | 1.110 | 90.1%     | 9.9%         |
| 36      | 1.051 | 95.1%     | 4.9%         |
| 48      | 1.023 | 97.8%     | 2.2%         |

##### BF Calculation & Scenarios
- [ ] Calculated BF with pricing ELR
- [ ] Calculated BF with historical ELR
- [ ] Calculated BF with industry ELR
- [ ] Compared BF to Chain Ladder
- [ ] Generated scenario comparison

**Results Summary:**
| Scenario    | Total Ultimate | vs CL     |
|------------|---------------|-----------|
| CL         | $XX.X M       | Base      |
| BF-Pricing | $XX.X M       | +$X.X M   |
| BF-Hist    | $XX.X M       | +$X.X M   |

##### ELR Selection & Discussion
- [ ] Developed ELR recommendation
- [ ] Documented rationale
- [ ] Prepared alternatives
- [ ] Discussed with actuary
- [ ] Finalized selection

**Recommended ELR:** [value]%
**Rationale:** [explanation]

##### Final BF Calculation
- [ ] Calculated BF with final selections
- [ ] Generated results by accident year
- [ ] Compared to CL
- [ ] Created exhibits
- [ ] Documented validation checks

##### Validation & Reasonability
- [ ] Calculated implied loss ratios
- [ ] BF vs CL comparison by maturity
- [ ] ELR sensitivity (±5%, ±10%)
- [ ] IBNR pattern analysis
- [ ] Prior analysis comparison
- [ ] Red flag review

##### Method Weighting Recommendation
- [ ] Proposed CL/BF weights by year
- [ ] Calculated blended ultimate
- [ ] Documented weighting rationale

**Proposed Weights:**
| AY   | Dev Age | CL Wt | BF Wt | Blended Ult |
|------|---------|-------|-------|-------------|
| 2024 | 48 mo   | 30%   | 70%   | $XX.X M     |
| 2025 | 36 mo   | 20%   | 80%   | $XX.X M     |
| 2026 | 24 mo   | 10%   | 90%   | $XX.X M     |

**Files Created:**
- `/analysis/bf_analysis.xlsx`
- `/analysis/bf_elr_comparison.xlsx`
- `/analysis/bf_vs_cl.png`
- `/selections/bf_selections.md`
```

---

## Common Pitfalls and Solutions

### Pitfall 1: Wrong Expected LR
**Problem:** Using outdated or inappropriate ELR  
**Solution:** Compare multiple ELR sources, validate against emerging actual

### Pitfall 2: Inconsistent Basis
**Problem:** ELR doesn't match exposure base  
**Solution:** Ensure ELR and exposure are on same basis

### Pitfall 3: Using BF for Mature Years
**Problem:** BF can distort mature year estimates if ELR is wrong  
**Solution:** Use method weighting - more CL weight for mature years

### Pitfall 4: No Sensitivity Analysis
**Problem:** Single point estimate without understanding uncertainty  
**Solution:** Always test ±5% and ±10% ELR scenarios

### Pitfall 5: Ignoring Actual Experience
**Problem:** BF can be unresponsive to emerging trends  
**Solution:** Monitor actual vs expected, adjust ELR if patterns change

---

## Key Formulas Reference

**BF Ultimate (Formula 1 - Direct):**
```
BF Ultimate = Latest Loss + (Expected Ultimate × % Unreported)
BF Ultimate = L + (E × (1 - w))
```

**BF Ultimate (Formula 2 - CL Blend):**
```
BF Ultimate = (Latest Loss × LDF × % Reported) + (Expected Ultimate × % Unreported)
BF Ultimate = (L × LDF × w) + (E × (1 - w))
```

**Percent Reported (w):**
```
w = 1 / LDF
```

**Percent Unreported (1 - w):**
```
1 - w = 1 - (1 / LDF) = (LDF - 1) / LDF
```

**Expected Ultimate:**
```
Expected Ultimate = Expected Loss Ratio × Earned Premium
E = ELR × P
```

**IBNR:**
```
IBNR = BF Ultimate - Latest Loss
```

**Implied Loss Ratio:**
```
Implied LR = BF Ultimate / Earned Premium
```

---

## References

- Bornhuetter, R.L., and Ferguson, R.E. "The Actuary and IBNR." Proceedings of the Casualty Actuarial Society, 1972.
- Friedland, Jacqueline. "Estimating Unpaid Claims Using Basic Techniques." Casualty Actuarial Society, 2010.
- Wikipedia: Bornhuetter-Ferguson method - https://en.wikipedia.org/wiki/Bornhuetter–Ferguson_method
- `chainladder` Python package documentation - https://chainladder-python.readthedocs.io/
