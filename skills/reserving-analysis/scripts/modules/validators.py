"""Validation utilities for triangle and related data."""

import pandas as pd
from typing import List, Optional


def validate_triangle_data(df: pd.DataFrame) -> None:
    """Validate triangle data format. Raises ValueError if validation fails.
    
    Special handling for Exposure:
    - Exposure measure can have null/placeholder ages since it doesn't develop over time
    - Downstream scripts only use the most recent exposure value per period (diagonal)
    """
    errors = []
    
    if df.empty:
        raise ValueError("Data validation failed!\n\nERRORS:\n  - DataFrame is empty")
    
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
    
    # Check for nulls in critical columns (excluding age for Exposure measure)
    for col in ['period', 'value', 'measure']:
        if col in df.columns and df[col].isna().sum() > 0:
            errors.append(f"'{col}' contains {df[col].isna().sum()} null value(s)")
    
    # Check age nulls only for non-Exposure measures
    if 'age' in df.columns and 'measure' in df.columns:
        non_exposure = df[df['measure'] != 'Exposure']
        if not non_exposure.empty:
            age_nulls = non_exposure['age'].isna().sum()
            if age_nulls > 0:
                errors.append(f"'age' contains {age_nulls} null value(s) in non-Exposure measures")
    
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
        valid_measures = ['Incurred Loss', 'Paid Loss', 'Reported Count', 'Closed Count', 'Exposure']
        invalid = df[~df['measure'].isin(valid_measures)]['measure'].unique()
        if len(invalid) > 0:
            errors.append(f"Invalid measure: {', '.join(map(str, invalid))}")
    
    # Check duplicates (only for measures that have meaningful ages)
    if all(col in df.columns for col in ['source', 'period', 'age', 'measure']):
        # For non-Exposure measures, check duplicates
        non_exposure = df[df['measure'] != 'Exposure']
        if not non_exposure.empty:
            dups = non_exposure.duplicated(subset=['source', 'period', 'age', 'measure'], keep=False)
            if dups.any():
                errors.append(f"Found {dups.sum()} duplicate source/period/age/measure combinations (non-Exposure)")
        
        # For Exposure, check period duplicates only
        exposure = df[df['measure'] == 'Exposure']
        if not exposure.empty:
            dups = exposure.duplicated(subset=['source', 'period', 'measure'], keep=False)
            if dups.any():
                errors.append(f"Found {dups.sum()} duplicate source/period/measure combinations for Exposure")
    
    if errors:
        raise ValueError("Data validation failed!\n\nERRORS:\n" + "\n".join(f"  - {e}" for e in errors))


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
