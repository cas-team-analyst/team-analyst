"""
goal: Step 1 of identify-format — load a data file into a pandas DataFrame.

Supported formats: .csv, .xlsx, .xlsm, .xls
"""

from pathlib import Path
from typing import Optional
import pandas as pd


# File extensions the skill accepts.
SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xlsm", ".xls"}

def load_data(
    file_path: str | Path,
    header: int = 0,
) -> dict[str, pd.DataFrame]:
    """
    Load all tabs/sheets from a data file into a dict of DataFrames.

    For Excel files, keys are sheet names. For CSV, the single DataFrame
    is under the key "data" (or the file stem if you prefer one table).

    Args:
        file_path: Path to the data file (string or pathlib.Path).
        header: Row number (0-indexed) to use as column headers. Defaults to 0.

    Returns:
        dict mapping tab/sheet name to pd.DataFrame.

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError: If the file extension is not supported.
    """
    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Accepted formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if ext == ".csv":
        df = pd.read_csv(path, header=header)
        return {"data": df}
    else:
        engine = "xlrd" if ext == ".xls" else "openpyxl"
        all_sheets = pd.read_excel(
            path,
            sheet_name=None,
            header=header,
            engine=engine,
        )
        return all_sheets
