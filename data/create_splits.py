"""
Create Train/Validation/Test Splits for MICE Stock Prediction Experiment
Implements temporal splits to prevent data leakage
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
SPLITS_DIR = DATA_DIR / 'splits'


def create_temporal_split(df, train_end, val_end, scenario_name=''):
    """
    Create temporal train/validation/test splits

    Parameters:
    -----------
    df : DataFrame
        Featured data with datetime index
    train_end : str
        End date for training set (e.g., '2020-12-31')
    val_end : str
        End date for validation set (e.g., '2022-12-31')
    scenario_name : str
        Name for logging

    Returns:
    --------
    tuple : (train_df, val_df, test_df)
    """
    train_end = pd.Timestamp(train_end)
    val_end = pd.Timestamp(val_end)

    # Create splits
    train_df = df[df.index <= train_end]
    val_df = df[(df.index > train_end) & (df.index <= val_end)]
    test_df = df[df.index > val_end]

    # Validation
    print(f"\n  {scenario_name} splits:")
    print(f"    Train: {train_df.index[0].date()} to {train_df.index[-1].date()} ({len(train_df)} samples)")
    print(f"    Val:   {val_df.index[0].date()} to {val_df.index[-1].date()} ({len(val_df)} samples)")
    print(f"    Test:  {test_df.index[0].date()} to {test_df.index[-1].date()} ({len(test_df)} samples)")

    # Calculate percentages
    total = len(df)
    train_pct = (len(train_df) / total) * 100
    val_pct = (len(val_df) / total) * 100
    test_pct = (len(test_df) / total) * 100

    print(f"    Percentages: Train {train_pct:.1f}%, Val {val_pct:.1f}%, Test {test_pct:.1f}%")

    # Check for temporal leakage
    assert train_df.index.max() < val_df.index.min(), "Temporal leakage: train overlaps with val"
    assert val_df.index.max() < test_df.index.min(), "Temporal leakage: val overlaps with test"

    print(f"    ✓ No temporal leakage detected")

    return train_df, val_df, test_df


def create_splits_scenario_1():
    """
    Create splits for Scenario 1: Cross-Market Holiday Prediction

    Split specification:
    - Train: 2014-2020 (70%)
    - Val: 2021-2022 (20%)
    - Test: 2023-2024 (10%)
    """
    print("=" * 80)
    print("CREATING SPLITS SCENARIO 1: Cross-Market Holiday Prediction")
    print("=" * 80)

    scenario_1_dir = PROCESSED_DIR / 'scenario_1'

    # Load combined featured data
    combined_path = scenario_1_dir / 'combined_featured.parquet'
    print(f"\nLoading: {combined_path.name}")

    df = pd.read_parquet(combined_path)
    print(f"Total samples: {len(df)}")
    print(f"Date range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"Features: {len(df.columns)}")

    # Create splits
    train_df, val_df, test_df = create_temporal_split(
        df,
        train_end='2020-12-31',
        val_end='2022-12-31',
        scenario_name='Scenario 1'
    )

    # Save splits
    splits_scenario_1 = SPLITS_DIR / 'scenario_1'
    splits_scenario_1.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving splits to {splits_scenario_1}...")

    train_path = splits_scenario_1 / 'train.parquet'
    val_path = splits_scenario_1 / 'val.parquet'
    test_path = splits_scenario_1 / 'test.parquet'

    train_df.to_parquet(train_path)
    val_df.to_parquet(val_path)
    test_df.to_parquet(test_path)

    print(f"  Saved: train.parquet ({len(train_df)} rows)")
    print(f"  Saved: val.parquet ({len(val_df)} rows)")
    print(f"  Saved: test.parquet ({len(test_df)} rows)")

    # Also save individual ticker splits
    print(f"\nCreating splits for individual tickers...")

    ticker_files = [f for f in scenario_1_dir.glob('*_featured.parquet')]

    for filepath in sorted(ticker_files):
        ticker = filepath.stem.replace('_featured', '')

        df_ticker = pd.read_parquet(filepath)

        train_ticker, val_ticker, test_ticker = create_temporal_split(
            df_ticker,
            train_end='2020-12-31',
            val_end='2022-12-31',
            scenario_name=ticker
        )

        # Save
        train_ticker.to_parquet(splits_scenario_1 / f'{ticker}_train.parquet')
        val_ticker.to_parquet(splits_scenario_1 / f'{ticker}_val.parquet')
        test_ticker.to_parquet(splits_scenario_1 / f'{ticker}_test.parquet')

    print(f"\n  ✓ Created splits for {len(ticker_files)} individual tickers")

    return train_df, val_df, test_df


def create_splits_scenario_2():
    """
    Create splits for Scenario 2: Sector Rotation Prediction

    Split specification:
    - Train: 2019-2021 (60%)
    - Val: 2022 (20%)
    - Test: 2023-2024 (20%)
    """
    print("\n" + "=" * 80)
    print("CREATING SPLITS SCENARIO 2: Sector Rotation Prediction")
    print("=" * 80)

    scenario_2_dir = PROCESSED_DIR / 'scenario_2'

    # Load combined featured data
    combined_path = scenario_2_dir / 'combined_featured.parquet'
    print(f"\nLoading: {combined_path.name}")

    df = pd.read_parquet(combined_path)
    print(f"Total samples: {len(df)}")
    print(f"Date range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"Features: {len(df.columns)}")

    # Create splits
    train_df, val_df, test_df = create_temporal_split(
        df,
        train_end='2021-12-31',
        val_end='2022-12-31',
        scenario_name='Scenario 2'
    )

    # Save splits
    splits_scenario_2 = SPLITS_DIR / 'scenario_2'
    splits_scenario_2.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving splits to {splits_scenario_2}...")

    train_path = splits_scenario_2 / 'train.parquet'
    val_path = splits_scenario_2 / 'val.parquet'
    test_path = splits_scenario_2 / 'test.parquet'

    train_df.to_parquet(train_path)
    val_df.to_parquet(val_path)
    test_df.to_parquet(test_path)

    print(f"  Saved: train.parquet ({len(train_df)} rows)")
    print(f"  Saved: val.parquet ({len(val_df)} rows)")
    print(f"  Saved: test.parquet ({len(test_df)} rows)")

    # Also save individual ticker splits
    print(f"\nCreating splits for individual tickers...")

    ticker_files = [f for f in scenario_2_dir.glob('*_featured.parquet')]

    for filepath in sorted(ticker_files):
        ticker = filepath.stem.replace('_featured', '')

        df_ticker = pd.read_parquet(filepath)

        train_ticker, val_ticker, test_ticker = create_temporal_split(
            df_ticker,
            train_end='2021-12-31',
            val_end='2022-12-31',
            scenario_name=ticker
        )

        # Save
        train_ticker.to_parquet(splits_scenario_2 / f'{ticker}_train.parquet')
        val_ticker.to_parquet(splits_scenario_2 / f'{ticker}_val.parquet')
        test_ticker.to_parquet(splits_scenario_2 / f'{ticker}_test.parquet')

    print(f"\n  ✓ Created splits for {len(ticker_files)} individual tickers")

    return train_df, val_df, test_df


def validate_splits():
    """
    Validate that all splits are properly created and have no leakage
    """
    print("\n" + "=" * 80)
    print("VALIDATING SPLITS")
    print("=" * 80)

    validation_results = []

    scenarios = ['scenario_1', 'scenario_2']

    for scenario in scenarios:
        scenario_dir = SPLITS_DIR / scenario

        if not scenario_dir.exists():
            print(f"\n⚠️  {scenario} splits directory not found")
            continue

        print(f"\nValidating {scenario}...")

        # Check main splits exist
        required_files = ['train.parquet', 'val.parquet', 'test.parquet']
        for filename in required_files:
            filepath = scenario_dir / filename
            if not filepath.exists():
                print(f"  ❌ Missing: {filename}")
                validation_results.append(False)
            else:
                df = pd.read_parquet(filepath)
                print(f"  ✓ {filename}: {len(df)} rows, {len(df.columns)} features")
                validation_results.append(True)

        # Validate temporal ordering
        try:
            train_df = pd.read_parquet(scenario_dir / 'train.parquet')
            val_df = pd.read_parquet(scenario_dir / 'val.parquet')
            test_df = pd.read_parquet(scenario_dir / 'test.parquet')

            if train_df.index.max() >= val_df.index.min():
                print(f"  ❌ Temporal leakage: train overlaps with val")
                validation_results.append(False)
            elif val_df.index.max() >= test_df.index.min():
                print(f"  ❌ Temporal leakage: val overlaps with test")
                validation_results.append(False)
            else:
                print(f"  ✓ No temporal leakage")
                validation_results.append(True)

        except Exception as e:
            print(f"  ❌ Error validating splits: {str(e)}")
            validation_results.append(False)

    # Overall result
    print(f"\n{'=' * 80}")
    if all(validation_results):
        print("✓ ALL VALIDATIONS PASSED")
    else:
        print("❌ SOME VALIDATIONS FAILED")
        failed_count = sum(not r for r in validation_results)
        print(f"   Failed: {failed_count}/{len(validation_results)}")

    return all(validation_results)


def generate_split_report():
    """
    Generate a summary report of all splits
    """
    print("\n" + "=" * 80)
    print("GENERATING SPLIT REPORT")
    print("=" * 80)

    report = []
    report.append("# Train/Validation/Test Split Report")
    report.append(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\nRandom seed: 42")

    scenarios = ['scenario_1', 'scenario_2']

    for scenario in scenarios:
        scenario_dir = SPLITS_DIR / scenario

        if not scenario_dir.exists():
            continue

        report.append(f"\n## {scenario.replace('_', ' ').title()}")

        # Load main splits
        try:
            train_df = pd.read_parquet(scenario_dir / 'train.parquet')
            val_df = pd.read_parquet(scenario_dir / 'val.parquet')
            test_df = pd.read_parquet(scenario_dir / 'test.parquet')

            total = len(train_df) + len(val_df) + len(test_df)

            report.append(f"\n### Main Splits")
            report.append(f"- **Train:** {len(train_df)} samples ({(len(train_df)/total)*100:.1f}%)")
            report.append(f"  - Date range: {train_df.index[0].date()} to {train_df.index[-1].date()}")
            report.append(f"- **Validation:** {len(val_df)} samples ({(len(val_df)/total)*100:.1f}%)")
            report.append(f"  - Date range: {val_df.index[0].date()} to {val_df.index[-1].date()}")
            report.append(f"- **Test:** {len(test_df)} samples ({(len(test_df)/total)*100:.1f}%)")
            report.append(f"  - Date range: {test_df.index[0].date()} to {test_df.index[-1].date()}")
            report.append(f"- **Total:** {total} samples")
            report.append(f"- **Features:** {len(train_df.columns)}")

        except Exception as e:
            report.append(f"\nError loading splits: {str(e)}")

        # Count individual ticker splits
        ticker_files = list(scenario_dir.glob('*_train.parquet'))
        if ticker_files:
            report.append(f"\n### Individual Ticker Splits")
            report.append(f"- Number of tickers: {len(ticker_files)}")

    # Save report
    report_path = SPLITS_DIR / 'SPLIT_REPORT.md'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))

    print(f"\nSplit report saved to: {report_path}")

    return report_path


def main():
    """
    Main function to create all splits
    """
    print("=" * 80)
    print("MICE STOCK PREDICTION - CREATE TRAIN/VAL/TEST SPLITS")
    print("=" * 80)
    print("Using temporal splits to prevent data leakage")
    print("Random seed: 42\n")

    # Create splits for all scenarios
    scenario_1_splits = create_splits_scenario_1()
    scenario_2_splits = create_splits_scenario_2()

    # Validate splits
    validation_passed = validate_splits()

    # Generate report
    report_path = generate_split_report()

    print("\n" + "=" * 80)
    print("SPLIT CREATION COMPLETE")
    print("=" * 80)
    print(f"\nSplits saved to: {SPLITS_DIR}")
    print(f"Split report: {report_path}")
    print(f"Validation: {'✓ PASSED' if validation_passed else '❌ FAILED'}")
    print("\nNext step: Run data quality tests (tests/test_data_quality.py)")


if __name__ == '__main__':
    main()
