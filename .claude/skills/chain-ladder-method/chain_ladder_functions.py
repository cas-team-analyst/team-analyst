import pandas as pd
import numpy as np
from typing import Dict, Optional, Any, List
from pathlib import Path

# Triangle data is stored as wide DataFrames:
# - Index: periods (accident years, origin periods, etc.)
# - Columns: development ages (12, 24, 36, etc.)
# - Values: loss amounts, counts, etc.
# - Use pd.read_csv(path, index_col=0) to load from CSV

def _detect_triangle_format(df: pd.DataFrame) -> str:
    """
    Detect whether a DataFrame is in wide or long format.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        "wide" or "long"
    """
    # Heuristic: wide format typically has numeric columns (ages) and fewer rows than columns
    # Long format typically has columns like accident_period, development_period, value
    
    if len(df.columns) <= 3:
        return "long"
    
    # Check if most columns are numeric (typical of wide triangle format)
    numeric_cols = sum(1 for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) or str(col).replace('.', '').isdigit())
    if numeric_cols > len(df.columns) * 0.7:
        return "wide"
    
    # Check for common long format column names
    col_names_lower = [str(col).lower() for col in df.columns]
    long_indicators = ["accident", "development", "origin", "period", "age", "value", "loss", "count"]
    if any(indicator in " ".join(col_names_lower) for indicator in long_indicators):
        return "long"
    
    # Default to wide if uncertain
    return "wide"

