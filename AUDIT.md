This file tracks changes and decisions made.

## 2026-03-22

### Project Setup
- Copied PROGRESS.md to project root and set interaction level to "Careful"
- Installed Python packages from requirements.txt
- Confirmed data file: `Triangle Examples 1.xlsx`

### EDA: Triangle Examples 1.xlsx
- Explored all 4 sheets. Identified WC paid/incurred/count development triangles, AY 2001-2024, 24 development ages (11-287 months)
- Updated PROJECT.md with file summaries and project metadata

## 2026-02-16

### JSON Format Update for Chain Ladder Reports
- **Change**: Modified JSON export format in 6-update-report.py to use column headers with data arrays
- **Reasoning**: Reduces redundancy by not repeating column names in every row object
- **Format**: Changed from array of objects to object with "columns" and "data" arrays
- **Example**:
  ```json
  "triangleData": {
    "columns": ["period", "age", "value"],
    "data": [
      ["Org Pd 1", "Dev Pd 1", 1361.0],
      ["Org Pd 1", "Dev Pd 2", 2246.0]
    ]
  }
  ```
- **Impact**: 
  - More compact format (similar to CSV in JSON)
  - Still maintains one data row per line for easy scanning
  - File sizes: ~46 KB per measure
  - Line count: 671 lines (slightly more than previous 660 due to structural overhead)
  - Applied to all 4 sections: triangleData, qaMetrics, actuarialDiagnostics, selections
