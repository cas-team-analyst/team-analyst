---
name: chain-ladder-method
description: Guide for using the Chain Ladder (Loss Development Method) for actuarial loss reserving.
---

# Chain Ladder Analysis Skill

## Overview
This skill automates chain ladder analysis using a JSON-based workflow that separates triangle data from LDF selections, making reviews efficient and reproducible.

## Quick Start

### 1. Extract Triangle Data
Copy and adapt `template_extraction.py` to extract your triangles:
```bash
python your_extraction_script.py
```

This generates CSV files:
- `output/processed/[name]_triangle.csv` - Triangle data (periods, ages, values)
- `output/selections/[name]_selections.csv` - LDF selections (averages/manual values with reasoning)

### 2. Review & Adjust Selections
Edit `_selections.csv` files if needed:
- Change `averageType`: `simple3`, `simple5`, `simpleAll`, `weighted3`, `weighted5`, `weightedAll`
- Or use `manualValue` for judgment overrides
- Update `reasoning` to document decisions

### 3. Generate HTML Reports
```bash
# First time: Copy script to output/scripts/
cp .claude/skills/chain-ladder-method/populate_selections.py output/scripts/

# Then generate report
python output/scripts/populate_selections.py --csv output/selections/[name]_selections.csv
```

### 4. View in Browser
```bash
npx vite --port 5175  # Run from project root
```
Open: http://localhost:5175/output/selections/[name]_selections.html

## Workflow

Copy steps from `PROGRESS.MD` into your project's `PROGRESS.md` file for detailed checklist.

## File Structure

