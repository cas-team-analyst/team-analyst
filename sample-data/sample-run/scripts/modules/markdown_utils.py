def df_to_markdown(df, index=False):
    import pandas as pd
    import numpy as np
    
    if df.empty:
        return "No data\n"
    if index:
        df = df.reset_index()
    
    # Format values: whole numbers without decimals, preserve other formats
    formatted_df = df.copy()
    for col in formatted_df.columns:
        formatted_df[col] = formatted_df[col].apply(lambda x: 
            '' if pd.isna(x) else
            f'{int(x)}' if isinstance(x, (int, float, np.number)) and not pd.isna(x) and float(x) == int(x) else
            str(x)
        )
    
    headers = [str(h) for h in formatted_df.columns]
    header_str = "| " + " | ".join(headers) + " |"
    sep_str = "|" + "|".join(["---"] * len(headers)) + "|"
    rows = []
    for _, row in formatted_df.iterrows():
        rows.append("| " + " | ".join(row.values) + " |")
    return "\n".join([header_str, sep_str] + rows) + "\n"
