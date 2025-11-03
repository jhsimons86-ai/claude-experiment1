"""
Data Preprocessing Pipeline for MICE Stock Prediction Experiment
Handles cleaning, validation, and quality checks
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set random seed
np.random.seed(42)

# Define paths
DATA_DIR = Path(__file__).parent
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'


def clean_data(df, ticker_name=''):
    """
    Clean and validate price data

    Parameters:
    -----------
    df : DataFrame
        Raw price data with OHLCV columns
    ticker_name : str
        Name of the ticker for logging

    Returns:
    --------
    DataFrame : Cleaned data
    """
    print(f"\n  Cleaning {ticker_name}...")

    # Make a copy
    df_clean = df.copy()

    initial_rows = len(df_clean)

    # 1. Remove duplicate timestamps
    df_clean = df_clean[~df_clean.index.duplicated(keep='first')]
    if len(df_clean) < initial_rows:
        print(f"    Removed {initial_rows - len(df_clean)} duplicate timestamps")

    # 2. Check for negative prices (data errors)
    if 'Close' in df_clean.columns:
        negative_prices = (df_clean['Close'] < 0).sum()
        if negative_prices > 0:
            print(f"    ⚠️  Found {negative_prices} negative prices, setting to NaN")
            df_clean.loc[df_clean['Close'] < 0, 'Close'] = np.nan

    # 3. Check for zero prices (likely data errors)
    if 'Close' in df_clean.columns:
        zero_prices = (df_clean['Close'] == 0).sum()
        if zero_prices > 0:
            print(f"    ⚠️  Found {zero_prices} zero prices, setting to NaN")
            df_clean.loc[df_clean['Close'] == 0, 'Close'] = np.nan

    # 4. Check for extreme price jumps (>50% in one day, likely splits/errors)
    if 'Close' in df_clean.columns:
        returns = df_clean['Close'].pct_change()
        extreme_returns = (np.abs(returns) > 0.5).sum()
        if extreme_returns > 0:
            print(f"    ⚠️  Found {extreme_returns} extreme daily returns (>50%)")
            # Note: In real scenario, would investigate if these are stock splits

    # 5. Handle missing data
    missing_before = df_clean.isna().sum().sum()

    # Forward fill small gaps (up to 5 days)
    df_clean_filled = df_clean.fillna(method='ffill', limit=5)

    missing_after = df_clean_filled.isna().sum().sum()

    if missing_before > 0:
        print(f"    Missing values: {missing_before} → {missing_after} (after forward fill)")

    # 6. Validate OHLC relationships (if available)
    if all(col in df_clean_filled.columns for col in ['Open', 'High', 'Low', 'Close']):
        # High should be >= Open, Close, Low
        # Low should be <= Open, Close, High
        invalid_high = ((df_clean_filled['High'] < df_clean_filled['Close']) |
                        (df_clean_filled['High'] < df_clean_filled['Open'])).sum()
        invalid_low = ((df_clean_filled['Low'] > df_clean_filled['Close']) |
                       (df_clean_filled['Low'] > df_clean_filled['Open'])).sum()

        if invalid_high > 0 or invalid_low > 0:
            print(f"    ⚠️  OHLC relationship violations: {invalid_high + invalid_low}")

    print(f"    ✓ Clean: {len(df_clean_filled)} rows, {df_clean_filled.columns.tolist()}")

    return df_clean_filled


def handle_missing(df, method='ffill', max_gap=10):
    """
    Handle missing data with specified method

    Parameters:
    -----------
    df : DataFrame
        Data with potential missing values
    method : str
        Method to handle missing: 'ffill', 'interpolate', 'drop'
    max_gap : int
        Maximum gap size to fill

    Returns:
    --------
    DataFrame : Data with missing values handled
    """
    if method == 'ffill':
        return df.fillna(method='ffill', limit=max_gap)
    elif method == 'interpolate':
        return df.interpolate(method='linear', limit=max_gap)
    elif method == 'drop':
        return df.dropna()
    else:
        raise ValueError(f"Unknown method: {method}")


def validate_data(df, ticker_name=''):
    """
    Validate data quality and generate statistics

    Parameters:
    -----------
    df : DataFrame
        Processed data to validate
    ticker_name : str
        Name for logging

    Returns:
    --------
    dict : Validation statistics
    """
    stats = {
        'ticker': ticker_name,
        'rows': len(df),
        'start_date': df.index[0] if len(df) > 0 else None,
        'end_date': df.index[-1] if len(df) > 0 else None,
        'columns': list(df.columns),
        'missing_pct': {},
        'outliers': {}
    }

    # Calculate missing percentages
    for col in df.columns:
        missing_pct = (df[col].isna().sum() / len(df)) * 100
        stats['missing_pct'][col] = missing_pct

    # Detect outliers (>3 standard deviations)
    for col in df.select_dtypes(include=[np.number]).columns:
        mean = df[col].mean()
        std = df[col].std()
        outliers = ((df[col] - mean).abs() > 3 * std).sum()
        stats['outliers'][col] = outliers

    return stats


def preprocess_scenario_1():
    """
    Preprocess Scenario 1: Cross-Market Holiday Prediction
    """
    print("=" * 80)
    print("PREPROCESSING SCENARIO 1: Cross-Market Holiday Prediction")
    print("=" * 80)

    scenario_1_dir = RAW_DIR / 'scenario_1'
    parquet_files = list(scenario_1_dir.glob('*.parquet'))

    # Exclude combined file
    parquet_files = [f for f in parquet_files if 'combined' not in f.name]

    print(f"\nFound {len(parquet_files)} ticker files to process")

    processed_data = {}
    validation_stats = []

    for filepath in sorted(parquet_files):
        ticker = filepath.stem

        # Load data
        df = pd.read_parquet(filepath)

        # Clean data
        df_clean = clean_data(df, ticker)

        # Validate
        stats = validate_data(df_clean, ticker)
        validation_stats.append(stats)

        # Store
        processed_data[ticker] = df_clean

    # Save processed data
    processed_scenario_1 = PROCESSED_DIR / 'scenario_1'
    processed_scenario_1.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving processed data to {processed_scenario_1}...")

    for ticker, df in processed_data.items():
        filepath = processed_scenario_1 / f'{ticker}.parquet'
        df.to_parquet(filepath)
        print(f"  Saved: {filepath.name}")

    # Create combined dataset
    close_prices = pd.DataFrame()
    for ticker, df in processed_data.items():
        if 'Close' in df.columns:
            close_prices[ticker] = df['Close']

    combined_path = processed_scenario_1 / 'combined_daily.parquet'
    close_prices.to_parquet(combined_path)
    print(f"  Saved combined: {combined_path.name} (shape: {close_prices.shape})")

    # Generate quality report
    print("\n" + "=" * 80)
    print("DATA QUALITY SUMMARY")
    print("=" * 80)

    for stats in validation_stats:
        print(f"\n{stats['ticker']}:")
        print(f"  Rows: {stats['rows']}")
        print(f"  Date range: {stats['start_date'].date()} to {stats['end_date'].date()}")

        # Show missing percentages
        max_missing = max(stats['missing_pct'].values()) if stats['missing_pct'] else 0
        if max_missing > 0:
            print(f"  Max missing: {max_missing:.2f}%")

        # Show outliers
        total_outliers = sum(stats['outliers'].values())
        if total_outliers > 0:
            print(f"  Outliers detected: {total_outliers}")

    return processed_data, validation_stats


def preprocess_scenario_2():
    """
    Preprocess Scenario 2: Sector Rotation Prediction
    """
    print("\n" + "=" * 80)
    print("PREPROCESSING SCENARIO 2: Sector Rotation Prediction")
    print("=" * 80)

    scenario_2_dir = RAW_DIR / 'scenario_2'
    parquet_files = list(scenario_2_dir.glob('*.parquet'))

    print(f"\nFound {len(parquet_files)} ticker files to process")

    processed_data = {}
    validation_stats = []

    for filepath in sorted(parquet_files):
        ticker = filepath.stem

        # Load data
        df = pd.read_parquet(filepath)

        # Clean data
        df_clean = clean_data(df, ticker)

        # Validate
        stats = validate_data(df_clean, ticker)
        validation_stats.append(stats)

        # Store
        processed_data[ticker] = df_clean

    # Save processed data
    processed_scenario_2 = PROCESSED_DIR / 'scenario_2'
    processed_scenario_2.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving processed data to {processed_scenario_2}...")

    for ticker, df in processed_data.items():
        filepath = processed_scenario_2 / f'{ticker}.parquet'
        df.to_parquet(filepath)
        print(f"  Saved: {filepath.name}")

    # Create combined dataset
    close_prices = pd.DataFrame()
    for ticker, df in processed_data.items():
        if 'Close' in df.columns:
            close_prices[ticker] = df['Close']

    combined_path = processed_scenario_2 / 'combined_daily.parquet'
    close_prices.to_parquet(combined_path)
    print(f"  Saved combined: {combined_path.name} (shape: {close_prices.shape})")

    return processed_data, validation_stats


def generate_quality_report(scenario_1_stats, scenario_2_stats):
    """
    Generate comprehensive data quality report
    """
    print("\n" + "=" * 80)
    print("GENERATING COMPREHENSIVE QUALITY REPORT")
    print("=" * 80)

    report = []
    report.append("# Data Quality Report")
    report.append(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Scenario 1
    report.append("\n## Scenario 1: Cross-Market Holiday Prediction")
    report.append(f"\nTotal tickers: {len(scenario_1_stats)}")

    for stats in scenario_1_stats:
        report.append(f"\n### {stats['ticker']}")
        report.append(f"- Rows: {stats['rows']}")
        report.append(f"- Date range: {stats['start_date'].date()} to {stats['end_date'].date()}")
        report.append(f"- Columns: {', '.join(stats['columns'])}")

        if stats['missing_pct']:
            report.append(f"- Missing data:")
            for col, pct in stats['missing_pct'].items():
                if pct > 0:
                    report.append(f"  - {col}: {pct:.2f}%")

        if stats['outliers']:
            total_outliers = sum(stats['outliers'].values())
            if total_outliers > 0:
                report.append(f"- Outliers (>3 std): {total_outliers}")

    # Scenario 2
    report.append("\n## Scenario 2: Sector Rotation Prediction")
    report.append(f"\nTotal tickers: {len(scenario_2_stats)}")

    for stats in scenario_2_stats:
        report.append(f"\n### {stats['ticker']}")
        report.append(f"- Rows: {stats['rows']}")
        report.append(f"- Date range: {stats['start_date'].date()} to {stats['end_date'].date()}")

    # Save report
    report_path = PROCESSED_DIR / 'QUALITY_REPORT.md'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))

    print(f"\nQuality report saved to: {report_path}")

    return report_path


def main():
    """
    Main preprocessing function
    """
    print("=" * 80)
    print("MICE STOCK PREDICTION - DATA PREPROCESSING")
    print("=" * 80)

    # Preprocess all scenarios
    scenario_1_data, scenario_1_stats = preprocess_scenario_1()
    scenario_2_data, scenario_2_stats = preprocess_scenario_2()

    # Generate quality report
    report_path = generate_quality_report(scenario_1_stats, scenario_2_stats)

    print("\n" + "=" * 80)
    print("PREPROCESSING COMPLETE")
    print("=" * 80)
    print(f"\nProcessed data saved to: {PROCESSED_DIR}")
    print(f"Quality report: {report_path}")
    print("\nNext step: Feature engineering (create_features.py)")


if __name__ == '__main__':
    main()
