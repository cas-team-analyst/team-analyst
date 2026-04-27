# Reads Analysis.xlsx (produced by 6a) and fills formula cells with
# Python-computed values to produce Analysis - Values Only.xlsx.
# The Values Only file is safe to read with openpyxl/pandas without Excel
# evaluating cross-workbook formulas first (used by script 7+).
#
# Prereq: 6a-create-complete-analysis.py must have run first.
#
# run-note: Run from the scripts/ directory:
#     cd scripts/
#     python 6b-create-values-only.py

import os
import pathlib

import pandas as pd
from openpyxl import load_workbook

from modules import config
from modules.xl_utils import measure_short_name
from modules.xl_values import (
    _has_method,
    _fill_method_cl_values,
    _fill_method_bf_values,
    _fill_method_ie_values,
    _fill_selection_values,
    _fill_cdf_row_values,
    _strip_formulas,
    _fill_cl_main_values,
    _fill_tail_values,
)
from modules.analysis_loaders import (
    MEASURE_TO_CATEGORY,
    load_selections,
    load_selection_reasoning,
    load_combined,
    get_exposure,
)

# ── Config ────────────────────────────────────────────────────────────────────

INPUT_ULTIMATES        = config.ULTIMATES + "projected-ultimates.parquet"
INPUT_TRIANGLES        = config.PROCESSED_DATA + "1_triangles.parquet"
INPUT_SELECTIONS_EXCEL = config.SELECTIONS + "Ultimates.xlsx"
INPUT_COMPLETE         = config.BASE_DIR + "Analysis.xlsx"
OUTPUT_VALUES          = config.BASE_DIR + "Analysis - Values Only.xlsx"

INPUT_CL_ENHANCED  = config.PROCESSED_DATA + "2_enhanced.parquet"
INPUT_LDF_AVERAGES = config.PROCESSED_DATA + "4_ldf_averages.parquet"

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not pathlib.Path(INPUT_COMPLETE).exists():
        raise FileNotFoundError(
            f"{INPUT_COMPLETE} not found. Run 6a-create-complete-analysis.py first."
        )

    sel_lookup = load_selections(INPUT_SELECTIONS_EXCEL)
    combined, _ = load_combined(INPUT_ULTIMATES, sel_lookup)
    reason_lookup = load_selection_reasoning(INPUT_SELECTIONS_EXCEL)
    combined["selected_reasoning"] = combined.apply(
        lambda row: reason_lookup.get(
            (MEASURE_TO_CATEGORY.get(row["measure"], row["measure"]), row["period"]),
            ""
        ) or "",
        axis=1
    )
    exp_map  = get_exposure(INPUT_TRIANGLES)
    measures = [m for m in combined["measure"].unique() if m != "Exposure"]

    print(f"Measures: {measures}")
    print("Loading Complete Analysis.xlsx...")
    wb = load_workbook(INPUT_COMPLETE, data_only=False)

    print("Computing formula values for Values Only...")
    df2_enh = pd.read_parquet(INPUT_CL_ENHANCED) if pathlib.Path(INPUT_CL_ENHANCED).exists() else pd.DataFrame()
    df4_avg = pd.read_parquet(INPUT_LDF_AVERAGES) if pathlib.Path(INPUT_LDF_AVERAGES).exists() else None
    measures_short_set = {measure_short_name(m) for m in measures}
    actual_lookup_full = combined.set_index(["period", "measure"])["actual"].to_dict()

    for sname in wb.sheetnames:
        ws = wb[sname]
        if sname in measures_short_set and not df2_enh.empty:
            full_m = next((m for m in measures if measure_short_name(m) == sname), None)
            if full_m:
                _fill_cl_main_values(ws, full_m, df2_enh, df4_avg)
                _fill_cdf_row_values(ws)
            _strip_formulas(ws)
        elif sname.endswith(" CL"):
            full_m = next((m for m in measures if measure_short_name(m) == sname[:-3]), None)
            if full_m:
                _fill_method_cl_values(ws, full_m, combined, actual_lookup_full)
            _strip_formulas(ws)
        elif sname.endswith(" BF"):
            full_m = next((m for m in measures if measure_short_name(m) == sname[:-3]), None)
            if full_m:
                _fill_method_bf_values(ws, full_m, combined, actual_lookup_full)
            _strip_formulas(ws)
        elif sname.endswith(" IE"):
            full_m = next((m for m in measures if measure_short_name(m) == sname[:-3]), None)
            if full_m and _has_method(combined, full_m, "ultimate_ie"):
                _fill_method_ie_values(ws, full_m, combined, exp_map)
            _strip_formulas(ws)
        elif sname == "Loss Selection":
            _fill_selection_values(ws, ["Incurred Loss", "Paid Loss"], combined, actual_lookup_full)
            _strip_formulas(ws)
        elif sname == "Count Selection":
            _fill_selection_values(ws, ["Reported Count", "Closed Count"], combined, actual_lookup_full)
            _strip_formulas(ws)
        else:
            _strip_formulas(ws)

    os.makedirs(pathlib.Path(OUTPUT_VALUES).parent, exist_ok=True)
    wb.save(OUTPUT_VALUES)
    print(f"  Saved -> {OUTPUT_VALUES}")

    if os.name == "nt":
        from modules.verify_formulas import run_verify
        run_verify()

if __name__ == "__main__":
    main()