### Core Library
- **chain_ladder_functions.py** - Reusable functions for triangle analysis
  
  **Diagnostic Functions** (calculate metrics, don't make decisions):
  - `calculate_historical_ldfs(triangle_df)` - Compute age-to-age factors by year
  - `calculate_average_ldfs(ldf_df, triangle_df)` - Calculate 9 average types (simple/weighted/medial × 3yr/5yr/all)
  - `calculate_qa_metrics(ldf_df)` - Calculate CV (volatility) and slope (trend) for each factor
  
  **Selection Functions** (create initial selections using diagnostics):
  - `make_selections_from_averages(averages, qa_metrics)` - Generate 4 scenarios from diagnostics:
    * **Conservative**: Emphasizes stability and longer-term data
    * **Best Estimate**: Balanced approach using standard methods
    * **Optimistic**: Focuses on recent favorable trends
    * **Final Recommendation**: Intelligent selection based on combined metrics *(default for user edits)*
  - `create_selections_csv(triangle_df, name)` - Create selections DataFrame
  - `save_selections_csv(df, path)` - Save selections to CSV
  
  **Full Workflow**:
  - `perform_full_analysis(triangle_df, name)` - End-to-end: diagnostics → auto-selections → save CSVs
  - `save_triangle_data(triangle_df, name, path)` - Save triangle to CSV
  
  **Note**: All functions use standard pandas DataFrames (wide format: periods as index, ages as columns)

### Templates (Adapt for Your Project)
- **template_extraction.py** - Example showing how to:
  - Load triangle data from your source (Excel, DB, CSV)
  - Create wide DataFrames (periods as index, ages as columns)
  - Run `perform_full_analysis()` to generate JSONs
  
- **template_report.html** - HTML template used by populate_selections.py
  - Uses absolute paths (`/static/`) for shared CSS/fonts
  - Auto-calculates LDFs, averages, and cumulative factors
  - Vite dev server enables hot-reload during review

### Scripts (Standardized, Take CSV Input)
- **output/scripts/populate_selections.py** - Generates HTML from CSV files
  - Takes standardized CSV input (triangle + selections)
  - Produces interactive HTML report with calculations

## Agent Behavior with Scenarios

**When users request edits:**
- **Default assumption**: User wants to modify the "Final Recommendation" scenario
- **Explicit scenario**: Only edit other scenarios when user specifically mentions "Conservative", "Best Estimate", or "Optimistic"
- **Reasoning**: The Final Recommendation represents the agent's best judgment based on statistical analysis

**Example user requests:**
- "Make the 12-24 factor more conservative" → Modify Final Recommendation scenario
- "Increase the Conservative scenario's 24-36 factor" → Modify Conservative scenario specifically
- "I think we should use manual judgment for the tail" → Modify Final Recommendation scenario

## CSV Format Reference

### Triangle CSV (`output/processed/[name]_triangle.csv`)
```csv
Period,12,24,36,48
2020,1000,1500,1800,1900
2021,1100,1650,1980,
2022,1200,1800,,
2023,1300,,,
```
- First column: Period labels
- Remaining columns: Development ages (12, 24, 36, etc.)
- Empty cells for future development periods

### Selections CSV (`output/selections/[name]_selections.csv`)
```csv
Scenario,AgeFactor,AverageType,ManualValue,Reasoning
Conservative,12-24,weighted3,,Recent weighted trend shows stability
Conservative,24-36,,,1.015,Judgment adjustment based on market
Best Estimate,12-24,simple5,,Balanced approach
Final Recommendation,12-24,simple5,,RECOMMENDED: Moderate volatility supports 5-year average
Final Recommendation,24-36,simple3,,RECOMMENDED: Stable with improving trend - recent experience preferred
```
- **Scenario**: Label (Conservative, Best Estimate, Optimistic, Final Recommendation)
- **AgeFactor**: Development factor (e.g., "12-24")
- **AverageType**: One of: simple3, simple5, simpleAll, weighted3, weighted5, weightedAll
- **ManualValue**: Custom value (leave AverageType empty if using this)
- **Reasoning**: Explanation for the selection

**Key Points:**
- One row per age-to-age factor per scenario (4 scenarios total)
- Use either AverageType OR ManualValue (not both)
- Reasoning is required for documentation
- **Final Recommendation** scenario uses "RECOMMENDED:" prefix in reasoning to indicate agent's preferred choice

**Average Types:**
| Type | Description |
|------|-------------|
| `simple3` | Simple average, 3 most recent years |
| `simple5` | Simple average, 5 most recent years |
| `simpleAll` | Simple average, all years |
| `weighted3` | Volume-weighted, 3 most recent years |
| `weighted5` | Volume-weighted, 5 most recent years |
| `weightedAll` | Volume-weighted, all years |

## Diagnostic Interpretation

### Coefficient of Variation (CV)
Measures volatility of historical age-to-age factors:
- **CV < 0.05**: Low volatility → Recent averages (3yr) are reliable
- **CV 0.05-0.10**: Moderate volatility → Medium periods (5yr) balance stability and responsiveness
- **CV > 0.10**: High volatility → Longer periods (all years) provide more stability

### Slope
Measures trend direction in recent factors:
- **Slope < 0**: Declining trend → Recent factors may be more relevant (consider shorter periods)
- **Slope ≈ 0**: Stable pattern → Standard averages appropriate
- **Slope > 0**: Increasing trend → Longer periods may dampen future increases

### Combining Metrics
- **Low CV + Declining Slope**: Short weighted (weighted3) captures trend reliably
- **High CV + Any Slope**: Long periods (all years) needed for stability
- **Moderate CV + Stable**: 5yr averages balance historical data and recent changes

## Python Usage Examples

### Extract and Analyze
```python
from chain_ladder_functions import perform_full_analysis
import pandas as pd

# Load your data (wide format: periods as index, ages as columns)
df = pd.read_excel("data/triangles.xlsx", sheet_name="Paid", index_col=0)

# Perform full analysis (generates CSV files)
perform_full_analysis(
    triangle_df=df,
    triangle_name="Paid Losses",
    processed_dir="output/processed",
    selections_dir="output/selections"
)
```

### Review Diagnostics and Refine Selections
```python
from chain_ladder_functions import (
    calculate_historical_ldfs,
    calculate_average_ldfs, calculate_qa_metrics
)
import pandas as pd

# Load triangle (wide format: periods as index, ages as columns)
triangle_df = pd.read_csv("output/processed/paid_losses_triangle.csv", index_col=0)

# Calculate diagnostics
ldf_df = calculate_historical_ldfs(triangle_df)
averages_df = calculate_average_ldfs(ldf_df, triangle_df)
qa_metrics = calculate_qa_metrics(ldf_df)

# Review diagnostics
print("Historical Age-to-Age Factors:")
print(ldf_df)
print("\nAvailable Averages:")
print(averages_df)
print("\nQA Metrics (CV=volatility, slope=trend):")
for interval, metrics in qa_metrics.items():
    print(f"{interval}: CV={metrics['cv']:.3f}, Slope={metrics['slope']:.4f}")

# Interpret and adjust selections
selections_df = pd.read_csv("output/selections/paid_losses_selections.csv")

# Example: Adjust Conservative scenario for 12-24 factor based on diagnostics
# If CV < 0.05 and slope < 0, use simple3 for recent declining trend
mask = (selections_df['Scenario'] == 'Conservative') & (selections_df['AgeFactor'] == '12-24')
if qa_metrics['12-24']['cv'] < 0.05 and qa_metrics['12-24']['slope'] < 0:
    selections_df.loc[mask, 'AverageType'] = 'simple3'
    selections_df.loc[mask, 'Reasoning'] = 'Low volatility + declining trend supports recent 3yr'

# Save adjusted selections
selections_df.to_csv("output/selections/paid_losses_selections.csv", index=False)
```

### Manual Selection Creation
```python
import pandas as pd

# Create selections DataFrame
selections_df = pd.DataFrame([
    {"Scenario": "Conservative", "AgeFactor": "12-24", 
     "AverageType": "weighted5", "ManualValue": None,
     "Reasoning": "Stable volume pattern"},
    {"Scenario": "Conservative", "AgeFactor": "24-36",
     "AverageType": None, "ManualValue": 1.05,
     "Reasoning": "Known change in claims handling"}
])

selections_df.to_csv("output/selections/paid_losses_selections.csv", index=False)
```

## Tips

**Separation of Concerns:**
- Triangle data rarely changes → `output/processed/[name]_triangle.csv`
- Selections change during review → `output/selections/[name]_selections.csv`
- CSV format is human-readable and Excel-friendly

**Static Assets:**
- All HTML reports share `/static/` folder (CSS, fonts, JS libraries)
- No duplication per report
- Vite must serve from project root for paths to resolve

**Auto-Generated Selections:**
- `perform_full_analysis()` creates intelligent defaults based on:
  - Coefficient of variation (volatility)
  - Trend analysis (recent slopes)
  - Available data points
- Review and adjust as needed for your business context
