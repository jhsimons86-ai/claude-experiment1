"""
Generate Sample Data for MICE Stock Prediction Experiment
This creates realistic synthetic data for testing the pipeline
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

# Define paths
DATA_DIR = Path(__file__).parent
RAW_DIR = DATA_DIR / 'raw'


def generate_correlated_returns(n_assets, n_days, correlation=0.3):
    """
    Generate correlated returns for multiple assets
    """
    # Create correlation matrix
    corr_matrix = np.full((n_assets, n_assets), correlation)
    np.fill_diagonal(corr_matrix, 1.0)

    # Generate correlated random returns
    mean_returns = np.zeros(n_assets)
    std_returns = np.ones(n_assets) * 0.015  # 1.5% daily volatility

    # Cholesky decomposition for correlated samples
    L = np.linalg.cholesky(corr_matrix)
    uncorrelated = np.random.standard_normal((n_days, n_assets))
    returns = uncorrelated @ L.T * std_returns + mean_returns

    return returns


def generate_price_series(initial_price, returns):
    """
    Convert returns to price series
    """
    price_multipliers = np.exp(np.cumsum(returns, axis=0))
    prices = initial_price * price_multipliers
    return prices


def generate_scenario_1():
    """
    Scenario 1: Cross-Market Holiday Prediction
    Generate 10 years of daily data (2014-2024)
    """
    print("=" * 80)
    print("GENERATING SCENARIO 1: Cross-Market Holiday Prediction")
    print("=" * 80)

    # Date range
    start_date = pd.Timestamp('2014-01-01')
    end_date = pd.Timestamp('2024-12-31')

    # Generate business days (Monday-Friday)
    date_range = pd.bdate_range(start=start_date, end=end_date, freq='B')
    n_days = len(date_range)

    print(f"\nGenerating {n_days} trading days from {start_date.date()} to {end_date.date()}")

    # Define assets
    assets = ['SPY', 'EWJ', 'EWG', 'EWU', 'EWH', 'VIX', 'DX_Y_NYB', 'GLD', 'USO', 'TNX']
    initial_prices = [200, 50, 25, 30, 22, 15, 95, 120, 30, 2.5]

    # Generate correlated returns (markets are correlated)
    returns = generate_correlated_returns(len(assets), n_days, correlation=0.4)

    # VIX should be negatively correlated with SPY
    returns[:, 5] = -0.5 * returns[:, 0] + 0.3 * np.random.randn(n_days)

    # Generate price series
    all_data = {}

    for i, asset in enumerate(assets):
        prices = generate_price_series(initial_prices[i], returns[:, i])

        # Create OHLCV data
        df = pd.DataFrame(index=date_range)
        df['Open'] = prices * (1 + np.random.randn(n_days) * 0.005)
        df['High'] = np.maximum(df['Open'], prices) * (1 + np.abs(np.random.randn(n_days)) * 0.003)
        df['Low'] = np.minimum(df['Open'], prices) * (1 - np.abs(np.random.randn(n_days)) * 0.003)
        df['Close'] = prices
        df['Volume'] = np.random.lognormal(15, 0.5, n_days)
        df['Adj Close'] = prices

        all_data[asset] = df
        print(f"  Generated {asset}: {len(df)} rows, price range ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")

    # Save individual ticker data
    scenario_1_dir = RAW_DIR / 'scenario_1'
    scenario_1_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving data to {scenario_1_dir}...")

    for asset, data in all_data.items():
        filepath = scenario_1_dir / f'{asset}.parquet'
        data.to_parquet(filepath)
        print(f"  Saved: {filepath.name}")

    # Create combined dataset
    close_prices = pd.DataFrame()
    for asset, data in all_data.items():
        close_prices[asset] = data['Close']

    combined_path = scenario_1_dir / 'combined_daily.parquet'
    close_prices.to_parquet(combined_path)
    print(f"  Saved combined: {combined_path.name} (shape: {close_prices.shape})")

    # Generate US market holidays (approximately 10 per year)
    # Major holidays: New Year's, MLK Day, Presidents Day, Good Friday, Memorial Day,
    # Independence Day, Labor Day, Thanksgiving, Christmas
    holidays = []

    for year in range(2014, 2025):
        # Fixed date holidays
        holidays.append(pd.Timestamp(f'{year}-01-01'))  # New Year's
        holidays.append(pd.Timestamp(f'{year}-07-04'))  # Independence Day
        holidays.append(pd.Timestamp(f'{year}-12-25'))  # Christmas

        # Third Monday of January (MLK Day)
        jan_mondays = pd.date_range(f'{year}-01-01', f'{year}-01-31', freq='W-MON')
        if len(jan_mondays) >= 3:
            holidays.append(jan_mondays[2])

        # Third Monday of February (Presidents Day)
        feb_mondays = pd.date_range(f'{year}-02-01', f'{year}-02-28', freq='W-MON')
        if len(feb_mondays) >= 3:
            holidays.append(feb_mondays[2])

        # Last Monday of May (Memorial Day)
        may_mondays = pd.date_range(f'{year}-05-01', f'{year}-05-31', freq='W-MON')
        if len(may_mondays) >= 1:
            holidays.append(may_mondays[-1])

        # First Monday of September (Labor Day)
        sep_mondays = pd.date_range(f'{year}-09-01', f'{year}-09-30', freq='W-MON')
        if len(sep_mondays) >= 1:
            holidays.append(sep_mondays[0])

        # Fourth Thursday of November (Thanksgiving)
        nov_thursdays = pd.date_range(f'{year}-11-01', f'{year}-11-30', freq='W-THU')
        if len(nov_thursdays) >= 4:
            holidays.append(nov_thursdays[3])

    # Remove duplicates and filter to business days
    holidays = sorted(set(h for h in holidays if h.weekday() < 5))

    holidays_df = pd.DataFrame({'holiday_date': holidays})
    holidays_path = scenario_1_dir / 'us_market_holidays.csv'
    holidays_df.to_csv(holidays_path, index=False)

    print(f"\n  Generated {len(holidays)} US market holidays")
    print(f"  Saved to: {holidays_path.name}")

    print(f"\n{'=' * 80}")
    print("SCENARIO 1 COMPLETE")
    print(f"{'=' * 80}")
    print(f"Assets: {len(all_data)}")
    print(f"Trading days: {n_days}")
    print(f"Holidays: {len(holidays)}")

    return all_data, close_prices, holidays


def generate_scenario_2():
    """
    Scenario 2: Sector Rotation Prediction
    Generate 5 years of daily data (2019-2024)
    """
    print("\n" + "=" * 80)
    print("GENERATING SCENARIO 2: Sector Rotation Prediction")
    print("=" * 80)

    # Date range
    start_date = pd.Timestamp('2019-01-01')
    end_date = pd.Timestamp('2024-12-31')
    date_range = pd.bdate_range(start=start_date, end=end_date, freq='B')
    n_days = len(date_range)

    print(f"\nGenerating {n_days} trading days from {start_date.date()} to {end_date.date()}")

    # Define sector ETFs
    sectors = ['XLK', 'XLF', 'XLV', 'XLE', 'XLY', 'XLP', 'XLI', 'XLB', 'XLU', 'XLRE']
    sector_names = ['Technology', 'Financials', 'Healthcare', 'Energy', 'Consumer Discretionary',
                    'Consumer Staples', 'Industrials', 'Materials', 'Utilities', 'Real Estate']

    # Generate sector returns (some correlation between sectors)
    sector_returns = generate_correlated_returns(len(sectors), n_days, correlation=0.25)

    # Generate sector ETF data
    all_data = {}

    for i, sector in enumerate(sectors):
        prices = generate_price_series(100, sector_returns[:, i])

        df = pd.DataFrame(index=date_range)
        df['Open'] = prices * (1 + np.random.randn(n_days) * 0.005)
        df['High'] = np.maximum(df['Open'], prices) * (1 + np.abs(np.random.randn(n_days)) * 0.003)
        df['Low'] = np.minimum(df['Open'], prices) * (1 - np.abs(np.random.randn(n_days)) * 0.003)
        df['Close'] = prices
        df['Volume'] = np.random.lognormal(15, 0.5, n_days)
        df['Adj Close'] = prices

        all_data[sector] = df
        print(f"  Generated {sector} ({sector_names[i]}): {len(df)} rows")

    # Add SPY and VIX
    spy_returns = sector_returns.mean(axis=1)  # SPY is average of sectors
    spy_prices = generate_price_series(280, spy_returns)

    spy_df = pd.DataFrame(index=date_range)
    spy_df['Open'] = spy_prices * (1 + np.random.randn(n_days) * 0.005)
    spy_df['High'] = np.maximum(spy_df['Open'], spy_prices) * (1 + np.abs(np.random.randn(n_days)) * 0.003)
    spy_df['Low'] = np.minimum(spy_df['Open'], spy_prices) * (1 - np.abs(np.random.randn(n_days)) * 0.003)
    spy_df['Close'] = spy_prices
    spy_df['Volume'] = np.random.lognormal(16, 0.5, n_days)
    spy_df['Adj Close'] = spy_prices
    all_data['SPY'] = spy_df

    vix_returns = -0.5 * spy_returns + 0.3 * np.random.randn(n_days)
    vix_prices = generate_price_series(16, vix_returns)
    vix_df = pd.DataFrame(index=date_range)
    vix_df['Close'] = np.abs(vix_prices)  # VIX is always positive
    all_data['VIX'] = vix_df

    print(f"  Generated SPY and VIX")

    # Save data
    scenario_2_dir = RAW_DIR / 'scenario_2'
    scenario_2_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving data to {scenario_2_dir}...")

    for ticker, data in all_data.items():
        filepath = scenario_2_dir / f'{ticker}.parquet'
        data.to_parquet(filepath)
        print(f"  Saved: {filepath.name}")

    # Note about small-cap stocks
    print("\n" + "-" * 80)
    print("NOTE: For proof of concept, using sector ETFs only.")
    print("In production, would include 200 small-cap stocks (20 per sector).")
    print("-" * 80)

    print(f"\n{'=' * 80}")
    print("SCENARIO 2 COMPLETE")
    print(f"{'=' * 80}")
    print(f"Sector ETFs: {len(sectors)}")
    print(f"Total tickers: {len(all_data)}")
    print(f"Trading days: {n_days}")

    return all_data


def generate_scenario_3_placeholder():
    """
    Scenario 3: Create placeholder for intraday data
    """
    print("\n" + "=" * 80)
    print("SCENARIO 3: Intraday Illiquidity (Placeholder)")
    print("=" * 80)

    scenario_3_dir = RAW_DIR / 'scenario_3'
    scenario_3_dir.mkdir(parents=True, exist_ok=True)

    placeholder_path = scenario_3_dir / 'README.md'
    with open(placeholder_path, 'w') as f:
        f.write("# Scenario 3: Intraday Data\n\n")
        f.write("This directory will contain 1-minute bar data for 2024.\n\n")
        f.write("Requirements:\n")
        f.write("- 25 liquid stocks (top S&P 500 by volume)\n")
        f.write("- 25 illiquid stocks ($500M-$2B, spread >0.5%)\n")
        f.write("- 1-minute bars for 2024\n\n")
        f.write("Status: Deferred to Sprint 2\n")

    print(f"Created placeholder: {placeholder_path}")

    return None


def generate_data_report():
    """
    Generate a summary report of all generated data
    """
    print("\n" + "=" * 80)
    print("GENERATING DATA SUMMARY REPORT")
    print("=" * 80)

    report = []
    report.append("# Data Generation Report")
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\nRandom Seed: 42")
    report.append("\n## Summary")

    scenarios = ['scenario_1', 'scenario_2', 'scenario_3']

    for scenario in scenarios:
        scenario_dir = RAW_DIR / scenario
        if scenario_dir.exists():
            parquet_files = list(scenario_dir.glob('*.parquet'))
            csv_files = list(scenario_dir.glob('*.csv'))

            report.append(f"\n### {scenario.replace('_', ' ').title()}")
            report.append(f"- Location: `{scenario_dir}`")
            report.append(f"- Parquet files: {len(parquet_files)}")
            report.append(f"- CSV files: {len(csv_files)}")

            if parquet_files:
                report.append(f"- Tickers:")
                for f in sorted(parquet_files):
                    # Load and get info
                    df = pd.read_parquet(f)
                    report.append(f"  - {f.stem}: {len(df)} rows, {df.index[0].date()} to {df.index[-1].date()}")

    report_path = DATA_DIR / 'DATA_REPORT.md'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))

    print(f"\nReport saved to: {report_path}")

    return report_path


def main():
    """
    Main function to generate all sample data
    """
    print("=" * 80)
    print("MICE STOCK PREDICTION - SAMPLE DATA GENERATION")
    print("=" * 80)
    print(f"Random seed: 42")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Generate all scenarios
    scenario_1_data, combined_df, holidays = generate_scenario_1()
    scenario_2_data = generate_scenario_2()
    scenario_3_data = generate_scenario_3_placeholder()

    # Generate report
    report_path = generate_data_report()

    print("\n" + "=" * 80)
    print("SAMPLE DATA GENERATION COMPLETE")
    print("=" * 80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nGenerated realistic synthetic data for:")
    print("  ✓ Scenario 1: 10 years daily cross-market data")
    print("  ✓ Scenario 2: 5 years daily sector rotation data")
    print("  ○ Scenario 3: Placeholder (requires intraday API)")
    print(f"\nData report: {report_path}")
    print("\nNext steps:")
    print("  1. Review data quality report")
    print("  2. Run preprocessing pipeline (preprocess.py)")
    print("  3. Create train/val/test splits (create_splits.py)")


if __name__ == '__main__':
    main()