def _find_long_format_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Find the column names for accident period, development period, and value in a long format DataFrame.
    
    Args:
        df: DataFrame in long format
        
    Returns:
        Dict with keys "accident", "development", "value"
    """
    cols = df.columns.tolist()
    col_names_lower = [str(col).lower() for col in cols]
    
    # Find accident period column
    accident_col = None
    for i, col_name in enumerate(col_names_lower):
        if any(term in col_name for term in ["accident", "origin", "ay", "period"]):
            accident_col = cols[i]
            break
    
    # Find development period column  
    dev_col = None
    for i, col_name in enumerate(col_names_lower):
        if any(term in col_name for term in ["development", "dev", "age", "period"]) and cols[i] != accident_col:
            dev_col = cols[i]
            break
    
    # Find value column (often the last numeric column)
    value_col = None
    for col in reversed(cols):
        if col not in [accident_col, dev_col] and pd.api.types.is_numeric_dtype(df[col]):
            value_col = col
            break
    
    # Fallback to positional detection if named detection fails
    if not accident_col:
        accident_col = cols[0]
    if not dev_col:
        dev_col = cols[1] if len(cols) > 1 else cols[0]
    if not value_col:
        value_col = cols[-1] if len(cols) > 2 else "value"
    
    return {
        "accident": accident_col,
        "development": dev_col,
        "value": value_col
    }

def _wide_to_long(df: pd.DataFrame, value_name: str = "value") -> pd.DataFrame:
    """
    Convert a wide triangle DataFrame to long format.
    
    Args:
        df: Wide DataFrame with accident periods as index and development ages as columns
        value_name: Name for the value column in long format
        
    Returns:
        Long format DataFrame with accident_period, development_period, value columns
    """
    # Reset index to make accident period a column
    df_reset = df.reset_index()
    accident_col = df_reset.columns[0]
    
    # Melt the DataFrame
    long_df = df_reset.melt(
        id_vars=[accident_col],
        var_name="development_period", 
        value_name=value_name
    )
    
    # Rename accident column to standard name
    long_df = long_df.rename(columns={accident_col: "accident_period"})
    
    # Remove rows with NaN values
    long_df = long_df.dropna(subset=[value_name])
    
    return long_df


def calculate_diagnostics(triangles_data: Dict[str, pd.DataFrame], exposure: Optional[Any] = None) -> Dict[str, pd.DataFrame]:
    """
    Calculate actuarial diagnostics between multiple triangles using the registry.
    """
    # Broad name mapping
    name_map = {
        "incurred": "incurred",
        "paid": "paid",
        "reported": "reported_counts",
        "reported_counts": "reported_counts",
        "closed": "closed_counts",
        "closed_counts": "closed_counts",
        "counts": "reported_counts"
    }

    # Process dataframes to ensure they're in wide format for diagnostics
    triangles = {}
    for name, df in triangles_data.items():
        # Map name to standard key if possible
        std_name = name_map.get(name.lower(), name.lower())
        
        # Heuristic detection for diagnostic triangles which are often long but can be wide
        fmt = _detect_triangle_format(df)
        if fmt == "wide":
            # For wide format, prepare for direct use
            temp_df = df.copy()
            # If it has a RangeIndex (0, 1, 2...), the first column is likely the origin
            if isinstance(temp_df.index, pd.RangeIndex):
                origin_col = temp_df.columns[0]
                temp_df = temp_df.set_index(origin_col)
            processed_df = temp_df
        else:
            # Convert long to wide format
            cols = _find_long_format_columns(df)
            accident_col = cols["accident"]
            dev_col = cols["development"] 
            value_col = cols.get("value", "value")
            processed_df = df.pivot(index=accident_col, columns=dev_col, values=value_col)
        triangles[std_name] = processed_df

    # Handle exposure if it's a dataframe to be treated as a triangle
    processed_exposure = exposure
    if isinstance(exposure, pd.DataFrame):
        fmt = _detect_triangle_format(exposure)
        if fmt == "wide":
             # Use the raw wide dataframe directly for division
             processed_exposure = exposure.copy()
             if isinstance(processed_exposure.index, pd.RangeIndex):
                 origin_col = processed_exposure.columns[0]
                 processed_exposure = processed_exposure.set_index(origin_col)
             
             # Ensure numeric columns for alignment if possible
             processed_exposure.columns = [int(float(str(c).replace("Dev Pd ", "").replace("Age ", ""))) if str(c).replace('.','').isdigit() or "Dev Pd" in str(c) or "Age" in str(c) else c for c in processed_exposure.columns]
        else:
            cols = _find_long_format_columns(exposure)
            accident_col = cols["accident"]
            dev_col = cols["development"] 
            value_col = cols.get("value", "value")
            processed_exposure = exposure.pivot(index=accident_col, columns=dev_col, values=value_col)

    registry = DiagnosticsRegistry()
    results = registry.calculate(triangles, processed_exposure)
    labels = registry.get_labels()
    formats = registry.get_formats()
    return results, labels, formats

class DiagnosticsRegistry:
    def __init__(self):
        # Embedded diagnostics configuration (formerly in diagnostics_registry.yaml)
        self.diagnostics = {
            "INCURRED_SEVERITY": {
                "label": "Incurred Severity",
                "format": "integer",
                "recipe": "safe_divide",
                "inputs": ["incurred", "reported_counts"],
                "args": {
                    "numerator": "incurred",
                    "denominator": "reported_counts",
                    "use_incremental": False
                }
            },
            "INCURRED_SEVERITY_INCR": {
                "label": "Incurred Severity (Incremental)",
                "format": "integer",
                "recipe": "safe_divide",
                "inputs": ["incurred", "reported_counts"],
                "args": {
                    "numerator": "incurred",
                    "denominator": "reported_counts",
                    "use_incremental": True
                }
            },
            "PAID_SEVERITY": {
                "label": "Paid Severity",
                "format": "integer",
                "recipe": "safe_divide",
                "inputs": ["paid", "closed_counts"],
                "args": {
                    "numerator": "paid",
                    "denominator": "closed_counts",
                    "use_incremental": False
                }
            },
            "PAID_SEVERITY_INCR": {
                "label": "Paid Severity (Incremental)",
                "format": "integer",
                "recipe": "safe_divide",
                "inputs": ["paid", "closed_counts"],
                "args": {
                    "numerator": "paid",
                    "denominator": "closed_counts",
                    "use_incremental": True
                }
            },
            "PAID_TO_INCURRED": {
                "label": "Paid / Incurred",
                "format": "percentage",
                "recipe": "safe_divide",
                "inputs": ["paid", "incurred"],
                "args": {
                    "numerator": "paid",
                    "denominator": "incurred",
                    "use_incremental": False
                }
            },
            "CASE_RESERVES": {
                "label": "Case Reserves",
                "format": "integer",
                "recipe": "subtract",
                "inputs": ["incurred", "paid"],
                "args": {
                    "left": "incurred",
                    "right": "paid",
                    "use_incremental": False
                }
            },
            "OPEN_COUNTS": {
                "label": "Open Counts",
                "format": "integer",
                "recipe": "subtract",
                "inputs": ["reported_counts", "closed_counts"],
                "args": {
                    "left": "reported_counts",
                    "right": "closed_counts",
                    "use_incremental": False
                }
            },
            "AVERAGE_CASE_RESERVES": {
                "label": "Average Case Reserves",
                "format": "integer",
                "recipe": "nested_divide",
                "inputs": ["incurred", "paid", "reported_counts", "closed_counts"],
                "args": {
                    "numerator_recipe": "subtract",
                    "numerator_args": {"left": "incurred", "right": "paid"},
                    "denominator_recipe": "subtract",
                    "denominator_args": {"left": "reported_counts", "right": "closed_counts"},
                    "use_incremental": False
                }
            },
            "CUMULATIVE_CLOSURE_RATE": {
                "label": "Cumulative Closure Rate",
                "format": "percentage",
                "recipe": "safe_divide",
                "inputs": ["closed_counts", "reported_counts"],
                "args": {
                    "numerator": "closed_counts",
                    "denominator": "reported_counts",
                    "use_incremental": False
                }
            },
            "INCREMENTAL_CLOSURE_RATE": {
                "label": "Incremental Closure Rate",
                "format": "percentage",
                "recipe": "safe_divide",
                "inputs": ["closed_counts", "reported_counts"],
                "args": {
                    "numerator": "closed_counts",
                    "denominator": "reported_counts",
                    "use_incremental": True
                }
            },
            "INCURRED_LOSS_RATE": {
                "label": "Incurred Loss Rate / Ratio",
                "format": "integer",
                "recipe": "safe_divide_exposure",
                "inputs": ["incurred"],
                "args": {
                    "numerator": "incurred",
                    "use_incremental": False
                }
            },
            "PAID_LOSS_RATE": {
                "label": "Paid Loss Rate / Ratio",
                "format": "integer",
                "recipe": "safe_divide_exposure",
                "inputs": ["paid"],
                "args": {
                    "numerator": "paid",
                    "use_incremental": False
                }
            },
            "REPORTED_FREQUENCY": {
                "label": "Reported Frequency",
                "format": "decimal",
                "recipe": "safe_divide_exposure",
                "inputs": ["reported_counts"],
                "args": {
                    "numerator": "reported_counts",
                    "use_incremental": False
                }
            },
            "CLOSED_FREQUENCY": {
                "label": "Closed Frequency",
                "format": "decimal",
                "recipe": "safe_divide_exposure",
                "inputs": ["closed_counts"],
                "args": {
                    "numerator": "closed_counts",
                    "use_incremental": False
                }
            }
        }

    def _get_data(self, key: str, triangles: Dict[str, pd.DataFrame], use_incremental: bool) -> pd.DataFrame:
        if key not in triangles:
            raise KeyError(f"Missing required triangle: {key}")
        
        df = triangles[key]
        if use_incremental:
            # First column remains as is for incremental? 
            # Usually, for triangles, the first development period IS the first incremental value.
            # .diff(axis=1) will make the first column NaN.
            # We want to preserve the first column if it's the first development period.
            incr = df.diff(axis=1)
            incr.iloc[:, 0] = df.iloc[:, 0]
            return incr
        return df

    def get_labels(self) -> Dict[str, str]:
        """Return a mapping of diagnostic key to human-readable label."""
        return {key: spec.get("label", key) for key, spec in self.diagnostics.items()}

    def get_formats(self) -> Dict[str, str]:
        """Return a mapping of diagnostic key to format type."""
        return {key: spec.get("format", "decimal") for key, spec in self.diagnostics.items()}

    def calculate(self, triangles: Dict[str, pd.DataFrame], exposure: Optional[Any] = None) -> Dict[str, pd.DataFrame]:
        results = {}
        for diag_key, spec in self.diagnostics.items():
            recipe = spec["recipe"]
            args = spec["args"]
            inputs = spec.get("inputs", [])
            
            # Check if all inputs are available
            if not all(k in triangles for k in inputs):
                continue

            if recipe == "safe_divide":
                num = self._get_data(args["numerator"], triangles, args.get("use_incremental", False))
                den = self._get_data(args["denominator"], triangles, args.get("use_incremental", False))
                results[diag_key] = num / den.replace(0, np.nan)
            
            elif recipe == "subtract":
                left = self._get_data(args["left"], triangles, args.get("use_incremental", False))
                right = self._get_data(args["right"], triangles, args.get("use_incremental", False))
                results[diag_key] = left - right

            elif recipe == "safe_divide_exposure":
                if exposure is None:
                    continue
                num = self._get_data(args["numerator"], triangles, args.get("use_incremental", False))
                
                if isinstance(exposure, pd.DataFrame):
                    # Exposure is a triangle (wide format expected here)
                    # We assume the index/columns match or align
                    results[diag_key] = num / exposure.replace(0, np.nan)
                elif isinstance(exposure, (pd.Series, dict)):
                    # Exposure is a vector
                    results[diag_key] = num.divide(exposure, axis=0).replace(0, np.nan)
                elif isinstance(exposure, pd.DataFrame):
                    results[diag_key] = num / exposure.replace(0, np.nan)
                else:
                    # Fallback for scalar or unknown
                    results[diag_key] = num / exposure
            
            # Special handling for AVERAGE_CASE_RESERVES which has nested recipes
            if recipe == "nested_divide":
                num_left = self._get_data(args["numerator_args"]["left"], triangles, False)
                num_right = self._get_data(args["numerator_args"]["right"], triangles, False)
                num = num_left - num_right
                
                den_left = self._get_data(args["denominator_args"]["left"], triangles, False)
                den_right = self._get_data(args["denominator_args"]["right"], triangles, False)
                den = den_left - den_right
                
                results[diag_key] = num / den.replace(0, np.nan)
        
        return results

def run_pre_analyst_workflow(
    triangles_data: Dict[str, pd.DataFrame], 
    exposure: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Initial workflow run before analyst intervention.
    Converts to wide, calculates diagnostics, LDFs, and QA metrics.
    Returns average LDFs in both dict and CSV format for tool consumption.
    """
    # 1. Calculate Diagnostics
    diagnostics, diagnostic_labels, diagnostic_formats = calculate_diagnostics(triangles_data, exposure)
    
    results = {
        "triangles": {},
        "diagnostics": {k: v.to_dict() for k, v in diagnostics.items()},
        "diagnostic_labels": diagnostic_labels,  # key -> human-readable label
        "diagnostic_formats": diagnostic_formats,  # key -> format type (integer/decimal)
        "ldf_data": {},
        "average_ldfs_csv": {}  # For passing to calculate_chainladder_ultimates
    }

    # 2. Process each triangle for LDFs and QA
    for name, df in triangles_data.items():
        # Heuristic to handle wide/long
        fmt = _detect_triangle_format(df)
        if fmt == "wide":
            accident_col = df.columns[0]
            long_df = _wide_to_long(df, "value")
            long_df = long_df.rename(columns={"accident_period": accident_col})
            dev_col = "development_period"
        else:
            cols = _find_long_format_columns(df)
            accident_col = cols["accident"]
            dev_col = cols["development"]
            long_df = df.rename(columns={cols.get("value", df.columns[-1]): "value"})

        # Convert to DataFrame if needed
        if isinstance(df, dict) and "data" in df:
            triangle_df = df["data"] 
        else:
            triangle_df = df
            
        results["triangles"][name] = triangle_df.to_dict()
        
        # Skip LDF calculations for exposure triangles
        if name.lower() not in ("paid", "incurred", "reported", "closed"):
            continue
        
        # LDF Calculations  
        ldf_tri_df = calculate_historical_ldfs(triangle_df)
        avgs_df = calculate_average_ldfs(ldf_tri_df, triangle_df)
        qa_metrics = calculate_qa_metrics(ldf_tri_df)
        
        results["ldf_data"][name] = {
            "historical_ldfs": ldf_tri_df.to_dict(),
            "average_ldfs": avgs_df.to_dict(),
            "qa_metrics": qa_metrics
        }
        
        # Store CSV format for tool consumption
        results["average_ldfs_csv"][name] = avgs_df.to_csv()

    return results

