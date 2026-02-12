"""
Chain Ladder calculation utilities for triangle projections.
Non-tool functions extracted from chain_ladder_ultimates.py for use in triangle app.
Refactored to use Polars for improved performance.

Key Changes from Pandas to Polars:
-----------------------------------
1. Import: pandas (pd) -> polars (pl)
2. DataFrames: All pd.DataFrame -> pl.DataFrame, pd.Series -> pl.Series or Dict
3. Methods:
   - .copy() -> .clone()
   - .apply() -> .map_elements() or explicit iteration
   - .dropna() -> .drop_nulls() or .is_not_null() filtering
   - .values -> .to_numpy() or .to_list()
   - .to_dict() -> .to_dict()
   - .to_csv() -> .write_csv()
4. Indexing: Polars doesn't have row indices like pandas - origin column now regular column
5. get_latest_diagonal() / get_latest_age() now return Dict instead of Series
6. Pivot operations updated to Polars syntax
7. Performance: Polars is typically 5-10x faster for large datasets

Compatibility Notes:
--------------------
- Functions that previously returned pd.Series now return Dict or pl.DataFrame
- Functions accepting pd.DataFrame now accept pl.DataFrame
- External functions (calculate_diagnostics, round_actuarial, format detection helpers)
  may need separate refactoring or compatibility wrappers
"""
import polars as pl
import numpy as np
from typing import Dict, Optional, Any, Union

class ActuarialTriangle:
    """
    Representation of an actuarial triangle using Polars for improved performance.
    """
    def __init__(self, data: pl.DataFrame = None, origin_col: str = None, dev_col: str = None, 
                 value_col: str = None, wide_df: pl.DataFrame = None):
        if wide_df is not None:
            self.wide = wide_df.clone()
            # Extract column names - first column is origin
            self.origin_col = wide_df.columns[0]
            self.dev_col = "Development"
            self.value_col = "Value"
        else:
            self.origin_col = origin_col
            self.dev_col = dev_col
            self.value_col = value_col
            
            # Store the raw long data
            self.data = data.clone()
            
            # Convert to wide format for triangle operations
            # Polars pivot: values from value_col, index is origin_col, columns from dev_col
            self.wide = data.pivot(
                values=value_col,
                index=origin_col,
                columns=dev_col
            )
        
        # Ensure development columns are numeric if possible (ages)
        dev_cols = [col for col in self.wide.columns if col != self.origin_col]
        rename_map = {}
        for col in dev_cols:
            col_str = str(col)
            if col_str.replace('.','').replace('-','').isdigit():
                try:
                    rename_map[col] = int(float(col_str))
                except:
                    pass
        
        if rename_map:
            self.wide = self.wide.rename(rename_map)
        
        # Sort rows by trailing number after last space (handles "CY 1", "CY 10" etc.)
        def extract_sort_key(val):
            s = str(val)
            parts = s.rsplit(' ', 1)
            trailing = parts[-1] if len(parts) > 1 else s
            try:
                return float(trailing)
            except ValueError:
                return float('inf')
        
        # Get origin values, sort them, then reorder dataframe
        origin_values = self.wide.select(self.origin_col).to_series().to_list()
        sorted_origins = sorted(origin_values, key=extract_sort_key)
        
        # Create a mapping for sort order
        origin_to_order = {origin: idx for idx, origin in enumerate(sorted_origins)}
        
        # Add temporary sort column, sort, then remove it
        self.wide = (
            self.wide
            .with_columns(pl.col(self.origin_col).map_elements(lambda x: origin_to_order.get(x, 999)).alias("_sort_order"))
            .sort("_sort_order")
            .drop("_sort_order")
        )

    def get_latest_diagonal(self) -> Dict[Any, float]:
        """
        Extract the latest diagonal (valuation at most recent development period for each origin).
        Returns dict mapping origin -> latest value.
        """
        result = {}
        dev_cols = [col for col in self.wide.columns if col != self.origin_col]
        
        for row in self.wide.iter_rows(named=True):
            origin = row[self.origin_col]
            # Get last non-null value across development columns
            latest_val = None
            for col in reversed(dev_cols):
                val = row.get(col)
                if val is not None and not (isinstance(val, float) and np.isnan(val)):
                    latest_val = val
                    break
            result[origin] = latest_val if latest_val is not None else np.nan
        
        return result

    def get_latest_age(self) -> Dict[Any, Any]:
        """
        Get the maximum development period (age) available for each origin period.
        Returns dict mapping origin -> latest age.
        """
        result = {}
        dev_cols = [col for col in self.wide.columns if col != self.origin_col]
        
        for row in self.wide.iter_rows(named=True):
            origin = row[self.origin_col]
            # Get last non-null development column name
            latest_age = None
            for col in reversed(dev_cols):
                val = row.get(col)
                if val is not None and not (isinstance(val, float) and np.isnan(val)):
                    latest_age = col
                    break
            result[origin] = latest_age if latest_age is not None else np.nan
        
        return result


