"""
Actuarial calculation functions with proper NaN/None handling.

All functions sanitize inputs to handle NaN, None, and 0 values consistently.
Returns None when inputs are invalid or calculations cannot be performed.
"""

import pandas as pd


def sanitize_value(val):
    """
    Convert NaN/None to None consistently for safe calculations.
    
    Args:
        val: Any value (could be NaN, None, or numeric)
        
    Returns:
        None if val is NaN or None, otherwise val
    """
    return val if pd.notna(val) else None


def calc_cl_ultimate(actual, cdf):
    """
    Chain Ladder ultimate = actual * cdf
    
    Args:
        actual: Current actual value
        cdf: Cumulative Development Factor
        
    Returns:
        Ultimate value or None if inputs invalid
    """
    actual = sanitize_value(actual)
    cdf = sanitize_value(cdf)
    if actual is not None and cdf is not None:
        return actual * cdf
    return None


def calc_bf_pct_unreported(cdf):
    """
    Bornhuetter-Ferguson % unreported = 1 - (1/cdf)
    
    Args:
        cdf: Cumulative Development Factor
        
    Returns:
        Percent unreported or None if cdf invalid or zero
    """
    cdf = sanitize_value(cdf)
    if cdf is not None and cdf != 0:
        return 1 - (1 / cdf)
    return None


def calc_bf_unreported(ie, pct_unreported):
    """
    BF unreported = IE * % unreported
    
    Args:
        ie: Initial Expected value
        pct_unreported: Percent unreported (from calc_bf_pct_unreported)
        
    Returns:
        Unreported amount or None if inputs invalid
    """
    ie = sanitize_value(ie)
    pct = sanitize_value(pct_unreported)
    if ie is not None and pct is not None:
        return ie * pct
    return None


def calc_bf_ultimate(unreported, actual):
    """
    BF ultimate = unreported + actual
    
    Args:
        unreported: Unreported amount (from calc_bf_unreported)
        actual: Current actual value
        
    Returns:
        Ultimate value or None if inputs invalid
    """
    unrep = sanitize_value(unreported)
    act = sanitize_value(actual)
    if unrep is not None and act is not None:
        return unrep + act
    return None


def calc_ibnr(ultimate, actual, measure, combined_df=None, period=None):
    """
    Calculate IBNR with special handling for Paid measures.
    
    For Paid Loss: IBNR = Ultimate - Incurred (not Ultimate - Paid)
    For others: IBNR = Ultimate - Actual
    
    Args:
        ultimate: Ultimate loss value
        actual: Current actual value
        measure: Measure name (e.g., "Paid Loss", "Incurred Loss")
        combined_df: DataFrame with all measures (required for Paid Loss)
        period: Accident period (required for Paid Loss)
        
    Returns:
        IBNR value or None if inputs invalid
    """
    ultimate = sanitize_value(ultimate)
    actual = sanitize_value(actual)
    
    if ultimate is None:
        return None
    
    if measure == "Paid Loss":
        # Need to lookup Incurred from combined dataframe
        if combined_df is None or period is None:
            return None
        
        # Get incurred value for this period
        inc_row = combined_df[(combined_df["measure"] == "Incurred Loss") & 
                             (combined_df["period"] == period)]
        if len(inc_row) > 0:
            incurred = sanitize_value(inc_row["actual"].iloc[0])
            if incurred is not None:
                return ultimate - incurred
        return None
    else:
        # Standard IBNR = Ultimate - Actual
        if actual is not None:
            return ultimate - actual
        return None


def calc_ie_loss_rate(ie_ultimate, exposure):
    """
    IE loss rate = IE ultimate / exposure
    
    Args:
        ie_ultimate: Initial Expected ultimate value
        exposure: Exposure amount
        
    Returns:
        Loss rate or None if inputs invalid or exposure is zero
    """
    ie = sanitize_value(ie_ultimate)
    exp = sanitize_value(exposure)
    if ie is not None and exp is not None and exp != 0:
        return ie / exp
    return None


def safe_divide(numerator, denominator):
    """
    Safe division with NaN handling.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        
    Returns:
        Division result or None if inputs invalid or denominator is zero
    """
    num = sanitize_value(numerator)
    den = sanitize_value(denominator)
    if num is not None and den is not None and den != 0:
        return num / den
    return None


def calc_total_ibnr(total_ultimate, total_actual, measure, combined_df=None):
    """
    Calculate total IBNR with special handling for Paid measures.
    
    For Paid Loss: Total IBNR = Total Ultimate - Total Incurred
    For others: Total IBNR = Total Ultimate - Total Actual
    
    Args:
        total_ultimate: Sum of ultimate values
        total_actual: Sum of actual values
        measure: Measure name (e.g., "Paid Loss", "Incurred Loss")
        combined_df: DataFrame with all measures (required for Paid Loss)
        
    Returns:
        Total IBNR value
    """
    if measure == "Paid Loss":
        # For Paid: Total IBNR = Total Ultimate - Total Incurred
        if combined_df is None:
            return total_ultimate - total_actual
        
        inc_data = combined_df[combined_df["measure"] == "Incurred Loss"]
        total_incurred = inc_data["actual"].sum() if len(inc_data) > 0 else 0
        total_incurred = total_incurred if pd.notna(total_incurred) else 0
        return total_ultimate - total_incurred
    else:
        # For other measures: Total IBNR = Total Ultimate - Total Actual
        return total_ultimate - total_actual
