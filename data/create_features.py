"""
Feature Engineering for MICE Stock Prediction Experiment
Creates technical indicators and features for modeling
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
PROCESSED_DIR = DATA_DIR / 'processed'


def create_returns(df, periods=[1, 5, 20]):
    """
    Create return features for different periods

    Parameters:
    -----------
    df : DataFrame
        Price data with 'Close' column
    periods : list
        List of periods for return calculation

    Returns:
    --------
    DataFrame : Original data with return features
    """
    df_features = df.copy()

    for period in periods:
        # Simple returns
        df_features[f'return_{period}d'] = df['Close'].pct_change(period)

        # Log returns
        df_features[f'log_return_{period}d'] = np.log(df['Close'] / df['Close'].shift(period))

    return df_features


def create_moving_averages(df, windows=[5, 10, 20, 50]):
    """
    Create moving average features

    Parameters:
    -----------
    df : DataFrame
        Price data with 'Close' column
    windows : list
        List of window sizes for moving averages

    Returns:
    --------
    DataFrame : Original data with MA features
    """
    df_features = df.copy()

    for window in windows:
        # Simple moving average
        df_features[f'sma_{window}'] = df['Close'].rolling(window=window).mean()

        # Exponential moving average
        df_features[f'ema_{window}'] = df['Close'].ewm(span=window, adjust=False).mean()

        # Deviation from moving average (normalized)
        df_features[f'price_to_sma_{window}'] = (df['Close'] - df_features[f'sma_{window}']) / df_features[
            f'sma_{window}']

    return df_features


def create_volatility_features(df, windows=[5, 20]):
    """
    Create volatility features

    Parameters:
    -----------
    df : DataFrame
        Price data with returns
    windows : list
        List of window sizes for volatility calculation

    Returns:
    --------
    DataFrame : Original data with volatility features
    """
    df_features = df.copy()

    # Calculate returns if not present
    if 'return_1d' not in df_features.columns:
        df_features['return_1d'] = df['Close'].pct_change()

    for window in windows:
        # Rolling standard deviation of returns
        df_features[f'volatility_{window}d'] = df_features['return_1d'].rolling(window=window).std()

        # Historical volatility (annualized)
        df_features[f'hist_vol_{window}d'] = df_features[f'volatility_{window}d'] * np.sqrt(252)

    return df_features


def create_momentum_features(df, windows=[5, 10, 20]):
    """
    Create momentum indicators

    Parameters:
    -----------
    df : DataFrame
        Price data
    windows : list
        Lookback windows for momentum

    Returns:
    --------
    DataFrame : Original data with momentum features
    """
    df_features = df.copy()

    for window in windows:
        # Rate of change
        df_features[f'roc_{window}d'] = ((df['Close'] - df['Close'].shift(window)) /
                                         df['Close'].shift(window)) * 100

        # Momentum (simple price difference)
        df_features[f'momentum_{window}d'] = df['Close'] - df['Close'].shift(window)

    # RSI (Relative Strength Index) - 14 day
    window = 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    df_features['rsi_14'] = 100 - (100 / (1 + rs))

    return df_features


def create_volume_features(df, windows=[5, 20]):
    """
    Create volume-based features

    Parameters:
    -----------
    df : DataFrame
        Data with 'Volume' column
    windows : list
        Windows for volume features

    Returns:
    --------
    DataFrame : Original data with volume features
    """
    df_features = df.copy()

    if 'Volume' not in df.columns:
        return df_features

    for window in windows:
        # Average volume
        df_features[f'avg_volume_{window}d'] = df['Volume'].rolling(window=window).mean()

        # Volume ratio (current / average)
        df_features[f'volume_ratio_{window}d'] = df['Volume'] / df_features[f'avg_volume_{window}d']

    # Volume trend (simple)
    df_features['volume_trend_5d'] = (df['Volume'].rolling(5).mean() /
                                      df['Volume'].rolling(20).mean())

    return df_features


def create_time_features(df):
    """
    Create time-based features

    Parameters:
    -----------
    df : DataFrame
        Data with datetime index

    Returns:
    --------
    DataFrame : Original data with time features
    """
    df_features = df.copy()

    # Day of week (Monday = 0, Friday = 4)
    df_features['day_of_week'] = df.index.dayofweek

    # Month
    df_features['month'] = df.index.month

    # Quarter
    df_features['quarter'] = df.index.quarter

    # Year
    df_features['year'] = df.index.year

    # Days since epoch (for temporal ordering)
    df_features['days_since_epoch'] = (df.index - pd.Timestamp('1970-01-01')).days

    # Is month end
    df_features['is_month_end'] = df.index.is_month_end.astype(int)

    # Is quarter end
    df_features['is_quarter_end'] = df.index.is_quarter_end.astype(int)

    return df_features


def create_cross_asset_features(df_dict):
    """
    Create features based on relationships between assets

    Parameters:
    -----------
    df_dict : dict
        Dictionary of {ticker: DataFrame} with 'Close' prices

    Returns:
    --------
    DataFrame : Combined features across assets
    """
    # Combine close prices
    close_prices = pd.DataFrame()
    for ticker, df in df_dict.items():
        if 'Close' in df.columns:
            close_prices[ticker] = df['Close']

    # Calculate correlations (rolling)
    features = pd.DataFrame(index=close_prices.index)

    # For each asset, calculate its correlation with others
    # (using 20-day rolling window)
    for ticker in close_prices.columns:
        returns_ticker = close_prices[ticker].pct_change()

        for other_ticker in close_prices.columns:
            if ticker != other_ticker:
                returns_other = close_prices[other_ticker].pct_change()

                # Rolling correlation
                rolling_corr = returns_ticker.rolling(20).corr(returns_other)
                features[f'corr_{ticker}_{other_ticker}_20d'] = rolling_corr

    return features


def engineer_features_scenario_1():
    """
    Feature engineering for Scenario 1: Cross-Market Holiday Prediction
    """
    print("=" * 80)
    print("FEATURE ENGINEERING SCENARIO 1: Cross-Market Holiday Prediction")
    print("=" * 80)

    scenario_1_dir = PROCESSED_DIR / 'scenario_1'
    parquet_files = [f for f in scenario_1_dir.glob('*.parquet') if 'combined' not in f.name]

    print(f"\nEngineering features for {len(parquet_files)} tickers")

    all_featured_data = {}

    for filepath in sorted(parquet_files):
        ticker = filepath.stem
        print(f"\n  Processing {ticker}...")

        # Load processed data
        df = pd.read_parquet(filepath)

        # Apply feature engineering
        df_features = df.copy()

        # Returns
        df_features = create_returns(df_features, periods=[1, 5, 20])
        print(f"    ✓ Created return features")

        # Moving averages
        df_features = create_moving_averages(df_features, windows=[5, 10, 20, 50])
        print(f"    ✓ Created moving average features")

        # Volatility
        df_features = create_volatility_features(df_features, windows=[5, 20])
        print(f"    ✓ Created volatility features")

        # Momentum
        df_features = create_momentum_features(df_features, windows=[5, 10, 20])
        print(f"    ✓ Created momentum features")

        # Volume (if available)
        if 'Volume' in df.columns:
            df_features = create_volume_features(df_features, windows=[5, 20])
            print(f"    ✓ Created volume features")

        # Time features
        df_features = create_time_features(df_features)
        print(f"    ✓ Created time features")

        print(f"    Total features: {len(df_features.columns)}")

        all_featured_data[ticker] = df_features

    # Save featured data
    print(f"\nSaving featured data...")
    for ticker, df in all_featured_data.items():
        filepath = scenario_1_dir / f'{ticker}_featured.parquet'
        df.to_parquet(filepath)
        print(f"  Saved: {filepath.name}")

    # Create combined featured dataset
    print(f"\nCreating combined featured dataset...")

    # Start with close prices
    combined = pd.DataFrame()
    for ticker, df in all_featured_data.items():
        # Select a subset of important features to avoid explosion
        important_features = ['Close', 'return_1d', 'return_5d', 'sma_20',
                              'volatility_20d', 'roc_5d', 'day_of_week', 'month']

        for feature in important_features:
            if feature in df.columns:
                combined[f'{ticker}_{feature}'] = df[feature]

    combined_path = scenario_1_dir / 'combined_featured.parquet'
    combined.to_parquet(combined_path)
    print(f"  Saved combined: {combined_path.name} (shape: {combined.shape})")

    return all_featured_data


def engineer_features_scenario_2():
    """
    Feature engineering for Scenario 2: Sector Rotation Prediction
    """
    print("\n" + "=" * 80)
    print("FEATURE ENGINEERING SCENARIO 2: Sector Rotation Prediction")
    print("=" * 80)

    scenario_2_dir = PROCESSED_DIR / 'scenario_2'
    parquet_files = [f for f in scenario_2_dir.glob('*.parquet') if 'combined' not in f.name]

    print(f"\nEngineering features for {len(parquet_files)} tickers")

    all_featured_data = {}

    for filepath in sorted(parquet_files):
        ticker = filepath.stem
        print(f"\n  Processing {ticker}...")

        # Load processed data
        df = pd.read_parquet(filepath)

        # Apply feature engineering
        df_features = df.copy()

        # Returns
        df_features = create_returns(df_features, periods=[1, 5, 20])

        # Moving averages
        df_features = create_moving_averages(df_features, windows=[5, 10, 20])

        # Volatility
        df_features = create_volatility_features(df_features, windows=[5, 20])

        # Momentum
        df_features = create_momentum_features(df_features, windows=[5, 10, 20])

        # Volume (if available)
        if 'Volume' in df.columns:
            df_features = create_volume_features(df_features, windows=[5, 20])

        # Time features
        df_features = create_time_features(df_features)

        print(f"    Total features: {len(df_features.columns)}")

        all_featured_data[ticker] = df_features

    # Save featured data
    print(f"\nSaving featured data...")
    for ticker, df in all_featured_data.items():
        filepath = scenario_2_dir / f'{ticker}_featured.parquet'
        df.to_parquet(filepath)
        print(f"  Saved: {filepath.name}")

    # Create combined dataset
    combined = pd.DataFrame()
    for ticker, df in all_featured_data.items():
        important_features = ['Close', 'return_1d', 'return_5d', 'sma_20',
                              'volatility_20d', 'roc_5d']

        for feature in important_features:
            if feature in df.columns:
                combined[f'{ticker}_{feature}'] = df[feature]

    combined_path = scenario_2_dir / 'combined_featured.parquet'
    combined.to_parquet(combined_path)
    print(f"  Saved combined: {combined_path.name} (shape: {combined.shape})")

    return all_featured_data


def generate_feature_documentation():
    """
    Generate documentation of all features created
    """
    print("\n" + "=" * 80)
    print("GENERATING FEATURE DOCUMENTATION")
    print("=" * 80)

    doc = []
    doc.append("# Feature Engineering Documentation")
    doc.append(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

    doc.append("\n## Feature Categories")

    doc.append("\n### 1. Return Features")
    doc.append("- `return_1d`: 1-day simple return")
    doc.append("- `return_5d`: 5-day simple return")
    doc.append("- `return_20d`: 20-day simple return")
    doc.append("- `log_return_Nd`: Log returns for periods 1, 5, 20")

    doc.append("\n### 2. Moving Average Features")
    doc.append("- `sma_N`: Simple moving average (N = 5, 10, 20, 50)")
    doc.append("- `ema_N`: Exponential moving average (N = 5, 10, 20, 50)")
    doc.append("- `price_to_sma_N`: Normalized deviation from SMA")

    doc.append("\n### 3. Volatility Features")
    doc.append("- `volatility_Nd`: Rolling standard deviation of returns (N = 5, 20)")
    doc.append("- `hist_vol_Nd`: Annualized historical volatility")

    doc.append("\n### 4. Momentum Features")
    doc.append("- `roc_Nd`: Rate of change over N days (N = 5, 10, 20)")
    doc.append("- `momentum_Nd`: Simple price momentum")
    doc.append("- `rsi_14`: Relative Strength Index (14-day)")

    doc.append("\n### 5. Volume Features")
    doc.append("- `avg_volume_Nd`: Average volume over N days (N = 5, 20)")
    doc.append("- `volume_ratio_Nd`: Current volume / average volume")
    doc.append("- `volume_trend_5d`: Volume trend indicator")

    doc.append("\n### 6. Time Features")
    doc.append("- `day_of_week`: Day of week (0 = Monday, 4 = Friday)")
    doc.append("- `month`: Month (1-12)")
    doc.append("- `quarter`: Quarter (1-4)")
    doc.append("- `year`: Year")
    doc.append("- `days_since_epoch`: Days since 1970-01-01")
    doc.append("- `is_month_end`: Binary indicator for month end")
    doc.append("- `is_quarter_end`: Binary indicator for quarter end")

    doc.append("\n## Data Leakage Prevention")
    doc.append("\n**Critical:** All features use only historical data (no future information)")
    doc.append("- Moving averages: Calculated from past data only")
    doc.append("- Returns: Based on past prices")
    doc.append("- Volatility: Rolling windows look backwards only")

    doc.append("\n## Feature Engineering Pipeline")
    doc.append("\n1. Load preprocessed data")
    doc.append("2. Create return features")
    doc.append("3. Create moving averages")
    doc.append("4. Create volatility features")
    doc.append("5. Create momentum indicators")
    doc.append("6. Create volume features (if available)")
    doc.append("7. Create time features")
    doc.append("8. Save featured data")

    # Save documentation
    doc_path = DATA_DIR / 'FEATURES.md'
    with open(doc_path, 'w') as f:
        f.write('\n'.join(doc))

    print(f"\nFeature documentation saved to: {doc_path}")

    return doc_path


def main():
    """
    Main feature engineering function
    """
    print("=" * 80)
    print("MICE STOCK PREDICTION - FEATURE ENGINEERING")
    print("=" * 80)

    # Engineer features for all scenarios
    scenario_1_data = engineer_features_scenario_1()
    scenario_2_data = engineer_features_scenario_2()

    # Generate documentation
    doc_path = generate_feature_documentation()

    print("\n" + "=" * 80)
    print("FEATURE ENGINEERING COMPLETE")
    print("=" * 80)
    print(f"\nFeatured data saved to: {PROCESSED_DIR}")
    print(f"Feature documentation: {doc_path}")
    print("\nNext step: Create train/val/test splits (create_splits.py)")


if __name__ == '__main__':
    main()
