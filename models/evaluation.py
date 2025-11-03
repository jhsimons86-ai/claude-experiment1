"""
Evaluation Metrics for MICE Stock Prediction Experiment
Implements primary and secondary metrics for model comparison
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Mean Absolute Error (MAE)

    MAE = mean(|y_true - y_pred|)

    Parameters:
    -----------
    y_true : ndarray
        True values
    y_pred : ndarray
        Predicted values

    Returns:
    --------
    mae : float
        Mean absolute error
    """
    return np.mean(np.abs(y_true - y_pred))


def root_mean_square_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Root Mean Square Error (RMSE)

    RMSE = sqrt(mean((y_true - y_pred)^2))

    Parameters:
    -----------
    y_true : ndarray
        True values
    y_pred : ndarray
        Predicted values

    Returns:
    --------
    rmse : float
        Root mean square error
    """
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-10) -> float:
    """
    Calculate Mean Absolute Percentage Error (MAPE)

    MAPE = mean(|y_true - y_pred| / |y_true|) * 100

    Parameters:
    -----------
    y_true : ndarray
        True values
    y_pred : ndarray
        Predicted values
    epsilon : float
        Small value to avoid division by zero

    Returns:
    --------
    mape : float
        Mean absolute percentage error (in percentage)
    """
    # Avoid division by zero
    denominator = np.maximum(np.abs(y_true), epsilon)
    return np.mean(np.abs((y_true - y_pred) / denominator)) * 100


def direction_accuracy(y_true: np.ndarray, y_pred: np.ndarray, y_previous: np.ndarray) -> float:
    """
    Calculate direction accuracy

    Measures if the model correctly predicts the direction of change

    Parameters:
    -----------
    y_true : ndarray
        True values
    y_pred : ndarray
        Predicted values
    y_previous : ndarray
        Previous values (for calculating direction)

    Returns:
    --------
    accuracy : float
        Direction accuracy (0-1)
    """
    true_direction = np.sign(y_true - y_previous)
    pred_direction = np.sign(y_pred - y_previous)

    # Calculate accuracy
    correct = (true_direction == pred_direction).sum()
    total = len(y_true)

    return correct / total


def sharpe_ratio(y_true: np.ndarray, y_pred: np.ndarray, y_current: np.ndarray,
                 risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """
    Calculate Sharpe ratio of a trading strategy based on predictions

    Strategy:
    - If pred > current: Buy (long)
    - If pred < current: Short (or stay out)

    Parameters:
    -----------
    y_true : ndarray
        True future values
    y_pred : ndarray
        Predicted future values
    y_current : ndarray
        Current values (at time of prediction)
    risk_free_rate : float
        Annual risk-free rate (default 0.0)
    periods_per_year : int
        Number of trading periods per year (default 252 for daily)

    Returns:
    --------
    sharpe : float
        Annualized Sharpe ratio
    """
    # Calculate returns based on strategy
    # If we predict up (pred > current), we go long
    # Return is (true - current) / current
    # If we predict down (pred < current), we go short
    # Return is (current - true) / current

    returns = []
    for pred, true, curr in zip(y_pred, y_true, y_current):
        if pred > curr:
            # Long position
            ret = (true - curr) / curr
        else:
            # Short position (or stay out - use 0)
            ret = (curr - true) / curr  # If shorting
            # ret = 0  # If staying out

        returns.append(ret)

    returns = np.array(returns)

    # Calculate Sharpe ratio
    mean_return = np.mean(returns)
    std_return = np.std(returns)

    if std_return == 0:
        return 0.0

    # Annualize
    annual_return = mean_return * periods_per_year
    annual_std = std_return * np.sqrt(periods_per_year)
    annual_rf = risk_free_rate

    sharpe = (annual_return - annual_rf) / annual_std

    return sharpe


def r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate R-squared (coefficient of determination)

    Parameters:
    -----------
    y_true : ndarray
        True values
    y_pred : ndarray
        Predicted values

    Returns:
    --------
    r2 : float
        R-squared value
    """
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)

    if ss_tot == 0:
        return 0.0

    return 1 - (ss_res / ss_tot)


def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray,
                         y_previous: Optional[np.ndarray] = None,
                         y_current: Optional[np.ndarray] = None) -> Dict[str, float]:
    """
    Calculate all evaluation metrics

    Parameters:
    -----------
    y_true : ndarray
        True values
    y_pred : ndarray
        Predicted values
    y_previous : ndarray, optional
        Previous values (needed for direction accuracy)
    y_current : ndarray, optional
        Current values (needed for Sharpe ratio)

    Returns:
    --------
    metrics : dict
        Dictionary of all metrics
    """
    metrics = {}

    # Primary metrics
    metrics['mae'] = mean_absolute_error(y_true, y_pred)
    metrics['rmse'] = root_mean_square_error(y_true, y_pred)
    metrics['mape'] = mean_absolute_percentage_error(y_true, y_pred)
    metrics['r2'] = r_squared(y_true, y_pred)

    # Secondary metrics
    if y_previous is not None:
        metrics['direction_accuracy'] = direction_accuracy(y_true, y_pred, y_previous)

    if y_current is not None:
        metrics['sharpe_ratio'] = sharpe_ratio(y_true, y_pred, y_current)

    return metrics