def calculate_historical_ldfs(triangle_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate historical age-to-age factors from a triangle DataFrame.
    
    Args:
        triangle_df: Wide DataFrame with periods as index, ages as columns
    """
    wide = triangle_df
    ldfs = []
    cols = sorted(wide.columns)
    for i in range(len(cols)-1):
        c1, c2 = cols[i], cols[i+1]
        factors = wide[c2] / wide[c1]
        ldfs.append(factors.rename(f"{c1}-{c2}"))
    return pd.concat(ldfs, axis=1)

def calculate_average_ldfs(ldf_triangle_df: pd.DataFrame, triangle_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate various average selections (weighted, simple, medial) for multiple time periods.
    
    Args:
        ldf_triangle_df: DataFrame of historical LDFs from calculate_historical_ldfs()
        triangle_df: Wide DataFrame with periods as index, ages as columns (for weighting)
    """
    averages = []
    wide_values = triangle_df
    for interval in ldf_triangle_df.columns:
        # Extract age_from from interval string "age_from-age_to"
        age_from_str = interval.split('-')[0]
        try:
            age_from = int(float(age_from_str))
        except ValueError:
            age_from = age_from_str
            
        factors = ldf_triangle_df[interval].dropna()
        
        if age_from in wide_values.columns:
            weights = wide_values[age_from].loc[factors.index]
        else:
            weights = pd.Series(1, index=factors.index)
        
        def calc_avgs(f, w, n=None):
            if n: 
                f, w = f.tail(n), w.tail(n)
            
            w_sum = w.sum()
            w_avg = (f * w).sum() / w_sum
            s_avg = f.mean()
            
            if len(f) > 2:
                m_avg = f.sort_values().iloc[1:-1].mean()
            else:
                m_avg = s_avg
                
            return w_avg, s_avg, m_avg

        all_w, all_s, all_m = calc_avgs(factors, weights)
        w3, s3, m3 = calc_avgs(factors, weights, 3)
        w5, s5, m5 = calc_avgs(factors, weights, 5)
        
        averages.append({
            "development_interval": interval,
            "weighted_all": all_w, "simple_all": all_s, "medial_all": all_m,
            "weighted_3yr": w3, "simple_3yr": s3, "medial_3yr": m3,
            "weighted_5yr": w5, "simple_5yr": s5, "medial_5yr": m5
        })
        
    return pd.DataFrame(averages).set_index("development_interval").T

def calculate_qa_metrics(ldf_tri_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate QA metrics for LDFs to identify trends and volatility.
    """
    metrics = {}
    for col in ldf_tri_df.columns:
        factors = ldf_tri_df[col].dropna()
        if len(factors) > 1:
            cv = factors.std() / factors.mean()
            # Trend calculation (simple linear slope of the last 3-5 points if available)
            if len(factors) >= 3:
                y = factors.values
                x = np.arange(len(y))
                slope = np.polyfit(x, y, 1)[0]
            else:
                slope = 0.0
            
            metrics[col] = {
                "cv": round(cv, 4),
                "slope": round(slope, 4)
            }
        else:
            metrics[col] = {"cv": 0.0, "slope": 0.0}
    return metrics


def make_selections_from_averages(
    averages_df: pd.DataFrame,
    qa_metrics: Dict[str, Dict[str, float]]
) -> Dict[str, List[Dict]]:
    """
    Make LDF selections based on calculated averages and QA metrics.
    
    Args:
        averages_df: DataFrame of averages from calculate_averages
        qa_metrics: Dictionary of QA metrics from calculate_qa_metrics
    
    Returns:
        Dictionary with three scenarios (Conservative, Best Estimate, Optimistic)
        Each scenario has a list of selections with averageType and reasoning
    """
    scenarios = {
        'Conservative': [],
        'Best Estimate': [],
        'Optimistic': []
    }
    
    for dev_interval in averages_df.columns:
        cv = qa_metrics.get(dev_interval, {}).get('cv', 0)
        slope = qa_metrics.get(dev_interval, {}).get('slope', 0)
        
        # Conservative: Prefer weighted averages or longer periods
        if cv < 0.05:  # Low volatility
            scenarios['Conservative'].append({
                'averageType': 'weighted3',
                'reasoning': f'Low volatility (CV={cv:.3f}) supports recent trend analysis'
            })
        elif cv < 0.10:
            scenarios['Conservative'].append({
                'averageType': 'weighted5',
                'reasoning': f'Moderate volatility (CV={cv:.3f}) requires longer-term perspective'
            })
        else:
            scenarios['Conservative'].append({
                'averageType': 'weightedAll',
                'reasoning': f'High volatility (CV={cv:.3f}) requires full data for stability'
            })
        
        # Best Estimate: Balanced approach
        if cv < 0.08:
            if abs(slope) < 0.01:
                scenarios['Best Estimate'].append({
                    'averageType': 'simple5',
                    'reasoning': f'Stable pattern (CV={cv:.3f}, slope={slope:.4f}) indicates consistent development'
                })
            else:
                trend_desc = "declining" if slope < 0 else "increasing"
                scenarios['Best Estimate'].append({
                    'averageType': 'simple5',
                    'reasoning': f'Stable with {trend_desc} trend (CV={cv:.3f}, slope={slope:.4f})'
                })
        else:
            scenarios['Best Estimate'].append({
                'averageType': 'simpleAll',
                'reasoning': f'Variable pattern (CV={cv:.3f}) benefits from full historical perspective'
            })
        
        # Optimistic: Recent trends
        if slope < -0.01:  # Significant decreasing trend
            scenarios['Optimistic'].append({
                'averageType': 'simple3',
                'reasoning': f'Strong declining trend (slope={slope:.4f}) suggests continued improvement'
            })
        elif slope < 0:  # Mild decreasing trend
            scenarios['Optimistic'].append({
                'averageType': 'simple3',
                'reasoning': f'Mild declining trend (slope={slope:.4f}) supports recent experience'
            })
        elif cv < 0.06:  # Stable, no strong trend
            scenarios['Optimistic'].append({
                'averageType': 'simple5',
                'reasoning': f'Stable development (CV={cv:.3f}) with no adverse trends'
            })
        else:
            scenarios['Optimistic'].append({
                'averageType': 'simple5',
                'reasoning': f'Recent experience (CV={cv:.3f}) may reflect improved conditions'
            })
    
    return scenarios


def save_triangle_data(triangle_df: pd.DataFrame, triangle_name: str, output_path: str) -> str:
    """
    Save triangle data to a CSV file.
    
    Args:
        triangle_df: Wide DataFrame with periods as index, ages as columns
        triangle_name: Name of the triangle
        output_path: Path to save the CSV file
    
    Returns:
        Path to saved file
    """
    wide_df = triangle_df.copy()
    
    # Rename index to "Period" for clarity
    wide_df.index.name = "Period"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save as CSV with Period as first column
    wide_df.to_csv(output_path, index=True)
    
    return str(output_path)


def create_selections_csv(
    triangle_df: pd.DataFrame,
    triangle_name: str,
    scenarios: Optional[Dict[str, List[Dict]]] = None
) -> pd.DataFrame:
    """
    Create a selections DataFrame (CSV format).
    
    Args:
        triangle_df: Wide DataFrame with periods as index, ages as columns
        triangle_name: Name of the triangle
        scenarios: Optional custom scenarios dict. If None, will auto-generate selections.
    
    Returns:
        DataFrame with columns: Scenario, AgeFactor, AverageType, ManualValue, Reasoning
    """
    # Generate scenarios if not provided
    if scenarios is None:
        ldf_tri = calculate_historical_ldfs(triangle_df)
        averages = calculate_average_ldfs(ldf_tri, triangle_df)
        qa_metrics = calculate_qa_metrics(ldf_tri)
        scenarios = make_selections_from_averages(averages, qa_metrics)
    
    # Get age factors from triangle
    ages = triangle_df.columns.tolist()
    age_factors = [f"{ages[i]}-{ages[i+1]}" for i in range(len(ages)-1)]
    
    # Build rows for CSV
    rows = []
    for scenario_label, selections in scenarios.items():
        for i, selection in enumerate(selections):
            row = {
                'Scenario': scenario_label,
                'AgeFactor': age_factors[i],
                'AverageType': selection.get('averageType', ''),
                'ManualValue': selection.get('manualValue', ''),
                'Reasoning': selection.get('reasoning', '')
            }
            rows.append(row)
    
    return pd.DataFrame(rows)


def save_selections_csv(selections_df: pd.DataFrame, output_path: str):
    """
    Save selections data to a CSV file.
    
    Args:
        selections_df: DataFrame from create_selections_csv
        output_path: Path to save the CSV file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    selections_df.to_csv(output_path, index=False)
    
    print(f"✓ Selections saved to: {output_path}")
    return str(output_path)


def perform_full_analysis(
    triangle_df: pd.DataFrame,
    triangle_name: str,
    processed_dir: str = "output/processed",
    selections_dir: str = "output/selections"
) -> str:
    """
    Perform complete chain ladder analysis and save results.
    
    Args:
        triangle_df: Wide DataFrame with periods as index, ages as columns
        triangle_name: Name of the triangle (e.g., "Paid Losses")
        processed_dir: Directory to save processed triangle CSV
        selections_dir: Directory to save selections CSV
    
    Returns:
        Path to saved selections CSV file
    """
    print(f"\n{'='*60}")
    print(f"Chain Ladder Analysis: {triangle_name}")
    print(f"{'='*60}\n")
    
    filename = triangle_name.lower().replace(' ', '_')
    
    # Save triangle data to processed directory
    triangle_path = f"{processed_dir}/{filename}_triangle.csv"
    save_triangle_data(triangle_df, triangle_name, triangle_path)
    print(f"✓ Triangle data: {triangle_path}")
    
    # Create and save selections CSV
    selections_df = create_selections_csv(triangle_df, triangle_name)
    selections_path = f"{selections_dir}/{filename}_selections.csv"
    save_selections_csv(selections_df, selections_path)
    
    print(f"\nAnalysis complete!")
    print(f"Periods: {len(triangle_df.index)}")
    print(f"Ages: {len(triangle_df.columns)}")
    print(f"Scenarios: {selections_df['Scenario'].unique().tolist()}")
    
    return selections_path
