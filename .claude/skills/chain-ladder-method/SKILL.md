---
name: chain-ladder-method
description: Guide for applying the Chain Ladder (Loss Development Method) for actuarial loss reserving. Use this when asked to calculate ultimate losses using the chain ladder method, analyze loss development triangles, calculate age-to-age factors, or project IBNR reserves using historical loss development patterns.
---

# Chain Ladder (Loss Development Method)

The Chain Ladder method is a prominent actuarial loss reserving technique that uses historical loss development patterns to project ultimate losses and estimate IBNR (Incurred But Not Reported) reserves.

**Core Principle:** Historical loss development patterns are indicative of future loss development patterns.

## Quick Reference

**Seven Steps:**
1. Compile claims data in a development triangle
2. Calculate age-to-age factors (loss development factors)
3. Calculate averages of age-to-age factors
4. Select claim development factors
5. Select tail factor
6. Calculate cumulative claim development factors
7. Project ultimate claims

**Progress Template:** See [Progress Tracking Template](#progress-tracking-template) section below to copy into PROGRESS.md

**Actuarial Selections:** See [Actuarial Selections Required](#actuarial-selections-required) section for decision points

**Required Inputs:**
- Loss triangle (accident year × valuation age)
- Can use reported losses, paid losses, or incurred losses

**Key Outputs:**
- Age-to-age factors (LDFs/link ratios)
- Selected development factors
- Cumulative development factors (CDFs)
- Ultimate loss estimates by accident year
- IBNR reserves

**Python Packages:** `pandas`, `numpy`, `chainladder`, `openpyxl`/`xlsxwriter` (Excel I/O)

**Limitations:**
- Assumes past development patterns continue unchanged
- Very responsive to changes (may be unsuitable for volatile lines)
- Sensitive to operational changes (claims staffing, settlement times)
- Relies solely on past experience (no external loss ratio information)

---

## Detailed Methodology

### Step 1: Data Requirements

#### Raw Data Formats

The Chain Ladder method requires loss data organized by accident year and development period. Data may arrive in various formats:

**Triangle format (preferred):**
```
Accident Year | 12 months | 24 months | 36 months | 48 months | ...
2020          | 10,000    | 12,000    | 13,500    | 14,200    | ...
2021          | 11,000    | 13,200    | 14,850    |           |
2022          | 12,000    | 14,400    |           |           |
```

**Transactional format:**
```
Accident Year | Valuation Date | Development Age | Cumulative Loss
2020          | 2020-12-31     | 12             | 10,000
2020          | 2021-12-31     | 24             | 12,000
2021          | 2021-12-31     | 12             | 11,000
...
```

**Policy-level format:**
```
Policy ID | Accident Date | Evaluation Date | Paid Loss | Case Reserve | Incurred Loss
P001      | 2020-01-15    | 2020-12-31     | 5,000     | 2,000        | 7,000
P001      | 2020-01-15    | 2021-12-31     | 6,500     | 1,500        | 8,000
...
```

#### Data Processing Requirements

**Transform to triangle:**
- Convert transaction-level data to cumulative triangle format
- Aggregate by accident year and development period
- Ensure consistent development age intervals (e.g., 12-month increments)
- Handle missing or incomplete data points

**Data validation checks:**
- Verify cumulative amounts increase monotonically
- Check for unusual patterns or outliers
- Confirm development ages are consistent
- Identify and document any data adjustments

**Standard processed format:**
- Rows: Accident years (oldest to newest)
- Columns: Development ages (youngest to oldest)
- Values: Cumulative losses at each evaluation point
- Export as both CSV and Excel for different use cases

---

### Step 2: Python Implementation

#### Useful Packages

```python
import pandas as pd
import numpy as np
import chainladder as cl  # Specialized actuarial package
from openpyxl import load_workbook
from dataclasses import dataclass
from typing import Dict, List, Tuple
```

**Package `chainladder`:** Specialized library for actuarial loss reserving with built-in triangle manipulation, development factor calculation, and multiple reserving methods. Install with: `pip install chainladder`

#### Code Sample: Basic Chain Ladder Implementation

```python
import pandas as pd
import numpy as np
from typing import Dict, Tuple

class ChainLadderMethod:
    """
    Implements the Chain Ladder (Loss Development) method for loss reserving.
    """
    
    def __init__(self, loss_triangle: pd.DataFrame):
        """
        Initialize with a loss triangle.
        
        Parameters:
        -----------
        loss_triangle : pd.DataFrame
            Triangle with accident years as index, development ages as columns.
            Values represent cumulative losses.
        """
        self.triangle = loss_triangle.copy()
        self.accident_years = loss_triangle.index.tolist()
        self.development_ages = loss_triangle.columns.tolist()
        
        # Results storage
        self.age_to_age_factors = None
        self.selected_ldfs = None
        self.cumulative_ldfs = None
        self.ultimate_losses = None
        self.ibnr = None
        
    def calculate_age_to_age_factors(self) -> pd.DataFrame:
        """
        Calculate age-to-age factors (loss development factors) for each accident year.
        
        Returns:
        --------
        pd.DataFrame : Age-to-age factors for each transition period
        """
        factors = pd.DataFrame(index=self.triangle.index)
        
        for i in range(len(self.development_ages) - 1):
            from_age = self.development_ages[i]
            to_age = self.development_ages[i + 1]
            col_name = f"{from_age}-{to_age}"
            
            # Calculate ratio of losses at to_age / from_age
            factors[col_name] = self.triangle[to_age] / self.triangle[from_age]
        
        self.age_to_age_factors = factors
        return factors
    
    def calculate_averages(self, method: str = 'simple', periods: int = None) -> pd.Series:
        """
        Calculate average age-to-age factors using specified method.
        
        Parameters:
        -----------
        method : str
            'simple' for simple average, 'volume' for volume-weighted average
        periods : int
            Number of most recent periods to average (None = all available)
            
        Returns:
        --------
        pd.Series : Average factors for each development period
        """
        if self.age_to_age_factors is None:
            self.calculate_age_to_age_factors()
        
        averages = {}
        
        for col in self.age_to_age_factors.columns:
            # Get non-null factors
            factors = self.age_to_age_factors[col].dropna()
            
            # Limit to most recent periods if specified
            if periods is not None:
                factors = factors.tail(periods)
            
            if method == 'simple':
                avg = factors.mean()
            elif method == 'volume':
                # Volume-weighted: need to weight by loss amounts
                # Extract from_age from column name (e.g., "12-24" -> 12)
                from_age = int(col.split('-')[0])
                
                # Get corresponding loss amounts for weighting
                weights = self.triangle[from_age].loc[factors.index]
                avg = (factors * weights).sum() / weights.sum()
            else:
                raise ValueError(f"Unknown method: {method}")
            
            averages[col] = avg
        
        return pd.Series(averages)
    
    def select_development_factors(self, 
                                   method: str = 'simple',
                                   periods: int = 5,
                                   tail_factor: float = 1.000,
                                   custom_selections: Dict = None) -> pd.Series:
        """
        Select development factors using judgment or specified method.
        
        Parameters:
        -----------
        method : str
            Averaging method ('simple', 'volume')
        periods : int
            Number of recent periods to average
        tail_factor : float
            Factor to develop from oldest age to ultimate
        custom_selections : Dict
            Optional dict to override specific LDF selections
            
        Returns:
        --------
        pd.Series : Selected age-to-age factors
        """
        # Start with calculated averages
        selected = self.calculate_averages(method=method, periods=periods)
        
        # Add tail factor
        to_ult_col = f"{self.development_ages[-1]}-Ult"
        selected[to_ult_col] = tail_factor
        
        # Apply custom overrides if provided
        if custom_selections:
            for key, value in custom_selections.items():
                selected[key] = value
        
        self.selected_ldfs = selected
        return selected
    
    def calculate_cumulative_ldfs(self) -> pd.Series:
        """
        Calculate cumulative development factors from selected age-to-age factors.
        
        Returns:
        --------
        pd.Series : Cumulative factors to ultimate for each development age
        """
        if self.selected_ldfs is None:
            raise ValueError("Must select development factors first")
        
        # Cumulative LDFs are calculated by multiplying from right to left
        factors_list = self.selected_ldfs.tolist()
        cumulative = [1.0] * (len(factors_list) + 1)
        
        # Work backwards
        for i in range(len(factors_list) - 1, -1, -1):
            cumulative[i] = cumulative[i + 1] * factors_list[i]
        
        # Map to development ages
        ages = self.development_ages + ['Ultimate']
        self.cumulative_ldfs = pd.Series(cumulative, index=ages)
        
        return self.cumulative_ldfs
    
    def project_ultimate_losses(self) -> pd.DataFrame:
        """
        Project ultimate losses for each accident year.
        
        Returns:
        --------
        pd.DataFrame : Results with latest losses, CDF to ultimate, and ultimate losses
        """
        if self.cumulative_ldfs is None:
            self.calculate_cumulative_ldfs()
        
        results = pd.DataFrame(index=self.accident_years)
        
        # Get latest non-null value for each accident year
        results['Latest_Loss'] = self.triangle.apply(lambda row: row.dropna().iloc[-1], axis=1)
        
        # Get latest development age for each accident year
        latest_ages = self.triangle.apply(lambda row: row.dropna().index[-1], axis=1)
        results['Latest_Age'] = latest_ages
        
        # Get corresponding CDF to ultimate
        results['CDF_to_Ultimate'] = latest_ages.map(self.cumulative_ldfs)
        
        # Calculate ultimate losses
        results['Ultimate_Losses'] = results['Latest_Loss'] * results['CDF_to_Ultimate']
        
        # Calculate IBNR
        results['IBNR'] = results['Ultimate_Losses'] - results['Latest_Loss']
        
        self.ultimate_losses = results
        self.ibnr = results['IBNR'].sum()
        
        return results
    
    def run_full_analysis(self, 
                         method: str = 'simple',
                         periods: int = 5,
                         tail_factor: float = 1.000) -> Dict:
        """
        Run complete chain ladder analysis.
        
        Returns:
        --------
        Dict : Dictionary containing all results and intermediate calculations
        """
        self.calculate_age_to_age_factors()
        self.select_development_factors(method=method, periods=periods, tail_factor=tail_factor)
        self.calculate_cumulative_ldfs()
        results = self.project_ultimate_losses()
        
        return {
            'age_to_age_factors': self.age_to_age_factors,
            'selected_ldfs': self.selected_ldfs,
            'cumulative_ldfs': self.cumulative_ldfs,
            'ultimate_losses': results,
            'total_ibnr': self.ibnr
        }
    
    def export_results(self, filepath: str):
        """
        Export all results to Excel file with multiple sheets.
        """
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            self.triangle.to_excel(writer, sheet_name='Loss_Triangle')
            self.age_to_age_factors.to_excel(writer, sheet_name='Age_to_Age_Factors')
            
            # Create summary sheet with selected factors and averages
            summary_df = pd.DataFrame({
                'Simple_Avg_5yr': self.calculate_averages('simple', 5),
                'Volume_Wtd_5yr': self.calculate_averages('volume', 5),
                'Simple_Avg_3yr': self.calculate_averages('simple', 3),
                'Selected': self.selected_ldfs
            })
            summary_df.to_excel(writer, sheet_name='LDF_Selection')
            
            # Cumulative factors
            self.cumulative_ldfs.to_frame('CDF_to_Ultimate').to_excel(
                writer, sheet_name='Cumulative_LDFs'
            )
            
            # Ultimate losses
            self.ultimate_losses.to_excel(writer, sheet_name='Ultimate_Losses')


# Example Usage
if __name__ == "__main__":
    # Sample loss triangle data
    data = {
        12: [37017487, 38954484, 41155776, 42394069, 44755243, 45163102, 45417309, 46360869, 46582684, 48853563],
        24: [43169009, 46045718, 49371478, 50584112, 52971643, 52497731, 52640322, 53790061, 54641339, np.nan],
        36: [45568919, 48882924, 52358476, 53704296, 56102312, 55468551, 55553673, 56786410, np.nan, np.nan],
        48: [46784558, 50219672, 53780322, 55150118, 57703851, 57015411, 56976657, np.nan, np.nan, np.nan],
        60: [47337318, 50729292, 54303086, 55895583, 58363564, 57565344, np.nan, np.nan, np.nan, np.nan],
        72: [47533264, 50926779, 54582950, 56156727, 58592712, np.nan, np.nan, np.nan, np.nan, np.nan],
        84: [47634419, 51069285, 54742188, 56299562, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        96: [47689655, 51163540, 54837929, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        108: [47724678, 51185767, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        120: [47742304, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    }
    
    accident_years = list(range(1998, 2008))
    triangle_df = pd.DataFrame(data, index=accident_years)
    
    # Initialize and run analysis
    cl_method = ChainLadderMethod(triangle_df)
    results = cl_method.run_full_analysis(method='simple', periods=5, tail_factor=1.000)
    
    # Display key results
    print("Selected Loss Development Factors:")
    print(results['selected_ldfs'])
    print("\nCumulative Development Factors:")
    print(results['cumulative_ldfs'])
    print("\nUltimate Losses by Accident Year:")
    print(results['ultimate_losses'])
    print(f"\nTotal IBNR: ${results['total_ibnr']:,.0f}")
    
    # Export to Excel
    cl_method.export_results('chain_ladder_results.xlsx')
```

#### Advanced: Using chainladder Package

```python
import chainladder as cl
import pandas as pd

# Load triangle from CSV or DataFrame
# chainladder package expects specific format
triangle_data = cl.Triangle(
    data=triangle_df,
    origin='accident_year',
    development='development_age',
    columns=['incurred_loss'],
    cumulative=True
)

# Apply chain ladder method
cl_model = cl.Chainladder()
cl_model.fit(triangle_data)

# Get results
ultimate = cl_model.ultimate_
ibnr = cl_model.ibnr_
ldfs = cl_model.ldf_

# Export results
results_df = pd.DataFrame({
    'Latest': triangle_data.latest_diagonal,
    'Ultimate': ultimate,
    'IBNR': ibnr
})

print(results_df)
```

---

### Step 3: Outputs and Selection Process

#### Primary Outputs

**1. Age-to-Age Factor Table:**
Shows the historical development patterns with multiple averaging options:
```
Development Period | Simple 5yr | Volume 5yr | Simple 3yr | Selected
12-24             | 1.168      | 1.168      | 1.164      | 1.164
24-36             | 1.058      | 1.058      | 1.056      | 1.056
36-48             | 1.027      | 1.027      | 1.027      | 1.027
...
```

**2. Cumulative Development Factors:**
```
Development Age | CDF to Ultimate
12              | 1.292
24              | 1.110
36              | 1.051
48              | 1.023
...
Ultimate        | 1.000
```

**3. Ultimate Loss Projections:**
```
Accident Year | Latest Loss | CDF | Ultimate Loss | IBNR
2020          | 47,742,304  | 1.000 | 47,742,304 | 0
2021          | 51,185,767  | 1.000 | 51,185,767 | 0
2022          | 54,837,929  | 1.001 | 54,892,767 | 54,838
...
Total         | 543,481,587 |       | 569,172,456 | 25,690,869
```

#### Creating Selection Candidates

The Chain Ladder method produces **one ultimate estimate per method variation**:

**Method Variations to Consider:**
1. **Simple average - 5 years:** Standard baseline
2. **Volume-weighted average - 5 years:** Gives more weight to larger years
3. **Simple average - 3 years:** More responsive to recent trends
4. **Volume-weighted average - 3 years:** Recent trends with volume weighting
5. **All-year average:** Maximum credibility (if stable)

**Selection Process:**

```python
def create_selection_candidates(triangle_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate multiple chain ladder estimates using different averaging methods.
    
    Returns a DataFrame with ultimate losses by accident year for each method.
    """
    candidates = {}
    
    # Method 1: Simple average - 5 years
    cl1 = ChainLadderMethod(triangle_df)
    results1 = cl1.run_full_analysis(method='simple', periods=5, tail_factor=1.000)
    candidates['CL_Simple_5yr'] = results1['ultimate_losses']['Ultimate_Losses']
    
    # Method 2: Volume-weighted - 5 years
    cl2 = ChainLadderMethod(triangle_df)
    results2 = cl2.run_full_analysis(method='volume', periods=5, tail_factor=1.000)
    candidates['CL_Volume_5yr'] = results2['ultimate_losses']['Ultimate_Losses']
    
    # Method 3: Simple average - 3 years
    cl3 = ChainLadderMethod(triangle_df)
    results3 = cl3.run_full_analysis(method='simple', periods=3, tail_factor=1.000)
    candidates['CL_Simple_3yr'] = results3['ultimate_losses']['Ultimate_Losses']
    
    # Method 4: All-year average
    cl4 = ChainLadderMethod(triangle_df)
    results4 = cl4.run_full_analysis(method='simple', periods=None, tail_factor=1.000)
    candidates['CL_All_Years'] = results4['ultimate_losses']['Ultimate_Losses']
    
    # Combine into selection table
    selection_df = pd.DataFrame(candidates)
    selection_df['Latest_Loss'] = results1['ultimate_losses']['Latest_Loss']
    
    # Reorder columns
    cols = ['Latest_Loss'] + [c for c in selection_df.columns if c != 'Latest_Loss']
    selection_df = selection_df[cols]
    
    return selection_df


# Usage
selection_candidates = create_selection_candidates(triangle_df)
print("\nChain Ladder Selection Candidates:")
print(selection_candidates)

# Export for actuary review
selection_candidates.to_excel('selections/chain_ladder_candidates.xlsx')
```

#### Documentation for Selections

Create a selection memo documenting:

1. **Data quality observations:** Any anomalies, adjustments, or data limitations
2. **LDF selection rationale:** Why specific averages were chosen for each development period
3. **Tail factor justification:** How tail factor was determined
4. **Alternative scenarios:** Other reasonable LDF selections and their impact
5. **Comparison to prior:** How current selections compare to previous analysis
6. **Reasonability checks:** Industry benchmarks, historical patterns, business context

**Template for selection documentation:**
```markdown
## Chain Ladder Method - LDF Selections

### Method Overview
Applied Chain Ladder method to reported loss triangle with development ages 12-120 months.

### Data Quality
- Data sourced from [system name]
- [Note any adjustments made]
- [Note any excluded accident years or development periods]

### LDF Selection Rationale

**12-24 months:**
- Selected: 1.164 (3-year simple average)
- Rationale: Recent experience shows decreasing development, 3-year average captures this trend
- Alternatives considered: 5-year average of 1.168 (higher, includes older outlier years)

**24-36 months:**
- Selected: 1.056 (5-year simple average)
- Rationale: Stable pattern across all years, 5-year average provides good credibility
- Alternatives: 3-year average of 1.056 (nearly identical)

[Continue for each development period...]

**Tail Factor:**
- Selected: 1.000
- Rationale: Oldest reported age shows minimal development, minimal tail expected
- Alternatives: 1.005 sensitivity scenario for conservative estimate

### Resulting Ultimate Losses
Total ultimate losses: $569,172,456
Total IBNR: $25,690,869
IBNR as % of reported: 4.7%

### Reasonability
- Implied loss ratio: [Calculate based on premium]
- Change from prior analysis: [% change]
- Industry benchmark comparison: [Within expected range / higher / lower]
```

---

## Diagnostic Displays

### Key visualizations to create:

```python
import matplotlib.pyplot as plt
import seaborn as sns

def create_diagnostic_charts(cl_method: ChainLadderMethod):
    """Generate diagnostic charts for Chain Ladder analysis."""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. Age-to-Age Factors by Development Period
    ax1 = axes[0, 0]
    cl_method.age_to_age_factors.T.plot(ax=ax1, marker='o')
    ax1.set_title('Age-to-Age Factors by Development Period')
    ax1.set_xlabel('Development Period')
    ax1.set_ylabel('Loss Development Factor')
    ax1.legend(title='Accident Year', bbox_to_anchor=(1.05, 1))
    ax1.grid(True, alpha=0.3)
    
    # 2. Cumulative Development Patterns
    ax2 = axes[0, 1]
    cumulative = cl_method.triangle.div(cl_method.triangle[12], axis=0)
    cumulative.T.plot(ax=ax2, marker='o')
    ax2.set_title('Cumulative Development to Age 12')
    ax2.set_xlabel('Development Age (Months)')
    ax2.set_ylabel('Cumulative Factor')
    ax2.legend(title='Accident Year', bbox_to_anchor=(1.05, 1))
    ax2.grid(True, alpha=0.3)
    
    # 3. IBNR by Accident Year
    ax3 = axes[1, 0]
    cl_method.ultimate_losses[['Latest_Loss', 'IBNR']].plot(
        kind='bar', stacked=True, ax=ax3
    )
    ax3.set_title('Latest Loss vs IBNR by Accident Year')
    ax3.set_xlabel('Accident Year')
    ax3.set_ylabel('Loss Amount')
    ax3.legend(['Reported', 'IBNR'])
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    # 4. Development Factor Selection Summary
    ax4 = axes[1, 1]
    summary = pd.DataFrame({
        'Simple 5yr': cl_method.calculate_averages('simple', 5),
        'Volume 5yr': cl_method.calculate_averages('volume', 5),
        'Simple 3yr': cl_method.calculate_averages('simple', 3),
        'Selected': cl_method.selected_ldfs[:-1]  # Exclude tail
    })
    summary.plot(kind='bar', ax=ax4)
    ax4.set_title('LDF Selection Comparison')
    ax4.set_xlabel('Development Period')
    ax4.set_ylabel('Loss Development Factor')
    ax4.legend()
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig('analysis/chain_ladder_diagnostics.png', dpi=300, bbox_inches='tight')
    plt.close()

# Generate diagnostics
create_diagnostic_charts(cl_method)
```

---

## Limitations and Considerations

### When Chain Ladder May Not Be Appropriate

1. **Operational changes:** Claims staffing changes, settlement time changes, case reserve practice changes
2. **Volatile lines of business:** High variability makes patterns unreliable
3. **Immature years:** Very recent accident years with minimal development
4. **External factors:** Rate changes, coverage changes, inflation shifts not captured in historical patterns

### Reasonability Checks

Before finalizing selections:
- Compare to prior period development factors
- Check if implied loss ratios are reasonable given pricing
- Compare IBNR/case ratios to expected values
- Test sensitivity to LDF selections (+/- 5%)
- Benchmark against industry development patterns if available

### Common Issues and Solutions

**Issue: Erratic age-to-age factors**
- Solution: Consider longer averaging periods or volume-weighted averages
- Alternative: Use Bornhuetter-Ferguson method which incorporates expected loss ratios

**Issue: Recent years showing different patterns**
- Solution: Give more weight to recent experience (3-year vs 5-year average)
- Alternative: Adjust older years or apply trend factors

**Issue: Missing or unreliable tail development**
- Solution: Use industry tail factors or extended development analysis
- Alternative: Judgmentally select conservative tail factor

---

## Integration with Overall Reserving Study

The Chain Ladder method typically produces one component of the overall ultimate loss estimate:

1. **Run Chain Ladder** with selected LDFs → Produces CL ultimate estimate
2. **Run Bornhuetter-Ferguson** (see bf-method skill) → Produces BF ultimate estimate  
3. **Run other methods** (Cape Cod, Expected Loss Ratio, etc.) → Additional estimates
4. **Weight methods** → Typically 40-60% Chain Ladder, with remainder on other methods
5. **Make final selections** → Judgment-based weighting considering credibility and appropriateness

Document the Chain Ladder ultimate as one candidate in the selections process, noting its strengths and limitations for the actuarial review.

---

## Progress Tracking Template

Copy this section into your main PROGRESS.md under "Step 3: Selections Process" when working the Chain Ladder method.

```markdown
#### Selection Level: Chain Ladder Method - Loss Development Factors
**Status:** [Not Started / In Progress / Completed]
**Method:** Chain Ladder (Loss Development Method)
**Started:** [Date]

##### 3A: Data Preparation
- [ ] Compiled loss triangle (reported or paid)
- [ ] Validated data quality (monotonic increases, no gaps)
- [ ] Documented data source and any adjustments
- [ ] Created triangle CSV/Excel file in /data/processed/
- [ ] Documented triangle structure in README.md

**Data Quality Issues:**
[Document any anomalies, adjustments, or exclusions]

**Files Created:**
- `/data/processed/loss_triangle_[reported/paid].csv`
- `/data/processed/triangle_validation_notes.md`

##### 3B: Calculate Development Factors
- [ ] Calculated age-to-age factors for all accident years
- [ ] Computed simple averages (all-year, 5-year, 3-year)
- [ ] Computed volume-weighted averages (all-year, 5-year, 3-year)
- [ ] Created age-to-age factor display table
- [ ] Generated diagnostic charts (factor patterns by year)

**Metrics Calculated:**
- Age-to-age factors by accident year and development period
- Simple average LDFs (all-year, 5-year, 3-year)
- Volume-weighted average LDFs (all-year, 5-year, 3-year)
- Median LDFs (for outlier detection)

**Files Created:**
- `/analysis/chain_ladder_factors.xlsx`
- `/analysis/chain_ladder_diagnostics.png`
- `/analysis/cl_calculations.py` (if using Python)

**Anomalies Identified:**
[Note any unusual patterns, outliers in specific years, or development periods]

##### 3C: LDF Selection Recommendations
- [ ] Reviewed age-to-age factors for each development period
- [ ] Identified outliers and investigated causes
- [ ] Developed initial LDF recommendations
- [ ] Documented reasoning for each development period
- [ ] Compared to prior analysis selections
- [ ] Compared to industry benchmarks (if available)

**Initial LDF Recommendations:**

| Development Period | Simple 5yr | Volume 5yr | Simple 3yr | All-Year | Recommended | Reasoning |
|-------------------|-----------|-----------|-----------|----------|-------------|----------|
| 12-24             | [e.g., 1.168] | [1.168] | [1.164] | [1.170] | [1.164] | [Recent trend lower, 3yr captures] |
| 24-36             | [1.058]   | [1.058]  | [1.056]  | [1.059]  | [1.058]    | [Stable across all periods, 5yr] |
| 36-48             | [1.027]   | [1.027]  | [1.027]  | [1.028]  | [1.027]    | [Very stable, any average appropriate] |
| 48-60             |           |          |          |          |             | |
| 60-72             |           |          |          |          |             | |
| 72-84             |           |          |          |          |             | |
| 84-96             |           |          |          |          |             | |
| 96-108            |           |          |          |          |             | |
| 108-120           |           |          |          |          |             | |
| Tail              | N/A       | N/A      | N/A      | N/A      | [1.000]     | [Minimal development beyond 120] |

**Tail Factor Selection:**
- Selected: [e.g., 1.000]
- Basis: [e.g., Industry benchmark, extended development analysis, judgment]
- Alternatives considered: [e.g., 1.005 for conservative scenario]

**Files Created:**
- `/analysis/ldf_selection_memo.md`
- `/analysis/ldf_comparison_to_prior.xlsx`

##### 3D: Discussion & Refinement
**Discussion Date:** [Date]  
**Participants:** [Names]

**Questions from Actuary:**
[Capture questions about specific LDF selections, outliers, or methodology]

**Feedback Received:**
[Document actuary's comments on recommendations]

**Refinements Made:**
| Development Period | Original Rec | Revised | Reason for Change |
|-------------------|-------------|---------|------------------|
| [e.g., 12-24]     | [1.164]     | [1.166] | [Actuary preferred blend of 3yr and 5yr] |

##### 3E: Final LDF Selections
- [ ] LDF selections finalized with actuary
- [ ] Documented final rationale for each selection
- [ ] Created selection backup documentation

**Final Selected LDFs:**

| Development Period | Selected LDF | Cumulative to Ultimate | Rationale |
|-------------------|-------------|----------------------|----------|
| 12-24             | [1.166]     | [1.292]              | [Final reasoning] |
| 24-36             | [1.058]     | [1.110]              | [Final reasoning] |
| 36-48             | [1.027]     | [1.051]              | [Final reasoning] |
| 48-60             | [1.012]     | [1.023]              | [Final reasoning] |
| 60-72             | [1.005]     | [1.011]              | [Final reasoning] |
| 72-84             | [1.003]     | [1.006]              | [Final reasoning] |
| 84-96             | [1.002]     | [1.003]              | [Final reasoning] |
| 96-108            | [1.001]     | [1.001]              | [Final reasoning] |
| 108-120           | [1.000]     | [1.000]              | [Final reasoning] |
| Tail              | [1.000]     | [1.000]              | [Final reasoning] |

**Files Created:**
- `/selections/chain_ladder_ldf_selections.md`
- `/selections/chain_ladder_backup.xlsx`

##### 3F: Ultimate Loss Calculation
- [ ] Applied selected LDFs to latest diagonal
- [ ] Calculated ultimate losses by accident year
- [ ] Calculated IBNR by accident year
- [ ] Created results summary tables
- [ ] Generated comparison charts

**Chain Ladder Ultimate Losses:**

| Accident Year | Latest Loss | Latest Age | CDF to Ult | Ultimate Loss | IBNR | IBNR % |
|--------------|------------|-----------|-----------|--------------|------|--------|
| 2018         |            |           |           |              |      |        |
| 2019         |            |           |           |              |      |        |
| 2020         |            |           |           |              |      |        |
| ...          |            |           |           |              |      |        |
| **Total**    |            |           |           |              |      |        |

**Summary Statistics:**
- Total Ultimate Losses: $[amount]
- Total IBNR: $[amount]
- IBNR as % of Reported: [%]
- Implied Current Year Loss Ratio: [%] (if premium available)

**Files Created:**
- `/analysis/chain_ladder_ultimate_losses.xlsx`
- `/analysis/chain_ladder_results_summary.md`
- `/output/chain_ladder_exhibits.xlsx`

##### 3G: Reasonability Testing
- [ ] Compared to prior analysis ultimate losses
- [ ] Tested sensitivity to LDF selections
- [ ] Benchmarked against industry (if available)
- [ ] Reviewed immature year implications
- [ ] Validated against expected business patterns

**Reasonability Checks:**

**Prior Period Comparison:**
| Metric | Current Analysis | Prior Analysis | Change | Expected? |
|--------|-----------------|---------------|--------|----------|
| Total Ultimate | | | | |
| Total IBNR | | | | |
| Latest AY Implied LR | | | | |

**Sensitivity Analysis:**
| Scenario | Total Ultimate | Total IBNR | Change from Base |
|----------|---------------|-----------|------------------|
| Base LDFs | | | Base |
| LDFs +5% | | | |
| LDFs -5% | | | |
| All-year avg LDFs | | | |
| 3-year avg LDFs | | | |

**Files Created:**
- `/analysis/chain_ladder_reasonability.xlsx`
- `/analysis/sensitivity_charts.png`

---
```

---

## Actuarial Selections Required

### Overview of Selection Points

The Chain Ladder method requires the actuary to make selections at multiple points. Each selection requires judgment based on data patterns, business knowledge, and professional expertise.

### Selection 1: Loss Triangle Basis

**Decision:** Use reported losses, paid losses, or incurred losses?

**Options:**
- **Reported losses (case incurred):** Case reserves + paid losses
- **Paid losses:** Only amounts actually paid
- **Incurred losses:** Reported losses adjusted for salvage/subrogation

**Considerations:**
- **Reported losses:** Most common, reflects current case reserve estimates
  - Pros: Incorporates adjuster expertise, more current than paid
  - Cons: Sensitive to case reserve adequacy changes
  - Best for: Most situations, especially when case reserves are credible

- **Paid losses:** More objective, not affected by case reserve practices
  - Pros: Objective, not influenced by reserving philosophy changes
  - Cons: Slower to respond to emerging trends, longer development tail
  - Best for: When case reserves are unreliable or have changed significantly

- **Incurred losses:** Most complete view of ultimate
  - Pros: Most comprehensive, reflects all known information
  - Cons: Requires tracking salvage/subrogation separately
  - Best for: When salvage/subrogation is material

**Questions to Ask:**
1. Have case reserving practices changed over the analysis period?
2. Are case reserves generally adequate based on historical emergence?
3. Is there material salvage/subrogation to track?
4. What basis was used in prior analyses?

**Documentation Required:**
- Selection made and rationale
- Any adjustments to raw data
- Comparison to prior analysis basis

---

### Selection 2: Loss Development Factors by Period

**Decision:** Which average (simple, volume-weighted, period length) to use for each development period?

**Options for each development period:**
- Simple average - all years
- Simple average - 5 years
- Simple average - 3 years
- Volume-weighted average - all years
- Volume-weighted average - 5 years
- Volume-weighted average - 3 years
- Judgmental selection (excluding outliers or blending methods)

**Considerations by Development Period:**

**Early Development (12-24, 24-36):**
- Usually higher factors, more volatile
- Consider: Are recent years showing different patterns (claims processing changes)?
- Typical approach: 3-5 year average (balance stability with responsiveness)
- Watch for: Operational changes, staffing changes, system implementations

**Middle Development (36-60):**
- More stable patterns typically emerge
- Consider: Is experience consistent across years?
- Typical approach: 5-year or all-year average if stable
- Watch for: One-off large losses affecting specific years

**Late Development (60-120):**
- Usually very stable, factors close to 1.0
- Consider: Is there sufficient data at these ages?
- Typical approach: All-year average for maximum credibility
- Watch for: Few data points may make averages unreliable

**Simple vs Volume-Weighted:**
- **Simple average:** Each year weighted equally
  - Use when: All years have similar credibility
  - Pros: Not dominated by large years
  - Cons: May not reflect current exposure levels

- **Volume-weighted average:** Larger loss years get more weight
  - Use when: Exposure has grown significantly
  - Pros: Reflects current scale of business
  - Cons: Can be dominated by outlier years

**Period Length (All-year vs 5-year vs 3-year):**
- **All-year:** Maximum credibility, assumes stability
  - Use when: Patterns are stable over entire history
  
- **5-year:** Balance of credibility and responsiveness
  - Use when: Standard default, most common choice
  
- **3-year:** More responsive to recent changes
  - Use when: Recent trends differ from long-term history

**Questions to Ask:**
1. Are development patterns stable across all years?
2. Have there been operational changes (claims systems, staffing, processes)?
3. Are any specific years outliers? Why?
4. Has exposure volume changed significantly?
5. What did prior analysis use? Why change or why not?
6. Do recent patterns suggest acceleration or deceleration in development?

**Red Flags:**
- Wildly different factors year to year (investigate causes)
- Recent years dramatically different from older years (may need trend adjustment)
- Obvious outliers not investigated (document and potentially exclude)
- Selections that differ significantly from prior without explanation

**Documentation Required:**
- Table showing all averaging options
- Selection for each development period with specific rationale
- Explanation of any outlier years excluded
- Comparison to prior analysis selections
- Investigation notes for any anomalies

---

### Selection 3: Tail Factor

**Decision:** What development factor to apply from oldest observed age to ultimate?

**Options:**
- 1.000 (no tail)
- Industry benchmark tail factor
- Extended development analysis
- Judgmental tail based on line of business expectations
- Range of tail factors for sensitivity

**Considerations:**

**Factors Affecting Tail Selection:**
- **Line of business:** Long-tail (e.g., general liability, medical malpractice) vs short-tail (e.g., property, auto physical damage)
- **Oldest development age:** More mature = less tail needed
- **Recent development pattern:** Still developing materially at oldest age?
- **Historical tail emergence:** What has past experience shown?
- **Industry data:** What do industry studies suggest?

**Common Approaches:**

1. **Minimal tail (1.000-1.005):**
   - Use when: Oldest age shows minimal development
   - Typical for: Short-tail lines, very mature development (120+ months)
   
2. **Moderate tail (1.005-1.025):**
   - Use when: Some development still evident at oldest age
   - Typical for: Medium-tail lines, moderately mature (84-120 months)
   
3. **Material tail (1.025-1.100+):**
   - Use when: Significant development expected beyond observed
   - Typical for: Long-tail lines, less mature cutoff (36-72 months)

**Industry Benchmark Sources:**
- CAS tail factor studies
- ISO loss development tables
- NCCI development factors
- Reinsurer published benchmarks

**Extended Development Analysis:**
- If data available beyond standard triangle, analyze true tail emergence
- Compare oldest observed age to ultimate from fully developed years

**Questions to Ask:**
1. What age is the oldest development column?
2. Is development still evident at that age?
3. What does industry data suggest for this line of business?
4. Do we have any internal data beyond the triangle cutoff?
5. What tail factor was used in prior analysis?
6. How sensitive are results to tail factor selection?

**Documentation Required:**
- Tail factor selected
- Rationale (industry benchmark, judgment, analysis)
- Source if using external data
- Sensitivity analysis showing impact of alternative tail factors
- Comparison to prior analysis

---

### Selection 4: Treatment of Outliers

**Decision:** How to handle unusually high or low age-to-age factors?

**Options:**
- Include all data as-is
- Exclude specific outlier years with documentation
- Cap/floor extreme values
- Use median instead of mean for specific periods
- Apply judgmental adjustments

**Considerations:**

**Identifying Outliers:**
- Age-to-age factor >2 standard deviations from mean
- Factors that are dramatically different from adjacent years
- Known events (large loss settlement, reserve strengthening/release)

**Handling Approaches:**

1. **Investigate and document:**
   - Always first step - understand why the outlier exists
   - Was it a one-time event or indicative of new pattern?
   
2. **Include with explanation:**
   - If outlier represents legitimate experience
   - Document why it should influence future expectations
   
3. **Exclude from average:**
   - If one-time event unlikely to repeat
   - Document exclusion clearly
   - Consider using median as alternative
   
4. **Adjust the data:**
   - Rarely appropriate
   - Only if data error or known distortion
   - Document adjustment thoroughly

**Questions to Ask:**
1. What caused this unusual development?
2. Is it a one-time event or new pattern?
3. How does including/excluding it affect ultimate losses?
4. Is there a better way to reflect this information (separate analysis, adjustment)?
5. What would a different actuary conclude looking at this?

**Documentation Required:**
- Identification of outliers
- Investigation of causes
- Decision to include/exclude with rationale
- Sensitivity showing impact of alternative treatments

---

### Selection 5: Validation and Alternatives

**Decision:** Is the selected Chain Ladder indication reasonable? What alternatives should be considered?

**Required Validations:**

1. **Comparison to prior analysis:**
   - Similar LDF selections? If not, why?
   - Ultimate losses directionally consistent?
   - Understand and explain material changes

2. **Implied loss ratios:**
   - Calculate ultimate LR for each accident year
   - Are they reasonable given pricing expectations?
   - Trending as expected?

3. **IBNR patterns:**
   - IBNR as % of reported reasonable by maturity?
   - Consistent with historical emergence patterns?

4. **Industry benchmarks:**
   - How do selected LDFs compare to industry?
   - Explained differences based on company specifics?

5. **Sensitivity testing:**
   - How much do results change with reasonable LDF variations?
   - What's the range of reasonable outcomes?

**Alternative Scenarios to Consider:**

- **Optimistic:** Lower LDFs (faster development)
- **Pessimistic:** Higher LDFs (slower development)  
- **Prior analysis:** Using previous selections
- **All-year averages:** Maximum stability
- **3-year averages:** Maximum responsiveness

**Questions to Ask:**
1. If I selected slightly different LDFs, how much would it change the answer?
2. Can I defend these selections to a  regulator or auditor?
3. Do the results make business sense?
4. What would happen if recent trends continue? Or reverse?
5. Should Chain Ladder be the primary method or just one input?

**Documentation Required:**
- Comparison table to prior analysis
- Implied loss ratio analysis
- Sensitivity analysis table
- Reasonability narrative
- Recommendation for method weighting in overall study

---

### Best Practices for Documentation

**For each selection, document:**
1. **What was selected:** Specific values chosen
2. **Why it was selected:** Rationale based on data and judgment
3. **What alternatives were considered:** Other reasonable options
4. **Impact of alternatives:** Sensitivity to different choices
5. **Comparison to prior:** Changes from previous analysis and why
6. **Support:** Data analysis, industry benchmarks, calculations

**Create supporting exhibits:**
- Development factor table with all averaging options
- Graphical displays of development patterns
- Prior analysis comparison
- Sensitivity analysis
- Outlier investigation notes

**Maintain audit trail:**
- Save intermediate calculations
- Document data sources
- Note dates of selections and who made them
- Keep version history of selection changes

---

## References

- Friedland, Jacqueline. "Estimating Unpaid Claims Using Basic Techniques." Casualty Actuarial Society, 2010.
- Wikipedia: Chain-ladder method - https://en.wikipedia.org/wiki/Chain-ladder_method
- `chainladder` Python package documentation - https://chainladder-python.readthedocs.io/
