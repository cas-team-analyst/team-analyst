def df_to_markdown(df, index=False):
    if df.empty:
        return "No data\n"
    if index:
        df = df.reset_index()
    str_df = df.astype(str)
    headers = list(str_df.columns)
    header_str = "| " + " | ".join(headers) + " |"
    sep_str = "|" + "|".join(["---"] * len(headers)) + "|"
    rows = []
    for _, row in str_df.iterrows():
        rows.append("| " + " | ".join(row.values) + " |")
    return "\n".join([header_str, sep_str] + rows) + "\n"
