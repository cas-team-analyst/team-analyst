import numpy as np
import pandas as pd

from modules.xl_utils import _period_int

# Unpaid = selected ultimate - latest actual of the proxy measure for that period.
UNPAID_PROXY = {
    "Incurred Loss":  "Paid Loss",
    "Paid Loss":      "Paid Loss",
    "Reported Count": "Closed Count",
    "Closed Count":   "Closed Count",
}


def _has_method(combined, measure, col):
    return col in combined.columns and combined[combined["measure"] == measure][col].notna().any()


def _fill_method_cl_values(ws, measure, combined, actual_lookup):
    """Replace CL method sheet formula cells with computed values."""
    sub = combined[combined["measure"] == measure].copy()
    sub["period_int"] = sub["period"].apply(_period_int)
    sub = sub.sort_values("period_int")
    proxy = UNPAID_PROXY.get(measure)

    for r, (_, row) in enumerate(sub.iterrows(), start=2):
        ult = row.get("ultimate_cl", np.nan)
        ult = None if pd.isna(ult) else float(ult)
        actual = row["actual"]
        actual = None if pd.isna(actual) else float(actual)

        ws.cell(r, 5).value = ult
        ws.cell(r, 6).value = (ult - actual) if ult is not None and actual is not None else None
        if proxy and proxy != measure:
            proxy_actual = actual_lookup.get((row["period"], proxy))
            ws.cell(r, 7).value = (ult - proxy_actual) if ult is not None and proxy_actual is not None else None
        else:
            ws.cell(r, 7).value = (ult - actual) if ult is not None and actual is not None else None


def _fill_method_bf_values(ws, measure, combined, actual_lookup):
    """Replace BF method sheet formula cells with computed values."""
    sub = combined[combined["measure"] == measure].copy()
    sub["period_int"] = sub["period"].apply(_period_int)
    sub = sub.sort_values("period_int")
    proxy = UNPAID_PROXY.get(measure)

    for r, (_, row) in enumerate(sub.iterrows(), start=2):
        cdf = row.get("cdf", np.nan)
        cdf = None if pd.isna(cdf) else float(cdf)
        actual = row["actual"]
        actual = None if pd.isna(actual) else float(actual)
        ult_bf = row.get("ultimate_bf", np.nan)
        ult_bf = None if pd.isna(ult_bf) else float(ult_bf)
        ult_ie = row.get("ultimate_ie", np.nan)
        ult_ie = None if pd.isna(ult_ie) else float(ult_ie)

        pct_unr = (1.0 - 1.0 / cdf) if cdf is not None and cdf != 0 else None
        unreported = (ult_bf - actual) if ult_bf is not None and actual is not None else None

        ws.cell(r, 5).value = pct_unr
        ws.cell(r, 6).value = unreported
        ws.cell(r, 8).value = ult_bf
        ws.cell(r, 9).value = (ult_bf - actual) if ult_bf is not None and actual is not None else None
        if proxy and proxy != measure:
            proxy_actual = actual_lookup.get((row["period"], proxy))
            ws.cell(r, 10).value = (ult_bf - proxy_actual) if ult_bf is not None and proxy_actual is not None else None
        else:
            ws.cell(r, 10).value = (ult_bf - actual) if ult_bf is not None and actual is not None else None