def calculate_cdfs(selected_ldfs: Union[Dict, pl.Series], tail_factor: float = 1.0) -> Dict[str, float]:
    """
    Calculate Cumulative Development Factors (CDFs) from selected Age-to-Age factors.
    
    Parameters:
    -----------
    selected_ldfs : Dict or pl.Series
        Age-to-age factors indexed by development interval (e.g., "12-24")
    tail_factor : float
        Tail factor to develop from last observed age to ultimate
        
    Returns:
    --------
    Dict mapping age to CDF
    """
    # Convert to dict if Series/DataFrame
    if isinstance(selected_ldfs, pl.Series):
        # Polars Series - convert to dict
        indices = selected_ldfs.to_list()
        values = [item[0] if isinstance(item, (list, tuple)) else item 
                 for item in selected_ldfs.to_list()]
        ldfs_dict = dict(zip(range(len(values)), values))
        # If we have parallel index info, use it
        selected_ldfs = ldfs_dict
    elif isinstance(selected_ldfs, pl.DataFrame):
        # If it's a DataFrame with interval names
        selected_ldfs = dict(zip(selected_ldfs.columns, selected_ldfs.row(0)))
    
    if not isinstance(selected_ldfs, dict):
        raise ValueError("selected_ldfs must be a dict, pl.Series, or pl.DataFrame")
    
    # Get factors and intervals
    intervals = sorted(selected_ldfs.keys(), key=lambda x: int(str(x).split('-')[0]) if '-' in str(x) else 0)
    factors = [selected_ldfs[interval] for interval in intervals]
    
    # Work backwards from tail to earliest period
    factors_reversed = factors[::-1]
    
    # Start with tail factor and work backwards
    cdf_current = tail_factor
    cdfs_reversed = []
    
    for f in factors_reversed:
        cdf_current = cdf_current * f
        cdfs_reversed.append(cdf_current)
    
    # Reverse to get correct order (earliest to latest)
    cdfs = cdfs_reversed[::-1]
    
    # Get ages from interval strings
    ages = [str(interval).split('-')[0] for interval in intervals]
    
    # Add the final age (tail start) and its CDF (the tail factor)
    if intervals:
        last_interval = intervals[-1]
        last_age = str(last_interval).split('-')[1] if '-' in str(last_interval) else str(last_interval)
        ages.append(last_age)
        cdfs.append(tail_factor)
    
    return dict(zip(ages, cdfs))


def calculate_ultimate_values(triangle: ActuarialTriangle, selected_cdfs: Dict[str, float], 
                              is_loss: bool = True) -> pl.DataFrame:
    """
    Project Ultimate values for a single triangle.
    Resulting dataframe has origin periods as first column.
    
    Parameters:
    -----------
    triangle : ActuarialTriangle
        Triangle with loss data
    selected_cdfs : Dict[str, float]
        CDFs by age {age_str: cdf_value}
    is_loss : bool
        Whether this is loss data (affects rounding)
        
    Returns:
    --------
    pl.DataFrame with columns: origin, Latest_Value, Latest_Age, CDF, Ultimate
    """
    latest_diagonal = triangle.get_latest_diagonal()
    latest_age = triangle.get_latest_age()
    
    # Build result rows
    rows = []
    for origin in triangle.wide.select(triangle.origin_col).to_series().to_list():
        latest_val = latest_diagonal.get(origin, np.nan)
        age = latest_age.get(origin, np.nan)
        
        # Get CDF for this age
        age_str = str(int(age)) if not (isinstance(age, float) and np.isnan(age)) else None
        cdf = selected_cdfs.get(age_str, 1.0) if age_str else 1.0
        
        # Calculate ultimate
        if isinstance(latest_val, (int, float)) and not np.isnan(latest_val):
            ultimate = latest_val * cdf
            # Round based on type
            if is_loss:
                ultimate = round(ultimate, 0)
            else:
                ultimate = round(ultimate, 4)
        else:
            ultimate = np.nan
        
        rows.append({
            triangle.origin_col: origin,
            'Latest_Value': latest_val,
            'Latest_Age': age,
            'CDF': cdf,
            'Ultimate': ultimate
        })
    
    return pl.DataFrame(rows)