def compare_models(baseline_errors: np.ndarray, model_errors: np.ndarray,
                   model_name: str = "Model") -> Dict[str, any]:
    """
    Statistical comparison between baseline and model

    Uses paired t-test and calculates effect size (Cohen's d)

    Parameters:
    -----------
    baseline_errors : ndarray
        Absolute errors from baseline
    model_errors : ndarray
        Absolute errors from model
    model_name : str
        Name of the model being compared

    Returns:
    --------
    comparison : dict
        Dictionary with statistical test results
    """
    # Paired t-test
    t_stat, p_value = stats.ttest_rel(baseline_errors, model_errors)

    # Cohen's d (effect size)
    mean_diff = np.mean(baseline_errors) - np.mean(model_errors)
    pooled_std = np.sqrt((np.var(baseline_errors) + np.var(model_errors)) / 2)
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0.0

    # Percentage improvement
    pct_improvement = ((np.mean(baseline_errors) - np.mean(model_errors)) /
                       np.mean(baseline_errors)) * 100

    comparison = {
        'model': model_name,
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'cohens_d': cohens_d,
        'effect_size': _interpret_cohens_d(cohens_d),
        'pct_improvement': pct_improvement,
        'better': mean_diff > 0  # True if model is better
    }

    return comparison


def _interpret_cohens_d(d: float) -> str:
    """
    Interpret Cohen's d effect size

    Parameters:
    -----------
    d : float
        Cohen's d value

    Returns:
    --------
    interpretation : str
        Verbal interpretation
    """
    d_abs = abs(d)

    if d_abs < 0.2:
        return "negligible"
    elif d_abs < 0.5:
        return "small"
    elif d_abs < 0.8:
        return "medium"
    else:
        return "large"


def bonferroni_correction(p_values: list, alpha: float = 0.05) -> Tuple[list, float]:
    """
    Apply Bonferroni correction for multiple comparisons

    Parameters:
    -----------
    p_values : list
        List of p-values from multiple tests
    alpha : float
        Overall significance level (default 0.05)

    Returns:
    --------
    significant : list
        Boolean list indicating which tests are significant
    corrected_alpha : float
        Corrected alpha level
    """
    n_tests = len(p_values)
    corrected_alpha = alpha / n_tests

    significant = [p < corrected_alpha for p in p_values]

    return significant, corrected_alpha


def create_comparison_table(results: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """
    Create a comparison table from results

    Parameters:
    -----------
    results : dict
        Dictionary of {model_name: metrics_dict}

    Returns:
    --------
    table : DataFrame
        Formatted comparison table
    """
    df = pd.DataFrame(results).T

    # Round values for readability (only numeric columns)
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if col in ['mae', 'rmse', 'mape', 'r2', 'sharpe_ratio']:
                df[col] = df[col].round(4)
            elif col == 'direction_accuracy':
                df[col] = (df[col] * 100).round(2)  # Convert to percentage

    # Sort by MAE (lower is better)
    if 'mae' in df.columns:
        df = df.sort_values('mae')

    return df


def save_results(results: Dict[str, Dict[str, float]], filepath: str):
    """
    Save results to CSV file

    Parameters:
    -----------
    results : dict
        Dictionary of {model_name: metrics_dict}
    filepath : str
        Path to save CSV file
    """
    df = create_comparison_table(results)
    df.to_csv(filepath)
    print(f"Results saved to: {filepath}")


def print_comparison(baseline_name: str, model_name: str, comparison: Dict[str, any]):
    """
    Pretty print comparison results

    Parameters:
    -----------
    baseline_name : str
        Name of baseline model
    model_name : str
        Name of comparison model
    comparison : dict
        Comparison results from compare_models()
    """
    print(f"\n{'='*60}")
    print(f"Comparison: {model_name} vs {baseline_name}")
    print(f"{'='*60}")

    print(f"t-statistic: {comparison['t_statistic']:.3f}")
    print(f"p-value: {comparison['p_value']:.4f}")
    print(f"Significant (p < 0.05): {'Yes' if comparison['significant'] else 'No'}")
    print(f"Cohen's d: {comparison['cohens_d']:.3f} ({comparison['effect_size']})")
    print(f"Improvement: {comparison['pct_improvement']:.2f}%")

    if comparison['better']:
        print(f"\n✓ {model_name} performs BETTER than {baseline_name}")
    else:
        print(f"\n✗ {model_name} performs WORSE than {baseline_name}")

    print(f"{'='*60}\n")


# Convenience function for complete evaluation
def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series,
                   y_previous: Optional[pd.Series] = None,
                   y_current: Optional[pd.Series] = None) -> Dict[str, float]:
    """
    Complete evaluation of a model

    Parameters:
    -----------
    model : BaselineModel
        Fitted model
    X_test : DataFrame
        Test features
    y_test : Series
        Test targets
    y_previous : Series, optional
        Previous values for direction accuracy
    y_current : Series, optional
        Current values for Sharpe ratio

    Returns:
    --------
    results : dict
        Dictionary of all metrics
    """
    # Make predictions
    y_pred = model.predict(X_test)

    # Convert to numpy arrays (handle both Series and ndarray)
    y_true = y_test.values if hasattr(y_test, 'values') else y_test
    y_prev = y_previous.values if y_previous is not None and hasattr(y_previous, 'values') else y_previous
    y_curr = y_current.values if y_current is not None and hasattr(y_current, 'values') else y_current

    # Calculate metrics
    results = evaluate_predictions(y_true, y_pred, y_prev, y_curr)

    # Add model name
    results['model'] = model.name

    return results
