"""Validation utilities for triangle and related data."""

import pandas as pd
from typing import List, Optional

__all__ = [
    'validate_triangle_data',
    'validate_exposure_data',
    'validate_combined_data',
    'validate_prior_selections',
    'validate_expected_loss_rates'
]


def validate_triangle_data(df: pd.DataFrame) -> None:
    """Validate developing triangle data (Incurred Loss, Paid Loss, Reported Count, Closed Count).
    
    Raises ValueError if validation fails.
    
    For Exposure data, use validate_exposure_data() instead.
    For combined data with both triangles and exposure, use validate_combined_data().
    """
    errors = []
    
    if df.empty:
        raise ValueError("Triangle data validation failed!\n\nERRORS:\n  - DataFrame is empty")
    
    # Required columns and types
    required = {
        'period': 'category',
        'age': 'category',
        'value': 'numeric',
        'measure': 'category',
        'unit_type': 'category'
    }
    
    for col, expected_type in required.items():
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
        elif expected_type == 'category' and df[col].dtype.name != 'category':
            errors.append(f"'{col}' must be categorical")
        elif expected_type == 'numeric' and not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"'{col}' must be numeric")
    
    # Check for nulls in all critical columns (triangles develop over age)
    for col in ['period', 'age', 'value', 'measure']:
        if col in df.columns and df[col].isna().sum() > 0:
            errors.append(f"'{col}' contains {df[col].isna().sum()} null value(s)")
    
    # Check ordered categoricals
    for col in ['period', 'age']:
        if col in df.columns and df[col].dtype.name == 'category' and not df[col].cat.ordered:
            errors.append(f"'{col}' categorical must be ordered")
    
    # Check valid values
    if 'unit_type' in df.columns:
        valid_units = ['Count', 'Dollars']
        invalid = df[~df['unit_type'].isin(valid_units)]['unit_type'].unique()
        if len(invalid) > 0:
            errors.append(f"Invalid unit_type: {', '.join(map(str, invalid))}")
    
    if 'measure' in df.columns:
        valid_measures = ['Incurred Loss', 'Paid Loss', 'Reported Count', 'Closed Count']
        invalid = df[~df['measure'].isin(valid_measures)]['measure'].unique()
        if len(invalid) > 0:
            errors.append(f"Invalid measure: {', '.join(map(str, invalid))} (use validate_exposure_data for Exposure)")
    
    # Check duplicates
    if all(col in df.columns for col in ['source', 'period', 'age', 'measure']):
        dups = df.duplicated(subset=['source', 'period', 'age', 'measure'], keep=False)
        if dups.any():
            errors.append(f"Found {dups.sum()} duplicate source/period/age/measure combinations")
    
    if errors:
        raise ValueError("Triangle data validation failed!\n\nERRORS:\n" + "\n".join(f"  - {e}" for e in errors))


def validate_exposure_data(df: pd.DataFrame) -> None:
    """Validate exposure data format. Raises ValueError if validation fails.
    
    Exposure data requirements:
    - Required columns: period, value, measure, unit_type
    - age column is optional; if present, values can be None/null
    - period must be an ordered categorical
    - One value per period (no duplicates by source/period/measure)
    """
    errors = []
    
    if df.empty:
        raise ValueError("Exposure data validation failed!\n\nERRORS:\n  - DataFrame is empty")
    
    # Check measure is Exposure
    if 'measure' in df.columns:
        if not (df['measure'] == 'Exposure').all():
            non_exposure = df[df['measure'] != 'Exposure']['measure'].unique()
            errors.append(f"validate_exposure_data() expects only Exposure measure, found: {', '.join(map(str, non_exposure))}")
    
    # Required columns and types (age is not required for exposure)
    required = {
        'period': 'category',
        'value': 'numeric',
        'measure': 'category',
        'unit_type': 'category'
    }
    
    for col, expected_type in required.items():
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
        elif expected_type == 'category' and df[col].dtype.name != 'category':
            errors.append(f"'{col}' must be categorical")
        elif expected_type == 'numeric' and not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"'{col}' must be numeric")
    
    # Check for nulls in critical columns (age nulls are OK for exposure)
    for col in ['period', 'value', 'measure']:
        if col in df.columns and df[col].isna().sum() > 0:
            errors.append(f"'{col}' contains {df[col].isna().sum()} null value(s)")
    
    # Check period is ordered categorical
    if 'period' in df.columns and df['period'].dtype.name == 'category' and not df['period'].cat.ordered:
        errors.append("'period' categorical must be ordered")
    
    # If age column exists, it should be an ordered categorical (even if all values are None)
    if 'age' in df.columns and df['age'].dtype.name == 'category' and not df['age'].cat.ordered:
        errors.append("'age' categorical must be ordered (values can be None for Exposure)")
    
    # Check valid values
    if 'unit_type' in df.columns:
        valid_units = ['Count', 'Dollars']
        invalid = df[~df['unit_type'].isin(valid_units)]['unit_type'].unique()
        if len(invalid) > 0:
            errors.append(f"Invalid unit_type: {', '.join(map(str, invalid))}")
    
    # Check duplicates (by period only, age is irrelevant for exposure)
    if all(col in df.columns for col in ['source', 'period', 'measure']):
        dups = df.duplicated(subset=['source', 'period', 'measure'], keep=False)
        if dups.any():
            errors.append(f"Found {dups.sum()} duplicate source/period/measure combinations")
    
    if errors:
        raise ValueError("Exposure data validation failed!\n\nERRORS:\n" + "\n".join(f"  - {e}" for e in errors))


