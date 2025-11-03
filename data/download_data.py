"""
Data Download Script for MICE Stock Prediction Experiment
Downloads data for all three scenarios
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

# Define paths
DATA_DIR = Path(__file__).parent
RAW_DIR = DATA_DIR / 'raw'


def download_scenario_1():
    """
    Scenario 1: Cross-Market Holiday Prediction
    Download 10 years of daily data (2014-2024)
    """
    print("=" * 80)
    print("SCENARIO 1: Cross-Market Holiday Prediction")
    print("=" * 80)

    # Define tickers
    tickers = {
        'SPY': 'S&P 500 ETF (Target)',
        'EWJ': 'Japan ETF (Nikkei 225 proxy)',
        'EWG': 'Germany ETF (DAX proxy)',
        'EWU': 'UK ETF (FTSE 100 proxy)',
        'EWH': 'Hong Kong ETF (Hang Seng proxy)',
        '^VIX': 'Volatility Index',
        'DX-Y.NYB': 'US Dollar Index',
        'GLD': 'Gold ETF',
        'USO': 'Oil ETF',
        '^TNX': '10-Year Treasury Yield'
    }

    # Date range
    start_date = '2014-01-01'
    end_date = '2024-12-31'

    print(f"\nDownloading data from {start_date} to {end_date}")
    print(f"Tickers: {len(tickers)}")

    # Download data
    all_data = {}
    failed_tickers = []

    for ticker, description in tickers.items():
        try:
            print(f"\nDownloading {ticker}: {description}...")
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)

            if data.empty:
                print(f"  ⚠️  No data returned for {ticker}")
                failed_tickers.append(ticker)
            else:
                all_data[ticker] = data
                print(f"  ✓ Downloaded {len(data)} rows")
                print(f"    Date range: {data.index[0]} to {data.index[-1]}")
                print(f"    Columns: {list(data.columns)}")

                # Check for missing data
                missing_pct = (data['Close'].isna().sum() / len(data)) * 100
                print(f"    Missing data: {missing_pct:.2f}%")

        except Exception as e:
            print(f"  ❌ Error downloading {ticker}: {str(e)}")
            failed_tickers.append(ticker)

    # Save individual ticker data
    scenario_1_dir = RAW_DIR / 'scenario_1'
    scenario_1_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 80}")
    print("Saving data...")

    for ticker, data in all_data.items():
        # Clean ticker name for filename
        clean_ticker = ticker.replace('^', '').replace('-', '_').replace('.', '_')
        filepath = scenario_1_dir / f'{clean_ticker}.parquet'
        data.to_parquet(filepath)
        print(f"  Saved: {filepath.name}")

    # Create combined dataset
    print("\nCreating combined dataset...")
    close_prices = pd.DataFrame()

    for ticker, data in all_data.items():
        clean_ticker = ticker.replace('^', '').replace('-', '_').replace('.', '_')
        close_prices[clean_ticker] = data['Close']

    # Save combined dataset
    combined_path = scenario_1_dir / 'combined_daily.parquet'
    close_prices.to_parquet(combined_path)
    print(f"  Saved combined: {combined_path.name}")
    print(f"  Shape: {close_prices.shape}")

    # Identify US market holidays (days when SPY didn't trade)
    print("\nIdentifying US market holidays...")

    # Create full date range
    full_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # Get SPY trading days
    spy_data = all_data['SPY']
    spy_trading_days = set(spy_data.index.date)

    # Find weekdays where SPY didn't trade (holidays)
    holidays = []
    for date in full_range:
        # Skip weekends
        if date.weekday() < 5:  # Monday = 0, Friday = 4
            if date.date() not in spy_trading_days:
                holidays.append(date)

    holidays_df = pd.DataFrame({'holiday_date': holidays})
    holidays_path = scenario_1_dir / 'us_market_holidays.csv'
    holidays_df.to_csv(holidays_path, index=False)

    print(f"  Found {len(holidays)} US market holidays")
    print(f"  Saved to: {holidays_path.name}")
    print(f"  Average holidays per year: {len(holidays) / 10:.1f}")

    # Summary statistics
    print(f"\n{'=' * 80}")
    print("SCENARIO 1 SUMMARY")
    print(f"{'=' * 80}")
    print(f"Successfully downloaded: {len(all_data)}/{len(tickers)} tickers")
    print(f"Failed tickers: {failed_tickers if failed_tickers else 'None'}")
    print(f"Combined dataset shape: {close_prices.shape}")
    print(f"Date range: {close_prices.index[0]} to {close_prices.index[-1]}")
    print(f"US market holidays identified: {len(holidays)}")

    return all_data, close_prices, holidays


def download_scenario_2():
    """
    Scenario 2: Sector Rotation Prediction
    Download 5 years of daily data (2019-2024)
    """
    print("\n" + "=" * 80)
    print("SCENARIO 2: Sector Rotation Prediction")
    print("=" * 80)

    # Define sector ETFs
    sector_etfs = {
        'XLK': 'Technology',
        'XLF': 'Financials',
        'XLV': 'Healthcare',
        'XLE': 'Energy',
        'XLY': 'Consumer Discretionary',
        'XLP': 'Consumer Staples',
        'XLI': 'Industrials',
        'XLB': 'Materials',
        'XLU': 'Utilities',
        'XLRE': 'Real Estate'
    }

    # Date range
    start_date = '2019-01-01'
    end_date = '2024-12-31'

    print(f"\nDownloading sector ETFs from {start_date} to {end_date}")

    # Download sector ETFs
    sector_data = {}
    for ticker, sector in sector_etfs.items():
        try:
            print(f"\nDownloading {ticker}: {sector}...")
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            sector_data[ticker] = data
            print(f"  ✓ Downloaded {len(data)} rows")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

    # Download SPY and VIX
    print("\nDownloading market indicators...")
    for ticker in ['SPY', '^VIX']:
        try:
            print(f"  Downloading {ticker}...")
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            sector_data[ticker] = data
            print(f"    ✓ {len(data)} rows")
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")

    # Save sector ETF data
    scenario_2_dir = RAW_DIR / 'scenario_2'
    scenario_2_dir.mkdir(parents=True, exist_ok=True)

    print("\nSaving sector ETF data...")
    for ticker, data in sector_data.items():
        clean_ticker = ticker.replace('^', '')
        filepath = scenario_2_dir / f'{clean_ticker}.parquet'
        data.to_parquet(filepath)
        print(f"  Saved: {filepath.name}")

    # For now, we'll document the process for selecting small-cap stocks
    # This requires additional filtering by market cap and liquidity
    print("\n" + "-" * 80)
    print("NOTE: Small-cap stock selection")
    print("-" * 80)
    print("200 small-cap stocks ($500M-$5B market cap) need to be selected")
    print("Selection criteria:")
    print("  - 20 stocks per sector")
    print("  - Market cap: $500M - $5B")
    print("  - Top by average daily volume")
    print("  - No delistings during 2019-2024")
    print("\nThis requires additional API access or manual selection.")
    print("For proof of concept, we'll use sector ETFs and top stocks.")

    # Summary
    print(f"\n{'=' * 80}")
    print("SCENARIO 2 SUMMARY")
    print(f"{'=' * 80}")
    print(f"Sector ETFs downloaded: {len([t for t in sector_data if t in sector_etfs])}/10")
    print(f"Market indicators downloaded: {len([t for t in sector_data if t not in sector_etfs])}")
    print(f"Total tickers: {len(sector_data)}")

    return sector_data


def download_scenario_3():
    """
    Scenario 3: Intraday Illiquidity Gaps
    NOTE: This requires API access to Polygon.io or Alpaca
    """
    print("\n" + "=" * 80)
    print("SCENARIO 3: Intraday Illiquidity (Not implemented yet)")
    print("=" * 80)

    print("\nThis scenario requires minute-level intraday data.")
    print("Options:")
    print("  1. Polygon.io API (requires paid subscription)")
    print("  2. Alpaca API (free tier available)")
    print("  3. Yahoo Finance intraday (limited history)")

    print("\nFor Sprint 1, we'll defer this to focus on daily data scenarios.")
    print("Action item: Set up API access for Sprint 2")

    scenario_3_dir = RAW_DIR / 'scenario_3'
    scenario_3_dir.mkdir(parents=True, exist_ok=True)

    # Create placeholder
    placeholder_path = scenario_3_dir / 'README.md'
    with open(placeholder_path, 'w') as f:
        f.write("# Scenario 3: Intraday Data\n\n")
        f.write("This directory will contain 1-minute bar data for 2024.\n\n")
        f.write("Requirements:\n")
        f.write("- 25 liquid stocks (top S&P 500 by volume)\n")
        f.write("- 25 illiquid stocks ($500M-$2B, spread >0.5%)\n")
        f.write("- 1-minute bars for 2024\n\n")
        f.write("API options: Polygon.io, Alpaca, or Yahoo Finance\n")

    print(f"Created placeholder: {placeholder_path}")

    return None


def generate_data_report():
    """
    Generate a summary report of all downloaded data
    """
    print("\n" + "=" * 80)
    print("GENERATING DATA SUMMARY REPORT")
    print("=" * 80)

    report = []
    report.append("# Data Download Report")
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n## Summary")

    # Check each scenario
    scenarios = ['scenario_1', 'scenario_2', 'scenario_3']

    for scenario in scenarios:
        scenario_dir = RAW_DIR / scenario
        if scenario_dir.exists():
            files = list(scenario_dir.glob('*.parquet'))
            report.append(f"\n### {scenario.replace('_', ' ').title()}")
            report.append(f"- Location: `{scenario_dir}`")
            report.append(f"- Files: {len(files)}")

            if files:
                report.append(f"- Tickers:")
                for f in sorted(files):
                    report.append(f"  - {f.stem}")

    # Save report
    report_path = DATA_DIR / 'DATA_REPORT.md'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))

    print(f"\nReport saved to: {report_path}")
    print("\n".join(report))

    return report_path


def main():
    """
    Main function to download all data
    """
    print("=" * 80)
    print("MICE STOCK PREDICTION - DATA DOWNLOAD")
    print("=" * 80)
    print(f"Random seed: 42")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Download all scenarios
    try:
        scenario_1_data, combined_df, holidays = download_scenario_1()
    except Exception as e:
        print(f"\n❌ Error in Scenario 1: {str(e)}")
        scenario_1_data = None

    try:
        scenario_2_data = download_scenario_2()
    except Exception as e:
        print(f"\n❌ Error in Scenario 2: {str(e)}")
        scenario_2_data = None

    try:
        scenario_3_data = download_scenario_3()
    except Exception as e:
        print(f"\n❌ Error in Scenario 3: {str(e)}")
        scenario_3_data = None

    # Generate report
    report_path = generate_data_report()

    print("\n" + "=" * 80)
    print("DATA DOWNLOAD COMPLETE")
    print("=" * 80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nNext steps:")
    print("  1. Review data quality report")
    print("  2. Run preprocessing pipeline (preprocess.py)")
    print("  3. Create train/val/test splits (create_splits.py)")


if __name__ == '__main__':
    main()
