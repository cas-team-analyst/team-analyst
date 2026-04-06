# Replication Steps

This file records the exact sequence of actions taken to recreate the analysis.

1. **Data Ingestion**
   - Executed `scripts/1a-prep-data.py` to process Excel data (`canonical-triangles.xlsx` and `canonical-elrs.xlsx`) into `.parquet` format. Includes `Exposure` measure mapping.

2. **Data Engineering & Enhancements**
   - Executed `scripts/1b-enhance-data.py` to calculate raw LDFs metrics from triangles.
   - Executed `scripts/1c-diagnostics.py` to gather diagnostic checks on historical triangle data.
   - Executed `scripts/1d-averages-qa.py` to compute traditional LDF averages (e.g. 3yr, 5yr, volume-weighted) across all measures.

3. **LDF Selections**
   - Executed `scripts/2a-chainladder-create-excel.py` to build the `selections/Chain Ladder Selections.xlsx` document.
   - AI generated automated selections using the logic defined in `agents/selector-chain-ladder-ldf.md` and saved to `selections/chainladder.json`.
   - Executed `scripts/2b-chainladder-update-selections.py` to update the Excel file with the AI selections + rationale.

4. **Deterministic Methods**
   - Executed `scripts/2c-chainladder-ultimates.py` to compute Chain Ladder ultimates.
   - Executed `scripts/3-ie-ultimates.py` to compute Initial Expected (a priori) ultimates.
   - Executed `scripts/4-bf-ultimates.py` to compute Bornhuetter-Ferguson ultimates.

5. **Ultimates Selections**
   - Created and executed `scripts/5a-ultimates-create-excel.py` to organize deterministic methods into an actionable spreadsheet format.
   - Created and executed script `scripts/generate_ultimates_json.py` to automate applying the maturity-based selection hierarchy weighting methods by period age (e.g. 100% BF for fresh periods, 100% CL for old periods). Ouput saved to `selections/ultimates.json`.
   - Created and executed `scripts/5b-ultimates-update-selections.py` to flush JSON selection values back into the `selections/Ultimates.xlsx` file.
