This file tracks changes and decisions made.

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