def _fill_selection_values(ws, measures_group, combined, actual_lookup):
    """Replace Selection sheet formula cells with computed values."""
    active_m = [m for m in measures_group if m in combined["measure"].unique()]
    if not active_m:
        return

    main_m = active_m[0]
    sub = combined[combined["measure"] == main_m].copy()
    sub["period_int"] = sub["period"].apply(_period_int)
    sub = sub.sort_values("period_int")

    ult_cl = {m: combined[combined["measure"] == m].set_index("period")["ultimate_cl"].to_dict() for m in active_m}
    ult_bf = {m: combined[combined["measure"] == m].set_index("period")["ultimate_bf"].to_dict() for m in active_m}
    actuals = {m: combined[combined["measure"] == m].set_index("period")["actual"].to_dict() for m in active_m}

    n = len(active_m)
    bf_m = [m for m in active_m if _has_method(combined, m, "ultimate_bf")]
    has_group_ie = any(_has_method(combined, m, "ultimate_ie") for m in active_m)

    for r, (_, row) in enumerate(sub.iterrows(), start=2):
        period = row["period"]
        col = 3
        for m in active_m:
            ws.cell(r, col).value = actuals[m].get(period)
            col += 1
        for m in active_m:
            v = ult_cl[m].get(period)
            ws.cell(r, col).value = None if v is None or (isinstance(v, float) and v != v) else v
            col += 1
        for m in bf_m:
            v = ult_bf[m].get(period)
            ws.cell(r, col).value = None if v is None or (isinstance(v, float) and v != v) else v
            col += 1
        if has_group_ie:
            col += 1  # Initial Expected already hardcoded
        # Selected Ultimate already hardcoded
        sel_ult = row["selected_ultimate"]
        sel_ult = None if pd.isna(sel_ult) else float(sel_ult)
        first_act = actuals[active_m[0]].get(period)
        ws.cell(r, col).value = (sel_ult - first_act) if sel_ult is not None and first_act is not None else None
        col += 1
        proxy_act = actuals[active_m[1]].get(period) if n > 1 else first_act
        ws.cell(r, col).value = (sel_ult - proxy_act) if sel_ult is not None and proxy_act is not None else None


def _fill_cdf_row_values(ws):
    """
    Resolve CDF formula strings in a triangle sheet's LDF Selections section to
    Python-computed values.  Used for the Values Only output.
    Right-to-left product: Selected[col] * CDF[col+1], seeded by the tail literal.
    """
    in_ldf = False
    selected_vals = {}
    cdf_row_num = None
    tail_literal_col = None

    for row_cells in ws.iter_rows():
        col1 = row_cells[0].value if row_cells else None
        if col1 == "LDF Selections":
            in_ldf = True; continue
        if not in_ldf:
            continue
        if col1 == "Selected":
            selected_vals = {
                c.column: float(c.value)
                for c in row_cells[1:]
                if isinstance(c.value, (int, float))
            }
        elif col1 == "CDF":
            cdf_row_num = row_cells[0].row
            for c in reversed(row_cells[1:]):
                if isinstance(c.value, (int, float)):
                    tail_literal_col = c.column
                    break
            break

    if cdf_row_num is None or not selected_vals or tail_literal_col is None:
        return

    prev_cdf = ws.cell(cdf_row_num, tail_literal_col).value
    for col in range(tail_literal_col - 1, 1, -1):
        cell = ws.cell(cdf_row_num, col)
        if isinstance(cell.value, str) and cell.value.startswith("="):
            ldf = selected_vals.get(col)
            if ldf is not None and prev_cdf is not None:
                prev_cdf = ldf * prev_cdf
                cell.value = round(prev_cdf, 6)
            else:
                cell.value = None
                prev_cdf = None
        elif isinstance(cell.value, (int, float)):
            prev_cdf = cell.value


def _strip_formulas(ws):
    """Replace formula strings with None so downstream readers see blank, not a formula string."""
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith("="):
                cell.value = None


