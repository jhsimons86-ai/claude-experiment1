"""
Scenario 2: Sector Rotation Prediction
Run all baseline models on sector ETF data
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from models.baselines import (
    ForwardFillBaseline,
    LinearInterpolationBaseline,
    HistoricalMeanBaseline,
    ARIMABaseline,
    RandomForestBaseline
)
from models.evaluation import evaluate_model, create_comparison_table, save_results

# Set random seed
np.random.seed(42)

# Define paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
SPLITS_DIR = DATA_DIR / 'splits' / 'scenario_2'
RESULTS_DIR = BASE_DIR / 'results'


def load_data():
    """Load train/val/test splits for Scenario 2"""
    print("Loading data...")

    train_df = pd.read_parquet(SPLITS_DIR / 'train.parquet')
    val_df = pd.read_parquet(SPLITS_DIR / 'val.parquet')
    test_df = pd.read_parquet(SPLITS_DIR / 'test.parquet')

    print(f"  Train: {len(train_df)} samples")
    print(f"  Val: {len(val_df)} samples")
    print(f"  Test: {len(test_df)} samples")

    return train_df, val_df, test_df


def prepare_features(df, target_col='XLK_Close'):
    """
    Prepare features and target

    For Scenario 2, we'll predict Technology sector (XLK) using other sectors
    """
    y = df[target_col]
    feature_cols = [col for col in df.columns if col != target_col]
    X = df[feature_cols]

    return X, y


def run_baseline(baseline, X_train, y_train, X_test, y_test, y_previous=None, y_current=None):
    """Run a single baseline model"""
    print(f"\n{'='*60}")
    print(f"Running {baseline.name}...")
    print(f"{'='*60}")

    try:
        # Fit model
        print("  Fitting model...")
        baseline.fit(X_train, y_train)
        print(f"  ✓ Model fitted")

        # Evaluate
        print("  Evaluating...")
        results = evaluate_model(baseline, X_test, y_test, y_previous, y_current)

        print(f"  ✓ Evaluation complete")
        print(f"\n  Results:")
        print(f"    MAE: {results['mae']:.4f}")
        print(f"    RMSE: {results['rmse']:.4f}")
        print(f"    MAPE: {results['mape']:.2f}%")
        print(f"    R²: {results['r2']:.4f}")

        if 'direction_accuracy' in results:
            print(f"    Direction Accuracy: {results['direction_accuracy']*100:.2f}%")

        if 'sharpe_ratio' in results:
            print(f"    Sharpe Ratio: {results['sharpe_ratio']:.4f}")

        return results

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def run_all_baselines():
    """Run all baseline models on Scenario 2"""
    print("="*80)
    print("SCENARIO 2: Sector Rotation Prediction - BASELINE EXPERIMENTS")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load data
    train_df, val_df, test_df = load_data()

    # Prepare features and target (predict XLK - Technology sector)
    print("\nPreparing features...")
    X_train, y_train = prepare_features(train_df, target_col='XLK_Close')
    X_test, y_test = prepare_features(test_df, target_col='XLK_Close')

    # For direction accuracy and Sharpe ratio
    y_previous = test_df['XLK_Close'].shift(1).iloc[1:]
    y_current = test_df['XLK_Close'].iloc[:-1]
    y_test_aligned = y_test.iloc[1:]
    X_test_aligned = X_test.iloc[1:]

    print(f"  Features: {len(X_train.columns)}")
    print(f"  Target: XLK_Close (Technology sector)")

    # Initialize baselines
    baselines = [
        ForwardFillBaseline(),
        LinearInterpolationBaseline(lookback=5),
        HistoricalMeanBaseline(window=20),
        ARIMABaseline(order=(5, 1, 0)),
        RandomForestBaseline(n_estimators=100, max_depth=10, random_state=42)
    ]

    # Run all baselines
    all_results = {}

    for baseline in baselines:
        results = run_baseline(
            baseline,
            X_train, y_train,
            X_test_aligned, y_test_aligned,
            y_previous.values, y_current.values
        )

        if results is not None:
            all_results[baseline.name] = results

    # Create comparison table
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)

    comparison_table = create_comparison_table(all_results)
    print("\n", comparison_table)

    # Save results
    results_dir = RESULTS_DIR / 'tables'
    results_dir.mkdir(parents=True, exist_ok=True)

    results_path = results_dir / 'scenario_2_baselines.csv'
    save_results(all_results, results_path)

    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE")
    print("="*80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nResults saved to: {results_path}")

    return all_results, comparison_table


if __name__ == '__main__':
    results, table = run_all_baselines()
