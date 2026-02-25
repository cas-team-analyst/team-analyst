"""
goal: Step 2 of validate-data — build a summary of a loaded DataFrame for a
      given data format.

Data formats:
  "loss_run"  — long format, one row per claim per evaluation date
  "triangle"  — wide format, rows = origin periods, columns = development periods

This script contains no user interaction. The agent (SKILL.md) is responsible
for asking the user which format their data is in, showing the returned summary,
and requesting confirmation before proceeding.
"""

from dataclasses import dataclass
from typing import Literal
import pandas as pd


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

DataFormat = Literal["loss_run", "triangle"]

FORMAT_LABELS = {
    "loss_run": "Loss Run (long format — one row per claim per evaluation date)",
    "triangle": "Triangle (wide format — rows = origin periods, columns = development periods)",
}


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class DataSummary:
    """Summary of the loaded dataset and the user-confirmed format."""

    format: DataFormat
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
            f"  Format : {FORMAT_LABELS[self.format]}",
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

def summarize(df: pd.DataFrame, fmt: DataFormat) -> DataSummary:
    """
    Build a DataSummary for the given DataFrame and format.

    Args:
        df:  The DataFrame loaded in step 1.
        fmt: The data format as identified by the user — "loss_run" or "triangle".

    Returns:
        DataSummary with shape, column metadata, null counts, and a sample.

    Raises:
        ValueError: If fmt is not a recognised DataFormat value.
    """

    if fmt not in FORMAT_LABELS:
        raise ValueError(
            f"Unknown format '{fmt}'. Expected one of: {list(FORMAT_LABELS.keys())}"
        )

    n_rows, n_cols = df.shape
    columns = df.columns.tolist()

    return DataSummary(
        format=fmt,
        shape=(n_rows, n_cols),
        columns=columns,
        dtypes={col: str(df[col].dtype) for col in columns},
        null_counts={col: int(df[col].isna().sum()) for col in columns},
        sample=df.head(5),
    )