def _fill_cl_main_values(ws, measure, df2, df4):
    """
    Replace formula strings in a CL main-measure sheet with Python-computed values.
    Only called for main measure sheets (e.g. Incurred Loss) -- Diag-* and CV-&-Slopes
    sheets have no formula cells.

    ATA section: each period/interval cell replaced from df2['ldf'].
    Averages section: each display-name/interval cell replaced from df4.

    Sheet structure in gen_wb after _copy_ws_filtered:
      Loss triangle title -> header -> data rows -> blank
      "Age-to-Age Factors" title -> "" header -> ATA data rows (formulas) -> blank
      "Averages" title -> "Metric" header -> avg data rows (formulas) -> blank
      "LDF Selections" title -> header -> "Selected" row
    """
    df_m = df2[df2['measure'].astype(str) == measure].copy()

    ata_lookup = {
        (str(r['period']), str(r['interval'])): r['ldf']
        for _, r in df_m[df_m['ldf'].notna()].iterrows()
    }

    avg_lookup = {}
    if df4 is not None and not df4.empty:
        df4_m = df4[df4['measure'].astype(str) == measure].copy()
        avg_data_cols = [c for c in df4_m.columns
                         if c not in ('measure', 'interval')
                         and not c.startswith('cv_')
                         and not c.startswith('slope_')]
        for _, r in df4_m.iterrows():
            intv = str(r['interval'])
            for col in avg_data_cols:
                display = col.replace('avg_exclude_high_low', 'exclude_high_low')
                avg_lookup[(display, intv)] = r[col]

    section = None
    col_headers = {}

    for row_cells in ws.iter_rows():
        col1 = row_cells[0].value if row_cells else None

        if col1 == "Age-to-Age Factors":
            section = "ata_pre_header"
            continue
        if col1 == "Averages":
            section = "avg_pre_header"
            continue
        if col1 == "LDF Selections":
            break

        if section == "ata_pre_header":
            col_headers = {c.column: str(c.value) for c in row_cells[1:] if c.value not in (None, "")}
            section = "ata"
            continue

        if section == "avg_pre_header":
            col_headers = {c.column: str(c.value) for c in row_cells[1:] if c.value not in (None, "")}
            section = "avg"
            continue

        if section == "ata":
            if col1 is None or col1 == "":
                section = None
                continue
            period = str(col1)
            for cell in row_cells[1:]:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    intv = col_headers.get(cell.column)
                    cell.value = ata_lookup.get((period, intv)) if intv else None

        elif section == "avg":
            if col1 is None or col1 == "":
                section = None
                continue
            display = str(col1)
            for cell in row_cells[1:]:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    intv = col_headers.get(cell.column)
                    cell.value = avg_lookup.get((display, intv)) if intv else None


def _fill_tail_values(ws, measure, df2):
    """
    Replace formula strings in a Tail sheet with Python-computed values.
    Only the "Average" and "CV" rows contain formulas; they summarise the observed
    ATA factors in the column above.  Header row col1 = "Accident Year" identifies
    the age columns so we can map them to df2 intervals.
    """
    df_m = df2[df2['measure'].astype(str) == measure].copy()

    # Map "to" age string -> interval string  e.g. "23" -> "11-23"
    to_age_map = {}
    for intv in df_m['interval'].dropna().unique():
        parts = str(intv).split('-')
        if len(parts) == 2:
            to_age_map[parts[1]] = str(intv)

    def _mean(intv):
        vals = df_m[df_m['interval'].astype(str) == intv]['ldf'].dropna()
        return vals.mean() if not vals.empty else None

    def _cv(intv):
        vals = df_m[df_m['interval'].astype(str) == intv]['ldf'].dropna()
        if vals.empty:
            return None
        m = vals.mean()
        return (vals.std() / m) if m and m != 0 else None

    col_to_intv = {}
    header_found = False

    for row_cells in ws.iter_rows():
        col1 = row_cells[0].value if row_cells else None

        if col1 == "Accident Year":
            col_to_intv = {c.column: to_age_map.get(str(c.value))
                           for c in row_cells[1:] if c.value is not None}
            header_found = True
            continue

        if not header_found:
            continue

        if col1 == "Average":
            for cell in row_cells[1:]:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    intv = col_to_intv.get(cell.column)
                    cell.value = _mean(intv) if intv else None

        elif col1 == "CV":
            for cell in row_cells[1:]:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    intv = col_to_intv.get(cell.column)
                    cell.value = _cv(intv) if intv else None
