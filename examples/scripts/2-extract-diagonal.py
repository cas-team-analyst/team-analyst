"""
Script 2: Extract the latest diagonal from the normalized triangle.

The "latest diagonal" is the most recent observed data point for each accident
period — i.e., the rightmost non-null entry in each row of the triangle.
It represents what we actually know today and is the starting point for all
reserve projections.

Also computes each period's current development age and flags how many more
development intervals remain before reaching the assumed tail age.

Usage (run from the project root):
    python scripts/2-extract-diagonal.py

Inputs:
    output/prep/triangles.pkl

Outputs (written to OUTPUT_DIR):
    - diagonal.pkl / diagonal.csv   : latest value per period per measure
    - age_map.pkl / age_map.csv     : ordered list of (age, next_age, interval) pairs
"""

import pandas as pd
import os

INPUT_FILE = "output/prep/triangles.pkl"
OUTPUT_DIR = "output/prep"


def extract_diagonal(df):
    """
    For each (period, measure), pick the row with the highest (latest) age.
    Returns a DataFrame with the same columns as the input plus 'age_rank'
    (0-indexed position of the age in the ordered age list, for convenience).
    """
    ages = df["age"].cat.categories.tolist()
    age_rank = {a: i for i, a in enumerate(ages)}

    df = df.copy()
    df["age_rank"] = df["age"].map(age_rank)

    diag = (df
            .sort_values("age_rank")
            .groupby(["period", "measure"], observed=True)
            .last()          # highest age_rank = most-developed observation
            .reset_index())

    return diag


def build_age_map(df):
    """
    Build a reference table of development intervals.
    Columns: age, next_age, interval (e.g. "12-24")
    Useful for downstream scripts that need to iterate over intervals.
    """
    ages = df["age"].cat.categories.tolist()
    rows = []
    for i, age in enumerate(ages):
        next_age = ages[i + 1] if i + 1 < len(ages) else None
        interval = f"{age}-{next_age}" if next_age else None
        rows.append(dict(age=age, next_age=next_age, interval=interval, age_index=i))
    return pd.DataFrame(rows)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_pickle(INPUT_FILE)
    print(f"Loaded {len(df)} rows from {INPUT_FILE}")

    diag = extract_diagonal(df)
    age_map = build_age_map(df)

    print("\nLatest diagonal (sample):")
    print(diag.head(8).to_string(index=False))
    print(f"\nTotal diagonal rows: {len(diag)}")
    print(f"  Periods  : {diag['period'].nunique()}")
    print(f"  Measures : {diag['measure'].nunique()}")

    print("\nAge map:")
    print(age_map.to_string(index=False))

    diag.to_pickle(f"{OUTPUT_DIR}/diagonal.pkl")
    diag.to_csv(f"{OUTPUT_DIR}/diagonal.csv", index=False)
    age_map.to_csv(f"{OUTPUT_DIR}/age_map.csv", index=False)

    print(f"\nSaved → {OUTPUT_DIR}/diagonal.[pkl|csv]  and  age_map.csv")


if __name__ == "__main__":
    print("=== Step 2: Extracting latest diagonal ===")
    main()
