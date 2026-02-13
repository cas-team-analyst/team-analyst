"""
Extract Triangle Data and Run Chain Ladder Analysis

TEMPLATE SCRIPT - Copy and adapt this for your project's data source.

This script demonstrates how to:
1. Extract all triangles from a data source (Excel example shown)
2. Load them into ActuarialTriangle objects
3. Perform chain ladder analysis on each
4. Generate CSV files for review

Modify the following for your project:
- EXCEL_FILE: Path to your data source
- SHEET_MAP: Map your source names to triangle names
- load_triangle_from_excel(): Adapt to match your data format
"""
import sys
import pandas as pd
from pathlib import Path

# Add skill directory to path
# If copying this template, you may need to adjust this path
skill_path = Path(__file__).parent.parent.parent / ".claude" / "skills" / "chain-ladder-method"
if not skill_path.exists():
    # Alternative: assume script is already in the skill folder
    skill_path = Path(__file__).parent
sys.path.insert(0, str(skill_path))

from chain_ladder_functions import perform_full_analysis


# ==============================================================================
# CONFIGURATION - Modify these for your data source
# ==============================================================================

EXCEL_FILE = "data/Triangle Examples 1.xlsx"

# Map sheet names to triangle names
SHEET_MAP = {
    'Paid 1': 'Paid Losses',
    'Inc 1': 'Incurred Losses',
    # 'Ct 1': 'Reported Counts',  # Different format, skip for now
}

# ==============================================================================
# DATA EXTRACTION FUNCTIONS
# ==============================================================================

def load_triangle_from_excel(file_path: str, sheet_name: str) -> pd.DataFrame:
    """
    Load a triangle from Excel file.
    Expected format:
    - First row contains age headers (development periods)
    - First column contains accident years
    - Values are in the grid
    
    Returns:
        Wide DataFrame with periods as index, ages as columns
    """
    print(f"\nLoading {sheet_name} from {file_path}...")
    
    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    print(f"Raw shape: {df.shape}")
    print(f"First few rows:\n{df.head()}\n")
    
    # First row should contain the age headers - let's check
    # Column 0 name is usually something like "Age of Evaluation"
    # Row 0 contains "Accident Year" in col 0 and ages in other columns
    
    # Get the header row (row 0)
    header_row = df.iloc[0]
    
    # First value should be something like "Accident Year"
    origin_label = header_row.iloc[0]
    print(f"Origin label: {origin_label}")
    
    # Rest are ages
    ages = []
    for val in header_row.iloc[1:]:
        if pd.notna(val):
            try:
                ages.append(int(float(val)))
            except:
                print(f"Warning: Could not convert age '{val}' to int")
                ages.append(val)
    
    print(f"Ages found: {ages[:5]}... (total: {len(ages)})")
    
    # Now get the data rows (skip row 0)
    data_df = df.iloc[1:].reset_index(drop=True)
    
    # First column is origin periods (accident years)
    origin_col_name = df.columns[0]
    origins = data_df[origin_col_name].astype(int).tolist()
    print(f"Origin periods: {origins[:5]}... (total: {len(origins)})")
    
    # Create wide dataframe
    # Use ages as column names
    value_cols = df.columns[1:]  # Skip first column
    wide_data = data_df[value_cols].values
    
    # Create proper dataframe
    wide_df = pd.DataFrame(
        wide_data,
        index=origins,
        columns=ages
    )
    
    # Set names
    wide_df.index.name = "Accident Year"
    wide_df.columns.name = "Development Age"
    
    print(f"Wide triangle shape: {wide_df.shape}")
    print(f"Triangle preview:\n{wide_df.iloc[:5, :5]}\n")
    
    return wide_df


# ==============================================================================
# MAIN WORKFLOW
# ==============================================================================

def extract_all_triangles():
    """Extract all triangles from the data source."""
    print(f"\n{'='*70}")
    print("STEP 1: EXTRACTING ALL TRIANGLE DATA")
    print(f"{'='*70}\n")
    
    triangles = {}
    xl = pd.ExcelFile(EXCEL_FILE)
    print(f"Available sheets: {xl.sheet_names}\n")
    
    for sheet_name, triangle_name in SHEET_MAP.items():
        try:
            print(f"Loading {triangle_name} from '{sheet_name}'...")
            triangle_df = load_triangle_from_excel(EXCEL_FILE, sheet_name)
            triangles[triangle_name] = triangle_df
            print(f"✓ {triangle_name}: {triangle_df.shape[0]} periods × {triangle_df.shape[1]} ages\n")
        except Exception as e:
            print(f"✗ Error loading {triangle_name}: {e}\n")
            continue
    
    print(f"Successfully extracted {len(triangles)} triangles\n")
    return triangles


def analyze_triangle(triangle_name: str, triangle_df: pd.DataFrame):
    """Perform chain ladder analysis on a single triangle."""
    print(f"\n{'='*70}")
    print(f"ANALYZING: {triangle_name}")
    print(f"{'='*70}\n")
    
    try:
        csv_path = perform_full_analysis(
            triangle_df=triangle_df,
            triangle_name=triangle_name,
            processed_dir="output/processed",
            selections_dir="output/selections"
        )
        print(f"\n✓ Success! CSV saved to: {csv_path}\n")
        return csv_path
    except Exception as e:
        print(f"\n✗ Error analyzing {triangle_name}:")
        print(f"  {type(e).__name__}: {e}\n")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main workflow: extract all data, then analyze each triangle."""
    
    # Step 1: Extract all triangle data (one time)
    triangles = extract_all_triangles()
    
    if not triangles:
        print("No triangles were successfully extracted. Exiting.")
        return
    
    # Step 2: Analyze each triangle
    print(f"\n{'='*70}")
    print("STEP 2: PERFORMING CHAIN LADDER ANALYSIS")
    print(f"{'='*70}")
    
    results = {}
    for triangle_name, triangle_df in triangles.items():
        csv_path = analyze_triangle(triangle_name, triangle_df)
        if json_path:
            results[triangle_name] = json_path
    
    # Summary
    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*70}\n")
    print(f"Successfully analyzed {len(results)}/{len(triangles)} triangles:\n")
    for name, path in results.items():
        filename = name.lower().replace(' ', '_')
        print(f"  ✓ {name}")
        print(f"    Selections: {path}")
        print(f"    Triangle: output/processed/{filename}_triangle.csv")
        print(f"    Next: python output/scripts/populate_selections.py --csv {path}\n")
    
    print(f"\nTo review reports:")
    print(f"  1. Copy populate_selections.py to output/scripts/ if needed")
    print(f"  2. Run populate script for each triangle")
    print(f"  3. Start: npx vite --port 5175")
    print(f"  4. View: http://localhost:5175/output/selections/[trianglename]_selections.html\n")
    
    print(f"\n{'='*70}")
    print("Analysis complete!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
