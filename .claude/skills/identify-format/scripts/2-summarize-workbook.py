"""
goal: Step 2 of identify-format — build a raw summary of a loaded DataFrame:
      shape, column names, dtypes, null counts, and sample rows.
      Supports per-tab summaries when given a workbook (dict of DataFrames).
"""

from dataclasses import dataclass

import pandas as pd


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class DataSummary:
    """Structural summary of the loaded dataset."""

    shape: tuple[int, int]
    columns: list[str]
    dtypes: dict[str, str]
    null_counts: dict[str, int]
    sample: pd.DataFrame  # first few rows

    def report(self) -> str:
        """Return a formatted text report suitable for display to the user."""
        n_rows, n_cols = self.shape
        lines = [
            "=" * 60,
            f"  Shape  : {n_rows:,} rows × {n_cols} columns",
            "",
            "  Columns:",
        ]
        for col in self.columns:
            null_pct = (
                f"{self.null_counts[col] / n_rows:.0%} null"
                if n_rows > 0
                else "n/a"
            )
            lines.append(f"    • {col}  [{self.dtypes[col]}]  {null_pct}")

        lines += [
            "",
            "  First rows:",
            self.sample.to_string(index=False),
            "=" * 60,
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def summarize(df: pd.DataFrame) -> DataSummary:
    """
    Build a DataSummary for the given DataFrame.

    Args:
        df: The DataFrame loaded in step 1.

    Returns:
        DataSummary with shape, column metadata, null counts, and a sample.
    """
    n_rows, n_cols = df.shape
    columns = df.columns.tolist()

    return DataSummary(
        shape=(n_rows, n_cols),
        columns=columns,
        dtypes={col: str(df[col].dtype) for col in columns},
        null_counts={col: int(df[col].isna().sum()) for col in columns},
        sample=df.head(5),
    )


def summarize_workbook(sheets: dict[str, pd.DataFrame]) -> str:
    """
    Build a combined report with a data summary for each tab in the workbook.

    Use with the result of load_workbook() from 1-load-data to get one summary
    section per sheet/tab (shape, columns, dtypes, null counts, sample rows).

    Args:
        sheets: Map of tab/sheet name to DataFrame (e.g. from load_workbook).

    Returns:
        Formatted string with a "Tab: <name>" section and full summary for each.
    """
    parts: list[str] = []
    for tab_name, df in sheets.items():
        parts.append("")
        parts.append(f"===== Tab: {tab_name} =====")
        parts.append(summarize(df).report())
    return "\n".join(parts).strip()