def validate_combined_data(df: pd.DataFrame) -> None:
    """Validate combined triangle and exposure data.
    
    Separates Exposure from triangle measures and validates each appropriately.
    """
    if df.empty:
        raise ValueError("Data validation failed!\n\nERRORS:\n  - DataFrame is empty")
    
    if 'measure' not in df.columns:
        raise ValueError("Data validation failed!\n\nERRORS:\n  - Missing required column: measure")
    
    # Separate exposure from triangles
    exposure = df[df['measure'] == 'Exposure']
    triangles = df[df['measure'] != 'Exposure']
    
    # Validate each separately
    if not triangles.empty:
        validate_triangle_data(triangles)
    
    if not exposure.empty:
        validate_exposure_data(exposure)


def validate_prior_selections(df: pd.DataFrame, triangle_data: pd.DataFrame) -> None:
    """Validate prior selections format and content."""
    errors = []
    
    if df.empty:
        return  # Empty is OK for optional data
    
    # Check required columns
    required = ['measure', 'interval', 'selection']
    for col in required:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
    
    # Check nulls and types
    for col in ['measure', 'interval']:
        if col in df.columns and df[col].isna().sum() > 0:
            errors.append(f"'{col}' contains {df[col].isna().sum()} null value(s)")
    
    if 'selection' in df.columns:
        if df['selection'].isna().sum() > 0:
            errors.append(f"'selection' contains {df['selection'].isna().sum()} null value(s)")
        if not pd.api.types.is_numeric_dtype(df['selection']):
            errors.append("'selection' must be numeric")
    
    if not errors:
        # Validate against triangle data
        valid_measures = triangle_data['measure'].cat.categories.tolist()
        invalid = df[~df['measure'].isin(valid_measures)]['measure'].unique()
        if len(invalid) > 0:
            errors.append(f"Invalid measures: {', '.join(invalid)}")
        
        # Check intervals
        age_cats = triangle_data['age'].cat.categories.tolist()
        valid_intervals = [f"{age_cats[i]}-{age_cats[i+1]}" for i in range(len(age_cats) - 1)]
        invalid = df[~df['interval'].isin(valid_intervals)]['interval'].unique()
        if len(invalid) > 0:
            errors.append(f"Invalid intervals: {', '.join(invalid)}")
        
        # Check duplicates
        dups = df.duplicated(subset=['measure', 'interval'], keep=False)
        if dups.any():
            errors.append(f"Found {dups.sum()} duplicate measure/interval combinations")
    
    if errors:
        raise ValueError("Prior selections validation failed!\n\nERRORS:\n" + "\n".join(f"  - {e}" for e in errors))


def validate_expected_loss_rates(df: pd.DataFrame, triangle_data: pd.DataFrame) -> None:
    """Validate expected loss rates format and content."""
    errors = []
    
    if df.empty:
        raise ValueError("Expected loss rates validation failed!\n\nERRORS:\n  - DataFrame is empty")
    
    # Check required columns
    required = ['period', 'expected_loss_rate', 'expected_freq']
    for col in required:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
    
    # Check types and nulls
    if 'expected_loss_rate' in df.columns:
        valid = df['expected_loss_rate'].dropna()
        if not valid.empty and not pd.api.types.is_numeric_dtype(valid):
            errors.append("'expected_loss_rate' must be numeric")
    
    if 'expected_freq' in df.columns:
        valid = df['expected_freq'].dropna()
        if not valid.empty and not pd.api.types.is_numeric_dtype(valid):
            errors.append("'expected_freq' must be numeric")
    
    if 'period' in df.columns and df['period'].isna().sum() > 0:
        errors.append(f"'period' contains {df['period'].isna().sum()} null value(s)")
    
    # Check that each row has at least one rate
    both_null = df[['expected_loss_rate', 'expected_freq']].isna().all(axis=1)
    if both_null.any():
        errors.append(f"Found {both_null.sum()} row(s) missing both rates")
    
    # Check duplicates
    if 'period' in df.columns:
        dups = df['period'].duplicated(keep=False)
        if dups.any():
            dup_periods = df[dups]['period'].unique()
            errors.append(f"Duplicate periods: {', '.join(map(str, dup_periods))}")
    
    # Validate periods match triangle
    if 'period' in df.columns and not df.empty:
        triangle_periods = set(triangle_data['period'].cat.categories.tolist())
        expected_periods = set(df['period'].astype(str).unique())
        
        extra = expected_periods - triangle_periods
        if extra:
            errors.append(f"Periods not in triangle data: {', '.join(sorted(extra))}")
        
        missing = triangle_periods - expected_periods
        if missing:
            print(f"  Note: {len(missing)} triangle period(s) have no expected loss rates")
    
    if errors:
        raise ValueError("Expected loss rates validation failed!\n\nERRORS:\n" + "\n".join(f"  - {e}" for e in errors))
    
    # Convert types
    triangle_period_cats = triangle_data['period'].cat.categories.tolist()
    valid_periods = [p for p in triangle_period_cats if p in df['period'].astype(str).values]
    
    df['period'] = pd.Categorical(df['period'].astype(str), categories=valid_periods, ordered=True)
    df['expected_loss_rate'] = df['expected_loss_rate'].astype(float)
    df['expected_freq'] = df['expected_freq'].astype(float)
    
    print(f"  Validated {len(df)} expected loss rate records")
