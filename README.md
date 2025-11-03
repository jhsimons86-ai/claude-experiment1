# MICE for Stock Price Prediction: Rigorous Experimental Study

## Research Question

Can Multiple Imputation by Chained Equations (MICE) outperform baseline methods for predicting stock prices in scenarios where multivariate relationships and temporal structure provide predictive signal?

## Experimental Design

This project implements a rigorous experimental framework inspired by Yann LeCun's principles:
- Clear null hypothesis with statistical testing (α = 0.05)
- Proper train/validation/test splits
- Multiple baselines (6 different methods)
- Statistical significance testing
- Ablation studies to understand mechanisms
- Full reproducibility (fixed random seeds)

## Project Structure

```
stock-prediction-mice/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── SPRINT_PLAN.md                    # Detailed sprint planning
├── TICKET_SUMMARY.md                 # Ticket tracking
├── data/
│   ├── raw/                          # Raw downloaded data
│   │   ├── scenario_1/              # Cross-market holiday data
│   │   ├── scenario_2/              # Sector rotation data
│   │   └── scenario_3/              # Intraday illiquidity data
│   ├── processed/                    # Cleaned and processed data
│   └── splits/                       # Train/val/test splits
├── models/
│   ├── baselines.py                  # 6 baseline implementations
│   ├── mice_variants.py              # 5 MICE implementations
│   └── evaluation.py                 # Metrics & statistical tests
├── experiments/
│   ├── scenario_1_holidays.py        # Cross-market experiment
│   ├── scenario_2_sector.py          # Sector rotation experiment
│   ├── scenario_3_intraday.py        # Intraday illiquidity experiment
│   └── ablation_studies.py           # All ablation experiments
├── results/
│   ├── tables/                       # CSV files with results
│   ├── figures/                      # Plots and visualizations
│   └── report.md                     # Final comprehensive report
└── tests/
    ├── test_data_quality.py          # Data validation tests
    ├── test_baselines.py             # Baseline sanity checks
    └── test_mice.py                  # MICE implementation tests
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd claude-experiment1
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set random seed for reproducibility:
All experiments use `random_state=42` for reproducibility.

## Three Test Scenarios

### Scenario 1: Cross-Market Holiday Prediction
- **Goal:** Predict US market opening after holidays using international markets
- **Data:** 10 years daily (2014-2024)
- **Variables:** SPY, Nikkei, FTSE, DAX, Hang Seng, VIX, DXY, Gold, Oil
- **Test cases:** ~100 US holidays
- **Why:** Tests if MICE can borrow information across correlated markets

### Scenario 2: Sector Rotation Prediction
- **Goal:** Predict small-cap stock prices using large-cap sector movements
- **Data:** 5 years daily (2019-2024)
- **Variables:** 200 small-cap stocks, 10 sector ETFs, SPY, VIX
- **Test cases:** Daily predictions for 200 stocks
- **Why:** Tests if MICE captures sector co-movement

### Scenario 3: Intraday Illiquidity Gaps
- **Goal:** Predict prices during thin trading using liquid stock movements
- **Data:** 1 year minute-level (2024)
- **Variables:** 50 stocks (25 liquid, 25 illiquid)
- **Test cases:** Predictions during illiquid periods
- **Why:** Tests high-frequency cross-sectional relationships

## Baseline Methods

1. **Forward Fill** - Simplest: use last known price
2. **Linear Interpolation** - Interpolate between surrounding values
3. **Historical Mean** - Average of past N days
4. **ARIMA** - Univariate time series forecasting
5. **Random Forest** - Multivariate ML baseline
6. **LSTM** - Deep learning baseline

## MICE Variants

1. **MICE-PMM** - Basic MICE with Predictive Mean Matching
2. **MICE-RF** - MICE with Random Forest estimator
3. **MICE-XGB** - MICE with XGBoost estimator
4. **MICE-Multiple** - Multiple imputations for uncertainty
5. **MICE-TimeAware** - MICE with explicit time features

## Evaluation Metrics

### Primary Metrics
- **MAE** - Mean Absolute Error
- **RMSE** - Root Mean Square Error
- **MAPE** - Mean Absolute Percentage Error

### Secondary Metrics
- **Direction Accuracy** - Did we predict the correct direction?
- **Sharpe Ratio** - Can you make money with this?
- **Calibration** - Are uncertainty estimates accurate?

### Statistical Significance
- Paired t-tests (MICE vs each baseline)
- Cohen's d effect sizes
- Bonferroni correction for multiple comparisons

## Running Experiments

### Quick Start - Run All Experiments
```bash
python run_all_experiments.py
```

### Run Individual Scenarios
```bash
# Scenario 1: Cross-Market Holidays
python experiments/scenario_1_holidays.py

# Scenario 2: Sector Rotation
python experiments/scenario_2_sector.py

# Scenario 3: Intraday Illiquidity
python experiments/scenario_3_intraday.py
```

### Run Ablation Studies
```bash
python experiments/ablation_studies.py
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test suite
pytest tests/test_data_quality.py -v
```

## Hypotheses

**H0 (Null):** MICE performs no better than forward-fill baseline (α = 0.05)

**H1 (Alternative):** MICE significantly outperforms ≥4 baselines in ≥2 scenarios

**H2 (Mechanism):** Performance gains from MICE are due to multivariate relationships, not temporal autocorrelation alone

**H3 (Robustness):** MICE maintains advantage across different market regimes (bull, bear, high volatility)

## Success Criteria

### Must Have (Accept H1)
- MICE beats ≥4 of 6 baselines (p < 0.05) in ≥2 of 3 scenarios
- MAE reduction >15% vs best baseline OR Direction accuracy >55% OR Sharpe >0.5
- Robustness across train/val/test splits

### Nice to Have
- 95% confidence intervals contain true value 90-98% of time
- Inference time <10x slowest baseline
- Clear ablation insights about what drives performance

## Timeline

- **Sprint 1 (Week 1):** Data Infrastructure - 8 tickets, 52 hours
- **Sprint 2 (Week 2):** Baseline Implementation - 12 tickets, 52 hours
- **Sprint 3 (Week 3):** MICE Implementation - 12 tickets, 60 hours
- **Sprint 4 (Week 4):** Analysis & Reporting - 15 tickets, 70 hours

**Total:** 4 weeks, 47 tickets, 234 hours

## Current Status

🔄 **Sprint 1 in Progress** - Data Infrastructure

See [TICKET_SUMMARY.md](TICKET_SUMMARY.md) for detailed status.

## Results

Results will be published in `results/report.md` after completion of all sprints.

## Citation

If you use this code or methodology, please cite:

```
[To be added upon publication]
```

## License

MIT License - See LICENSE file for details

## Contact

For questions or issues, please open an issue on GitHub.

## Acknowledgments

Experimental design inspired by Yann LeCun's principles for rigorous ML research.