def run_pre_analyst_workflow(
    triangles_data: Dict[str, pl.DataFrame], 
    exposure: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Initial workflow run before analyst intervention.
    Converts to wide, calculates diagnostics, LDFs, and QA metrics.
    Returns average LDFs in both dict and CSV format for tool consumption.
    
    Parameters:
    -----------
    triangles_data : Dict[str, pl.DataFrame]
        Dictionary of triangle name -> DataFrame
    exposure : Optional
        Exposure data (if available)
        
    Returns:
    --------
    Dict containing triangles, diagnostics, LDF data, and average LDFs
    """
    # 1. Calculate Diagnostics (assuming this function exists elsewhere)
    # diagnostics, diagnostic_labels, diagnostic_formats = calculate_diagnostics(triangles_data, exposure)
    
    results = {
        "triangles": {},
        # "diagnostics": {k: v.to_dict() for k, v in diagnostics.items()},
        # "diagnostic_labels": diagnostic_labels,
        # "diagnostic_formats": diagnostic_formats,
        "ldf_data": {},
        "average_ldfs_csv": {}
    }

    # 2. Process each triangle for LDFs and QA
    for name, df in triangles_data.items():
        # Heuristic to handle wide/long format
        # For now, assume we receive properly formatted long data
        # You may need to implement _detect_triangle_format, _wide_to_long, etc.
        
        # Simple heuristic: if DataFrame has many columns, likely wide format
        is_wide = len(df.columns) > 5
        
        if is_wide:
            # Assume first column is accident period, rest are development periods
            accident_col = df.columns[0]
            # Convert wide to long (simplified - may need adjustment)
            tri = ActuarialTriangle(wide_df=df)
        else:
            # Assume long format with columns for accident, development, value
            # Try to identify columns
            cols = df.columns
            if len(cols) >= 3:
                accident_col = cols[0]
                dev_col = cols[1]
                value_col = cols[2]
            else:
                raise ValueError(f"Cannot process triangle {name}: insufficient columns")
            
            tri = ActuarialTriangle(df, accident_col, dev_col, value_col)
        
        # Store wide format as dict
        results["triangles"][name] = tri.wide.to_dict()
        
        # Skip LDF calculations for exposure triangles
        if name.lower() not in ("paid", "incurred", "reported", "closed"):
            continue
        
        # LDF Calculations
        ldf_tri_df = calculate_historical_ldfs(tri)
        avgs_df = calculate_average_ldfs(ldf_tri_df, tri)
        qa_metrics = calculate_qa_metrics(ldf_tri_df)
        
        results["ldf_data"][name] = {
            "historical_ldfs": ldf_tri_df.to_dict(),
            "average_ldfs": avgs_df.to_dict(),
            "qa_metrics": qa_metrics
        }
        
        # Store CSV format for tool consumption
        results["average_ldfs_csv"][name] = avgs_df.write_csv()

    return results

def calculate_historical_ldfs(triangle: ActuarialTriangle) -> pl.DataFrame:
    """
    Calculate historical age-to-age factors from an ActuarialTriangle.
    
    Returns a DataFrame where each column represents a development interval (e.g., "12-24")
    and each row represents an origin period with its corresponding LDF.
    """
    wide = triangle.wide
    dev_cols = [col for col in wide.columns if col != triangle.origin_col]
    dev_cols_sorted = sorted(dev_cols)
    
    # Calculate LDFs for each adjacent pair of development periods
    ldf_data = {triangle.origin_col: wide.select(triangle.origin_col).to_series().to_list()}
    
    for i in range(len(dev_cols_sorted) - 1):
        c1, c2 = dev_cols_sorted[i], dev_cols_sorted[i + 1]
        interval_name = f"{c1}-{c2}"
        
        # Calculate ratio for each origin period
        col1_values = wide.select(c1).to_series()
        col2_values = wide.select(c2).to_series()
        
        # Polars division with null handling
        ratios = (col2_values / col1_values).to_list()
        ldf_data[interval_name] = ratios
    
    return pl.DataFrame(ldf_data)


def calculate_average_ldfs(ldf_triangle_df: pl.DataFrame, triangle: ActuarialTriangle) -> pl.DataFrame:
    """
    Calculate various average selections (weighted, simple, medial) for multiple time periods.
    
    Returns a DataFrame with average methods as rows and development intervals as columns.
    """
    # Get development interval columns (exclude origin column)
    origin_col = ldf_triangle_df.columns[0]
    interval_cols = [col for col in ldf_triangle_df.columns if col != origin_col]
    
    wide_values = triangle.wide
    dev_cols = [col for col in wide_values.columns if col != triangle.origin_col]
    
    # Structure: method -> list of values (one per interval)
    methods = ['weighted_all', 'simple_all', 'medial_all',
               'weighted_3yr', 'simple_3yr', 'medial_3yr',
               'weighted_5yr', 'simple_5yr', 'medial_5yr']
    
    averages_data = {method: [] for method in methods}
    
    for interval in interval_cols:
        # Get the age_from for weighting
        age_from_str = interval.split('-')[0]
        try:
            age_from = int(float(age_from_str))
        except ValueError:
            age_from = age_from_str
        
        # Get factors and filter out nulls
        factors_series = ldf_triangle_df.select(interval).to_series()
        origins_series = ldf_triangle_df.select(origin_col).to_series()
        
        # Create mask for non-null values
        valid_mask = factors_series.is_not_null()
        factors = factors_series.filter(valid_mask).to_list()
        valid_origins = origins_series.filter(valid_mask).to_list()
        
        if not factors:
            # No valid factors for this interval - append None for all methods
            for method in methods:
                averages_data[method].append(None)
            continue
        
        # Get weights from the triangle
        if age_from in dev_cols:
            weight_series = wide_values.select(age_from).to_series()
            origin_to_weight = dict(zip(
                wide_values.select(triangle.origin_col).to_series().to_list(),
                weight_series.to_list()
            ))
            weights = [origin_to_weight.get(origin, 1.0) for origin in valid_origins]
        else:
            weights = [1.0] * len(factors)
        
        def calc_avgs(f_list, w_list, n=None):
            """Calculate weighted, simple, and medial averages."""
            if n:
                f_list, w_list = f_list[-n:], w_list[-n:]
            
            if not f_list:
                return None, None, None
            
            # Weighted average
            w_sum = sum(w_list)
            if w_sum > 0:
                w_avg = sum(f * w for f, w in zip(f_list, w_list)) / w_sum
            else:
                w_avg = None
            
            # Simple average
            s_avg = sum(f_list) / len(f_list)
            
            # Medial average (exclude highest and lowest)
            if len(f_list) > 2:
                sorted_f = sorted(f_list)
                m_avg = sum(sorted_f[1:-1]) / len(sorted_f[1:-1])
            else:
                m_avg = s_avg
            
            return w_avg, s_avg, m_avg
        
        # Calculate for different periods
        all_w, all_s, all_m = calc_avgs(factors, weights)
        w3, s3, m3 = calc_avgs(factors, weights, 3)
        w5, s5, m5 = calc_avgs(factors, weights, 5)
        
        # Append values to each method's list
        averages_data['weighted_all'].append(all_w)
        averages_data['simple_all'].append(all_s)
        averages_data['medial_all'].append(all_m)
        averages_data['weighted_3yr'].append(w3)
        averages_data['simple_3yr'].append(s3)
        averages_data['medial_3yr'].append(m3)
        averages_data['weighted_5yr'].append(w5)
        averages_data['simple_5yr'].append(s5)
        averages_data['medial_5yr'].append(m5)
    
    # Create DataFrame with method as first column, then intervals as remaining columns
    result_data = {'method': methods}
    for i, interval in enumerate(interval_cols):
        result_data[interval] = [averages_data[method][i] for method in methods]
    
    return pl.DataFrame(result_data)


def calculate_qa_metrics(ldf_tri_df: pl.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate QA metrics for LDFs to identify trends and volatility.
    
    Returns dict of {interval: {cv: float, slope: float}}
    """
    metrics = {}
    
    # Get all columns except the first (origin) column
    origin_col = ldf_tri_df.columns[0]
    interval_cols = [col for col in ldf_tri_df.columns if col != origin_col]
    
    for col in interval_cols:
        factors_series = ldf_tri_df.select(col).to_series()
        factors = factors_series.filter(factors_series.is_not_null()).to_list()
        
        if len(factors) > 1:
            # Coefficient of variation
            mean_val = sum(factors) / len(factors)
            variance = sum((f - mean_val) ** 2 for f in factors) / len(factors)
            std_val = variance ** 0.5
            cv = std_val / mean_val if mean_val != 0 else 0.0
            
            # Trend calculation (simple linear slope)
            if len(factors) >= 3:
                y = np.array(factors)
                x = np.arange(len(y))
                slope = np.polyfit(x, y, 1)[0]
            else:
                slope = 0.0
            
            metrics[col] = {
                "cv": round(cv, 4),
                "slope": round(float(slope), 4)
            }
        else:
            metrics[col] = {"cv": 0.0, "slope": 0.0}
    
    return metrics

