"""
Data Quality Tests for MICE Stock Prediction Experiment
Tests data integrity, temporal ordering, and feature validity
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
SPLITS_DIR = DATA_DIR / 'splits'


class TestDataExistence:
    """Test that all required data files exist"""

    def test_raw_data_scenario_1_exists(self):
        """Test that Scenario 1 raw data exists"""
        scenario_1_dir = DATA_DIR / 'raw' / 'scenario_1'
        assert scenario_1_dir.exists(), "Scenario 1 raw data directory not found"

        # Check for key files
        required_files = ['SPY.parquet', 'combined_daily.parquet', 'us_market_holidays.csv']
        for filename in required_files:
            filepath = scenario_1_dir / filename
            assert filepath.exists(), f"Missing file: {filename}"

    def test_raw_data_scenario_2_exists(self):
        """Test that Scenario 2 raw data exists"""
        scenario_2_dir = DATA_DIR / 'raw' / 'scenario_2'
        assert scenario_2_dir.exists(), "Scenario 2 raw data directory not found"

        # Check for sector ETFs
        sector_etfs = ['XLK', 'XLF', 'XLV', 'XLE', 'XLY', 'XLP', 'XLI', 'XLB', 'XLU', 'XLRE']
        for etf in sector_etfs:
            filepath = scenario_2_dir / f'{etf}.parquet'
            assert filepath.exists(), f"Missing ETF data: {etf}"

    def test_processed_data_exists(self):
        """Test that processed data exists"""
        assert PROCESSED_DIR.exists(), "Processed data directory not found"

        for scenario in ['scenario_1', 'scenario_2']:
            scenario_dir = PROCESSED_DIR / scenario
            assert scenario_dir.exists(), f"{scenario} processed data not found"

            # Check for combined file
            combined_file = scenario_dir / 'combined_daily.parquet'
            assert combined_file.exists(), f"Missing combined file for {scenario}"

    def test_splits_exist(self):
        """Test that train/val/test splits exist"""
        assert SPLITS_DIR.exists(), "Splits directory not found"

        for scenario in ['scenario_1', 'scenario_2']:
            scenario_dir = SPLITS_DIR / scenario
            assert scenario_dir.exists(), f"{scenario} splits not found"

            # Check for required split files
            required_files = ['train.parquet', 'val.parquet', 'test.parquet']
            for filename in required_files:
                filepath = scenario_dir / filename
                assert filepath.exists(), f"Missing {filename} for {scenario}"


class TestDataIntegrity:
    """Test data integrity and quality"""

    def test_no_duplicate_timestamps(self):
        """Test that there are no duplicate timestamps"""
        # Scenario 1
        df1 = pd.read_parquet(PROCESSED_DIR / 'scenario_1' / 'combined_daily.parquet')
        assert not df1.index.duplicated().any(), "Scenario 1 has duplicate timestamps"

        # Scenario 2
        df2 = pd.read_parquet(PROCESSED_DIR / 'scenario_2' / 'combined_daily.parquet')
        assert not df2.index.duplicated().any(), "Scenario 2 has duplicate timestamps"

    def test_no_negative_prices(self):
        """Test that there are no negative prices"""
        # Scenario 1
        scenario_1_files = list((PROCESSED_DIR / 'scenario_1').glob('*.parquet'))
        scenario_1_files = [f for f in scenario_1_files if 'combined' not in f.name
                            and 'featured' not in f.name]

        for filepath in scenario_1_files:
            df = pd.read_parquet(filepath)
            if 'Close' in df.columns:
                assert (df['Close'] >= 0).all(), f"Negative prices found in {filepath.name}"

        # Scenario 2
        scenario_2_files = list((PROCESSED_DIR / 'scenario_2').glob('*.parquet'))
        scenario_2_files = [f for f in scenario_2_files if 'combined' not in f.name
                            and 'featured' not in f.name]

        for filepath in scenario_2_files:
            df = pd.read_parquet(filepath)
            if 'Close' in df.columns:
                assert (df['Close'] >= 0).all(), f"Negative prices found in {filepath.name}"

    def test_missing_data_acceptable(self):
        """Test that missing data is within acceptable limits (<10%)"""
        # Scenario 1
        df1 = pd.read_parquet(PROCESSED_DIR / 'scenario_1' / 'combined_daily.parquet')
        missing_pct = (df1.isna().sum() / len(df1)) * 100

        for col in df1.columns:
            assert missing_pct[col] < 10, f"Scenario 1: {col} has {missing_pct[col]:.2f}% missing data"

        # Scenario 2
        df2 = pd.read_parquet(PROCESSED_DIR / 'scenario_2' / 'combined_daily.parquet')
        missing_pct = (df2.isna().sum() / len(df2)) * 100

        for col in df2.columns:
            assert missing_pct[col] < 10, f"Scenario 2: {col} has {missing_pct[col]:.2f}% missing data"

    def test_no_all_nan_columns(self):
        """Test that no columns are entirely NaN"""
        # Scenario 1
        df1 = pd.read_parquet(PROCESSED_DIR / 'scenario_1' / 'combined_daily.parquet')
        assert not df1.isna().all().any(), "Scenario 1 has all-NaN columns"

        # Scenario 2
        df2 = pd.read_parquet(PROCESSED_DIR / 'scenario_2' / 'combined_daily.parquet')
        assert not df2.isna().all().any(), "Scenario 2 has all-NaN columns"


class TestTemporalOrdering:
    """Test temporal ordering and no data leakage"""

    def test_splits_no_temporal_leakage(self):
        """Test that train/val/test splits have no temporal overlap"""
        for scenario in ['scenario_1', 'scenario_2']:
            scenario_dir = SPLITS_DIR / scenario

            train_df = pd.read_parquet(scenario_dir / 'train.parquet')
            val_df = pd.read_parquet(scenario_dir / 'val.parquet')
            test_df = pd.read_parquet(scenario_dir / 'test.parquet')

            # Check temporal ordering
            assert train_df.index.max() < val_df.index.min(), \
                f"{scenario}: Train overlaps with validation"

            assert val_df.index.max() < test_df.index.min(), \
                f"{scenario}: Validation overlaps with test"

    def test_splits_chronological_order(self):
        """Test that each split is in chronological order"""
        for scenario in ['scenario_1', 'scenario_2']:
            scenario_dir = SPLITS_DIR / scenario

            for split in ['train', 'val', 'test']:
                df = pd.read_parquet(scenario_dir / f'{split}.parquet')

                # Check that index is sorted
                assert df.index.is_monotonic_increasing, \
                    f"{scenario} {split} is not in chronological order"

    def test_scenario_1_date_ranges(self):
        """Test that Scenario 1 has correct date ranges"""
        scenario_dir = SPLITS_DIR / 'scenario_1'

        train_df = pd.read_parquet(scenario_dir / 'train.parquet')
        val_df = pd.read_parquet(scenario_dir / 'val.parquet')
        test_df = pd.read_parquet(scenario_dir / 'test.parquet')

        # Check train ends in 2020
        assert train_df.index.max().year == 2020, "Train should end in 2020"

        # Check val is 2021-2022
        assert val_df.index.min().year == 2021, "Val should start in 2021"
        assert val_df.index.max().year == 2022, "Val should end in 2022"

        # Check test is 2023-2024
        assert test_df.index.min().year == 2023, "Test should start in 2023"
        assert test_df.index.max().year == 2024, "Test should end in 2024"

    def test_scenario_2_date_ranges(self):
        """Test that Scenario 2 has correct date ranges"""
        scenario_dir = SPLITS_DIR / 'scenario_2'

        train_df = pd.read_parquet(scenario_dir / 'train.parquet')
        val_df = pd.read_parquet(scenario_dir / 'val.parquet')
        test_df = pd.read_parquet(scenario_dir / 'test.parquet')

        # Check train ends in 2021
        assert train_df.index.max().year == 2021, "Train should end in 2021"

        # Check val is 2022
        assert val_df.index.min().year == 2022, "Val should start in 2022"
        assert val_df.index.max().year == 2022, "Val should end in 2022"

        # Check test is 2023-2024
        assert test_df.index.min().year == 2023, "Test should start in 2023"
        assert test_df.index.max().year == 2024, "Test should end in 2024"


class TestFeatureValidity:
    """Test that features are valid and within expected ranges"""

    def test_features_exist(self):
        """Test that expected features exist in featured data"""
        # Load featured data
        df1 = pd.read_parquet(PROCESSED_DIR / 'scenario_1' / 'combined_featured.parquet')

        # Check for key features
        expected_features = ['SPY_Close', 'SPY_return_1d', 'SPY_sma_20', 'SPY_volatility_20d']

        for feature in expected_features:
            assert feature in df1.columns, f"Missing feature: {feature}"

    def test_return_features_reasonable(self):
        """Test that return features are within reasonable bounds"""
        # Load a featured dataset
        df = pd.read_parquet(PROCESSED_DIR / 'scenario_1' / 'SPY_featured.parquet')

        if 'return_1d' in df.columns:
            # Daily returns should generally be within -20% to +20%
            # (allowing for extreme events)
            returns = df['return_1d'].dropna()
            assert (returns.abs() < 0.5).sum() / len(returns) > 0.95, \
                "More than 5% of returns are extreme (>50%)"

    def test_moving_averages_positive(self):
        """Test that moving averages are positive for price data"""
        df = pd.read_parquet(PROCESSED_DIR / 'scenario_1' / 'SPY_featured.parquet')

        # Select only actual MA columns, not price_to_sma (which can be negative)
        ma_columns = [col for col in df.columns
                      if ('sma_' in col or 'ema_' in col)
                      and 'price_to_sma' not in col]

        for col in ma_columns:
            non_nan_values = df[col].dropna()
            if len(non_nan_values) > 0:
                assert (non_nan_values > 0).all(), f"{col} has non-positive values"

    def test_rsi_in_range(self):
        """Test that RSI is between 0 and 100"""
        df = pd.read_parquet(PROCESSED_DIR / 'scenario_1' / 'SPY_featured.parquet')

        if 'rsi_14' in df.columns:
            rsi = df['rsi_14'].dropna()
            assert (rsi >= 0).all() and (rsi <= 100).all(), "RSI out of range [0, 100]"

    def test_time_features_valid(self):
        """Test that time features have valid values"""
        df = pd.read_parquet(PROCESSED_DIR / 'scenario_1' / 'SPY_featured.parquet')

        # Day of week should be 0-4 (Monday-Friday for business days)
        if 'day_of_week' in df.columns:
            assert df['day_of_week'].min() >= 0, "Invalid day_of_week (< 0)"
            assert df['day_of_week'].max() <= 6, "Invalid day_of_week (> 6)"

        # Month should be 1-12
        if 'month' in df.columns:
            assert df['month'].min() >= 1, "Invalid month (< 1)"
            assert df['month'].max() <= 12, "Invalid month (> 12)"

        # Quarter should be 1-4
        if 'quarter' in df.columns:
            assert df['quarter'].min() >= 1, "Invalid quarter (< 1)"
            assert df['quarter'].max() <= 4, "Invalid quarter (> 4)"


class TestSplitSizes:
    """Test that splits have reasonable sizes"""

    def test_split_size_proportions(self):
        """Test that splits have approximately correct proportions"""
        for scenario in ['scenario_1', 'scenario_2']:
            scenario_dir = SPLITS_DIR / scenario

            train_df = pd.read_parquet(scenario_dir / 'train.parquet')
            val_df = pd.read_parquet(scenario_dir / 'val.parquet')
            test_df = pd.read_parquet(scenario_dir / 'test.parquet')

            total = len(train_df) + len(val_df) + len(test_df)

            train_pct = (len(train_df) / total) * 100
            val_pct = (len(val_df) / total) * 100
            test_pct = (len(test_df) / total) * 100

            # Train should be at least 50%
            assert train_pct >= 50, f"{scenario}: Train set too small ({train_pct:.1f}%)"

            # Val should be at least 10%
            assert val_pct >= 10, f"{scenario}: Validation set too small ({val_pct:.1f}%)"

            # Test should be at least 10%
            assert test_pct >= 10, f"{scenario}: Test set too small ({test_pct:.1f}%)"

    def test_minimum_samples(self):
        """Test that each split has minimum number of samples"""
        min_samples = 100  # Minimum for meaningful statistics

        for scenario in ['scenario_1', 'scenario_2']:
            scenario_dir = SPLITS_DIR / scenario

            for split in ['train', 'val', 'test']:
                df = pd.read_parquet(scenario_dir / f'{split}.parquet')
                assert len(df) >= min_samples, \
                    f"{scenario} {split} has fewer than {min_samples} samples"


class TestHolidayData:
    """Test holiday-specific data for Scenario 1"""

    def test_holidays_file_exists(self):
        """Test that US market holidays file exists"""
        holidays_path = DATA_DIR / 'raw' / 'scenario_1' / 'us_market_holidays.csv'
        assert holidays_path.exists(), "US market holidays file not found"

    def test_holidays_count_reasonable(self):
        """Test that number of holidays is reasonable"""
        holidays_path = DATA_DIR / 'raw' / 'scenario_1' / 'us_market_holidays.csv'
        holidays_df = pd.read_csv(holidays_path)

        # Should have approximately 8-12 holidays per year for 10 years
        num_holidays = len(holidays_df)
        assert 50 <= num_holidays <= 150, \
            f"Unexpected number of holidays: {num_holidays} (expected 50-150)"


def test_data_reports_exist():
    """Test that data quality reports exist"""
    # Check for data report
    data_report = DATA_DIR / 'DATA_REPORT.md'
    assert data_report.exists(), "DATA_REPORT.md not found"

    # Check for quality report
    quality_report = PROCESSED_DIR / 'QUALITY_REPORT.md'
    assert quality_report.exists(), "QUALITY_REPORT.md not found"

    # Check for feature documentation
    features_doc = DATA_DIR / 'FEATURES.md'
    assert features_doc.exists(), "FEATURES.md not found"

    # Check for split report
    split_report = SPLITS_DIR / 'SPLIT_REPORT.md'
    assert split_report.exists(), "SPLIT_REPORT.md not found"


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])
