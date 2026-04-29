# Shared diagnostics sheet builder for Chain Ladder LDF workbook and Analysis workbook.

import pandas as pd

DIAG_SHEET_LABELS = {
    'reported_claims': 'REPORTED CLAIMS',
    'incurred_severity': 'INCURRED SEVERITY',
    'paid_severity': 'PAID SEVERITY',
    'paid_to_incurred': 'PAID TO INCURRED',
    'case_reserves': 'CASE RESERVES',
    'open_counts': 'OPEN COUNTS',
    'average_case_reserve': 'AVERAGE CASE RESERVE',
    'claim_closure_rate': 'CLAIM CLOSURE RATE',
    'incurred_loss_rate': 'INCURRED LOSS RATE',
    'paid_loss_rate': 'PAID LOSS RATE',
    'reported_frequency': 'REPORTED FREQUENCY',
    'closed_frequency': 'CLOSED FREQUENCY',
    'incremental_paid_severity': 'INCREMENTAL PAID SEVERITY',
    'incremental_closure_rate': 'INCREMENTAL CLOSURE RATE',
}

DIAG_NUMBER_FORMATS = {
    'reported_claims': '#,##0',
    'incurred_severity': '#,##0',
    'paid_severity': '#,##0',
    'paid_to_incurred': '0.0000',
    'case_reserves': '#,##0',
    'open_counts': '#,##0',
    'average_case_reserve': '#,##0',
    'claim_closure_rate': '0.00%',
    'incurred_loss_rate': '#,##0',
    'paid_loss_rate': '#,##0',
    'reported_frequency': '0.0000',
    'closed_frequency': '0.0000',
    'incremental_paid_severity': '#,##0',
    'incremental_closure_rate': '0.00%',
}


def build_combined_diagnostics_sheet(ws, diagnostic_cols, df2, df3, fmt):
    """
    Build combined diagnostics sheet with all diagnostic triangles stacked vertically.
    
    Args:
        ws: xlsxwriter worksheet
        diagnostic_cols: list of diagnostic column names to include
        df2: enhanced DataFrame with period/age/measure data
        df3: diagnostics DataFrame with diagnostic metric values
        fmt: format dictionary (must include 'wb' for workbook reference)
    """
    first_measure = df2['measure'].cat.categories[0]
    df_m = df2[df2['measure'] == first_measure].copy()
    periods = df_m['period'].cat.categories.tolist()
    ages = [str(a) for a in df_m['age'].cat.categories.tolist()]
    
    row_ptr = 0
    
    for diag_col in diagnostic_cols:
        # Skip redundant/unnecessary diagnostics
        if diag_col in ('reported_claims', 'incremental_incurred_severity'):
            continue
        
        number_format = DIAG_NUMBER_FORMATS.get(diag_col, "0.0000")
        
        # Create format with specific number format
        diag_data_fmt = fmt['wb'].add_format({
            'align': 'right',
            'valign': 'vcenter',
            'num_format': number_format
        })
        
        # Write section title
        label = DIAG_SHEET_LABELS.get(diag_col, diag_col.replace('_', ' ').upper())
        ws.merge_range(row_ptr, 0, row_ptr, len(ages), label, fmt['diagnostic_section'])
        row_ptr += 1
        
        # Write header row
        ws.write(row_ptr, 0, "Period", fmt['subheader_left'])
        for c_idx, age in enumerate(ages):
            ws.write(row_ptr, c_idx + 1, age, fmt['subheader_right'])
        row_ptr += 1
        
        # Write data rows - all values from df3
        # Build data dict from df3
        diag_dict = {}
        for _, row in df3.iterrows():
            if diag_col in row and pd.notna(row[diag_col]):
                diag_dict[(str(row['period']), str(row['age']))] = row[diag_col]
        
        for period in periods:
            ws.write(row_ptr, 0, str(period), fmt['label'])
            for c_idx, age in enumerate(ages):
                val = diag_dict.get((str(period), age))
                if val is not None:
                    ws.write(row_ptr, c_idx + 1, val, diag_data_fmt)
            row_ptr += 1
        
        # Add spacing between sections
        row_ptr += 1
    
    ws.set_column(0, 0, 22)
    for c_idx in range(1, len(ages) + 1):
        ws.set_column(c_idx, c_idx, 12)
