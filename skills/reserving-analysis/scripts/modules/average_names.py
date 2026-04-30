# Shared average name display mapping for LDF average columns.
# Used by chainladder-create-excel.py and analysis-create-excel.py.

AVERAGE_DISPLAY_NAMES = {
    # Exclude High/Low
    'avg_exclude_high_low_all': 'Exclude High/Low - All Years',
    'exclude_high_low_all': 'Exclude High/Low - All Years',
    'avg_exclude_high_low_5yr': 'Exclude High/Low - 5 Years',
    'exclude_high_low_5yr': 'Exclude High/Low - 5 Years',
    'avg_exclude_high_low_10yr': 'Exclude High/Low - 10 Years',
    'exclude_high_low_10yr': 'Exclude High/Low - 10 Years',
    
    # Simple averages
    'simple_all': 'Average - All Years',
    'simple_3yr': 'Average - 3 Years',
    'simple_5yr': 'Average - 5 Years',
    'simple_10yr': 'Average - 10 Years',
    
    # Weighted averages
    'weighted_all': 'Weighted Average - All Years',
    'weighted_3yr': 'Weighted Average - 3 Years',
    'weighted_5yr': 'Weighted Average - 5 Years',
    'weighted_10yr': 'Weighted Average - 10 Years',
    
    # Min/Max
    'min_all': 'Min - All Years',
    'max_all': 'Max - All Years',
    
    # Coefficient of Variation
    'cv_3yr': 'CV - 3 Years',
    'cv_5yr': 'CV - 5 Years',
    'cv_10yr': 'CV - 10 Years',
    
    # Slope
    'slope_3yr': 'Slope - 3 Years',
    'slope_5yr': 'Slope - 5 Years',
    'slope_10yr': 'Slope - 10 Years',
}


def pretty_average_name(col_name):
    """
    Convert average column name to pretty display name.
    
    Args:
        col_name: Raw column name (e.g., 'simple_3yr', 'avg_exclude_high_low_5yr')
    
    Returns:
        Pretty display name (e.g., 'Average - 3 Years', 'Exclude High/Low - 5 Years')
    """
    if col_name in AVERAGE_DISPLAY_NAMES:
        return AVERAGE_DISPLAY_NAMES[col_name]
    
    # Fallback for unmapped names
    return col_name.replace('avg_exclude_high_low', 'exclude_high_low')
