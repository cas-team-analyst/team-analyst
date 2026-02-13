_Copy these steps into PROGRESS to use this skill._

- [ ] Based on available data, determine which triangles we will use to come up with Ultimates estimates: Paid Losses, Incurred Losses, Reported Claims, Closed Claims, etc.

## Data Extraction (One Time)

- [ ] Copy `.claude\skills\chain-ladder-method\template_extraction.py` and adapt it:
  - Update data source path and format
  - Modify `load_triangle_from_excel()` to match your data
  - Set triangle names for your business
- [ ] Run your extraction script: `python your_extraction_script.py`
- [ ] Verify CSV files generated in the expected format:
  - `output/processed/[name]_triangle.csv` for each triangle
  - `output/selections/[name]_selections.csv` for each triangle

---

## Per-Triangle Steps

_For each triangle identified, copy these steps into PROGRESS and work through them one at a time._

**Triangle: [NAME]**

### 1. Review Diagnostics and Adjust Selections
- [ ] Review generated CSV files:
  - `output/processed/[trianglename]_triangle.csv` - Triangle data
  - `output/selections/[trianglename]_selections.csv` - Auto-generated LDF selections
- [ ] Calculate and review diagnostics (see SKILL.md for detailed code examples):
  - Load triangle as DataFrame (wide format: periods as index, ages as columns)
  - Calculate historical LDFs, averages, and QA metrics (CV, slope)
  - Interpret CV and slope thresholds (see SKILL.md "Diagnostic Interpretation")
- [ ] Adjust selections based on diagnostic insights:
  - Load, edit, and save `output/selections/[trianglename]_selections.csv`
  - Update AverageType or ManualValue as needed
  - Document reasoning in Reasoning column
- [ ] Document any adjustments made in AUDIT.md with reasoning

### 2. Generate HTML Report
- [ ] Copy populate script to output/scripts: `cp .claude/skills/chain-ladder-method/populate_selections.py output/scripts/`
- [ ] Run: `python output/scripts/populate_selections.py --csv output/selections/[trianglename]_selections.csv`
- [ ] Verify `output/selections/[trianglename]_selections.html` created

### 3. Review in Browser
- [ ] Start Vite dev server from project root: `npx vite --port 5175`
- [ ] Open: http://localhost:5175/output/selections/[trianglename]_selections.html
- [ ] Work with the user to make adjustments. If adjustments needed, edit CSV and regenerate HTML (repeat steps 2-3)
- [ ] Close Vite server after all triangles reviewed