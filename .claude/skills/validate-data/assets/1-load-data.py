"""
goal: Step 1 of validate-data — load a data file into a pandas DataFrame.

Supported formats: .csv, .xlsx, .xlsm, .xls

This script contains no user interaction. The agent (SKILL.md) is responsible
for asking the user for a file path and passing it to load_data().
"""

from pathlib import Path
from typing import Optional
import pandas as pd


# File extensions the skill accepts.
SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xlsm", ".xls"}


def load_data(
    file_path: str | Path,
    sheet_name: Optional[str | int] = 0,
    header: int = 0,
) -> pd.DataFrame:
    """
    Validate and load a data file into a pandas DataFrame.

    Args:
        file_path:   Path to the data file (string or pathlib.Path).
        sheet_name:  Sheet name or index for Excel files. Defaults to 0 (first sheet).
        header:      Row number (0-indexed) to use as column headers. Defaults to 0.

    Returns:
        pd.DataFrame containing the raw file contents.

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError: If the file extension is not supported.
    """

    path = Path(file_path).expanduser().resolve()

    # Validate existence.
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Validate extension.
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Accepted formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # Read the file.
    if ext == ".csv":
        df = pd.read_csv(path, header=header)
    else:
        engine = "xlrd" if ext == ".xls" else "openpyxl"
        df = pd.read_excel(
            path,
            sheet_name=sheet_name,
            header=header,
            engine=engine,
        )

    return df
