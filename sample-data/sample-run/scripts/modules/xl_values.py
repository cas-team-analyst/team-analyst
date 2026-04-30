# Simplified xl_values.py - formula-related functions removed
# Only UNPAID_PROXY constant and _has_method() function remain (used by script 6)

import pandas as pd

# Unpaid = selected ultimate - latest actual of the proxy measure for that period.
UNPAID_PROXY = {
    "Incurred Loss":  "Paid Loss",
    "Paid Loss":      "Paid Loss",
    "Reported Count": "Closed Count",
    "Closed Count":   "Closed Count",
}


def _has_method(combined, measure, col):
    """Check if a method column has any non-null values for a given measure."""
    return col in combined.columns and combined[combined["measure"] == measure][col].notna().any()
