# MICE Stock Prediction - Sprint Planning

## Project Overview
**Research Question:** Can Multiple Imputation by Chained Equations (MICE) outperform baseline methods for predicting stock prices?

**Duration:** 4 sprints (4 weeks)
**Branch:** `claude/mice-stock-prediction-sprint-1-011CUk7594cBGkRKyoxLQNH7`

---

## Sprint 1: Data Infrastructure & Collection (Week 1)
**Goal:** Establish robust data pipeline with all three scenarios ready for experimentation

### Tickets

#### SP1-T01: Project Setup & Repository Structure
**Priority:** Critical
**Estimate:** 4 hours
**Dependencies:** None

**Tasks:**
- [ ] Create directory structure as per spec
- [ ] Initialize requirements.txt with core dependencies
- [ ] Set up README.md with experiment overview
- [ ] Configure random seeds (42) for reproducibility
- [ ] Create .gitignore for data files and results

**Acceptance Criteria:**
- Repository structure matches specification
- All directories created (data/, models/, experiments/, results/, tests/)
- README clearly explains experiment purpose

---

#### SP1-T02: Data Collection - Scenario 1 (Cross-Market)
**Priority:** Critical
**Estimate:** 8 hours
**Dependencies:** SP1-T01

**Tasks:**
- [ ] Implement download_data.py for cross-market data
- [ ] Download 10 years daily data (2014-2024):
  - SPY, EWJ (Nikkei proxy), EWU (FTSE proxy), EWG (DAX proxy)
  - VIX, DXY, GLD, USO, 10Y Treasury
- [ ] Validate data completeness (check for gaps)
- [ ] Identify US market holidays (NYSE calendar)
- [ ] Store raw data in data/raw/scenario_1/

**Acceptance Criteria:**
- All tickers downloaded for full date range
- ~100 US holidays identified across 10 years
- Data quality report generated (missing percentages per ticker)
- Raw data saved in parquet/CSV format

---

#### SP1-T03: Data Collection - Scenario 2 (Sector Rotation)
**Priority:** Critical
**Estimate:** 10 hours
**Dependencies:** SP1-T01

**Tasks:**
- [ ] Download sector ETFs (XLK, XLF, XLV, XLE, XLY, XLP, XLI, XLB, XLU, XLRE)
- [ ] Download SPY and VIX data (2019-2024)
- [ ] Identify 200 small-cap stocks ($500M-$5B market cap):
  - 20 per sector
  - Filter by liquidity (avg volume)
  - Check for delistings
- [ ] Download stock data for selected tickers
- [ ] Store in data/raw/scenario_2/

**Acceptance Criteria:**
- 10 sector ETFs downloaded
- 200 small-cap stocks identified and validated
- No delisted stocks in sample
- Stock selection criteria documented

---

#### SP1-T04: Data Collection - Scenario 3 (Intraday)
**Priority:** High
**Estimate:** 8 hours
**Dependencies:** SP1-T01

**Tasks:**
- [ ] Set up API connection (Polygon.io or Alpaca)
- [ ] Identify 25 liquid stocks (top S&P 500 by volume)
- [ ] Identify 25 illiquid stocks ($500M-$2B, spread >0.5%)
- [ ] Download 1-minute bars for 2024
- [ ] Store in efficient format (HDF5 or parquet)
- [ ] Store in data/raw/scenario_3/

**Acceptance Criteria:**
- API connection established
- 50 stocks selected (25 liquid, 25 illiquid)
- 1-minute data for full 2024 year downloaded
- Data size documented (<10GB recommended)

---

#### SP1-T05: Data Preprocessing Pipeline
**Priority:** Critical
**Estimate:** 6 hours
**Dependencies:** SP1-T02, SP1-T03, SP1-T04

**Tasks:**
- [ ] Implement preprocess.py with functions:
  - clean_data(): Handle splits, dividends, delistings
  - handle_missing(): Document natural missingness patterns
  - validate_data(): Check for anomalies
- [ ] Apply preprocessing to all 3 scenarios
- [ ] Generate data quality report
- [ ] Store cleaned data in data/processed/

**Acceptance Criteria:**
- All scenarios preprocessed without errors
- Data quality report shows <5% missing data in training period
- Outliers identified and documented
- Processed data ready for feature engineering

---

#### SP1-T06: Feature Engineering
**Priority:** Critical
**Estimate:** 8 hours
**Dependencies:** SP1-T05

**Tasks:**
- [ ] Implement create_features() in preprocess.py:
  - Returns (daily, cumulative)
  - Moving averages (5, 20 day)
  - Volatility measures (std dev)
  - Momentum indicators
  - Volume features
  - Time features (day of week, month, etc.)
- [ ] Apply to all scenarios
- [ ] Document all features in data/FEATURES.md
- [ ] Store featured data

**Acceptance Criteria:**
- Minimum 10 features per scenario
- No data leakage (no future information)
- Feature correlation matrix generated
- Features documented with descriptions

---

#### SP1-T07: Train/Val/Test Split Creation
**Priority:** Critical
**Estimate:** 4 hours
**Dependencies:** SP1-T06

**Tasks:**
- [ ] Implement create_splits.py
- [ ] Create splits for each scenario:
  - Scenario 1: Train 2014-2020, Val 2021-2022, Test 2023-2024
  - Scenario 2: Train 2019-2021, Val 2022, Test 2023-2024
  - Scenario 3: Train Jan-Aug, Val Sep-Oct, Test Nov-Dec
- [ ] Validate no temporal leakage
- [ ] Save splits to data/splits/
- [ ] Generate split statistics

**Acceptance Criteria:**
- Splits follow specification exactly
- No overlap between train/val/test
- Split sizes match percentages (±2%)
- Statistics show balanced representation

---

#### SP1-T08: Data Quality Tests
**Priority:** High
**Estimate:** 4 hours
**Dependencies:** SP1-T07

**Tasks:**
- [ ] Create tests/test_data_quality.py
- [ ] Implement tests:
  - test_no_future_leakage()
  - test_date_ranges()
  - test_missing_data_acceptable()
  - test_outliers_flagged()
  - test_split_sizes()
- [ ] Run all tests
- [ ] Document any data issues found

**Acceptance Criteria:**
- All tests pass
- Test coverage >80% for data pipeline
- CI/CD ready (can run with pytest)

---

### Sprint 1 Success Criteria
- ✅ All 3 scenarios have complete, clean data
- ✅ Train/val/test splits created and validated
- ✅ Features engineered without leakage
- ✅ Data quality tests passing
- ✅ Repository structure complete
- ✅ Documentation up to date

**Estimated Total:** 52 hours

---

## Sprint 2: Baseline Implementation (Week 2)
**Goal:** Implement and validate all 6 baseline methods across all scenarios

### Tickets

#### SP2-T01: Baseline Infrastructure
**Priority:** Critical
**Estimate:** 4 hours
**Dependencies:** Sprint 1 complete

**Tasks:**
- [ ] Create models/baselines.py with base class
- [ ] Define BaselineModel interface:
  - fit(X_train, y_train)
  - predict(X_test)
  - get_params()
- [ ] Create models/evaluation.py with metrics:
  - MAE, RMSE, MAPE
  - Direction accuracy
  - Sharpe ratio
- [ ] Set up result storage structure

**Acceptance Criteria:**
- Base class defines clear interface
- All 6 baselines inherit from base
- Metrics functions tested and documented

---

#### SP2-T02: Baseline 1 - Forward Fill
**Priority:** Critical
**Estimate:** 3 hours
**Dependencies:** SP2-T01

**Tasks:**
- [ ] Implement BaselineForwardFill class
- [ ] Handle edge cases (no prior value)
- [ ] Test on toy data
- [ ] Document methodology

**Acceptance Criteria:**
- Correctly uses last known value
- Handles missing data gracefully
- Unit tests pass

---

#### SP2-T03: Baseline 2 - Linear Interpolation
**Priority:** Critical
**Estimate:** 3 hours
**Dependencies:** SP2-T01

**Tasks:**
- [ ] Implement BaselineLinearInterpolation
- [ ] For forward prediction: use linear trend from last N points
- [ ] Test on toy data
- [ ] Document methodology

**Acceptance Criteria:**
- Interpolation mathematically correct
- Works for forward prediction
- Unit tests pass

---

#### SP2-T04: Baseline 3 - Historical Mean
**Priority:** Critical
**Estimate:** 3 hours
**Dependencies:** SP2-T01

**Tasks:**
- [ ] Implement BaselineHistoricalMean
- [ ] Use rolling window (parameterize N days)
- [ ] Test with different window sizes
- [ ] Document methodology

**Acceptance Criteria:**
- Correctly calculates rolling mean
- Window size is configurable
- Unit tests pass

---

#### SP2-T05: Baseline 4 - ARIMA
**Priority:** High
**Estimate:** 6 hours
**Dependencies:** SP2-T01

**Tasks:**
- [ ] Implement BaselineARIMA using statsmodels
- [ ] Auto-select order using AIC/BIC (or fix to (5,1,0))
- [ ] Handle convergence issues
- [ ] Test on multiple time series
- [ ] Document methodology and parameters

**Acceptance Criteria:**
- ARIMA fits without errors on test data
- Predictions are reasonable (not explosive)
- Gracefully handles convergence failures
- Unit tests pass

---

#### SP2-T06: Baseline 5 - Random Forest
**Priority:** High
**Estimate:** 6 hours
**Dependencies:** SP2-T01

**Tasks:**
- [ ] Implement BaselineRandomForest using sklearn
- [ ] Feature engineering for multivariate input
- [ ] Hyperparameter tuning (n_estimators, max_depth)
- [ ] Cross-validation on training set
- [ ] Document methodology

**Acceptance Criteria:**
- Uses all available features
- Hyperparameters tuned on validation set
- Feature importance logged
- Unit tests pass

---

#### SP2-T07: Baseline 6 - LSTM
**Priority:** High
**Estimate:** 8 hours
**Dependencies:** SP2-T01

**Tasks:**
- [ ] Implement BaselineLSTM using TensorFlow/Keras
- [ ] Design architecture (layers, units, dropout)
- [ ] Implement sequence windowing
- [ ] Train with early stopping
- [ ] Document architecture and hyperparameters

**Acceptance Criteria:**
- LSTM trains without errors
- Uses proper sequence windowing
- Early stopping prevents overfitting
- Model architecture documented
- Unit tests pass

---

#### SP2-T08: Run Baselines - Scenario 1
**Priority:** Critical
**Estimate:** 4 hours
**Dependencies:** SP2-T02 through SP2-T07

**Tasks:**
- [ ] Create experiments/scenario_1_holidays.py
- [ ] Run all 6 baselines on holiday prediction task
- [ ] Simulate missing data pattern (US holidays)
- [ ] Calculate all metrics (MAE, RMSE, MAPE, direction, Sharpe)
- [ ] Store results in results/tables/scenario_1_baselines.csv

**Acceptance Criteria:**
- All 6 baselines run without errors
- Results table includes all metrics
- Predictions saved for analysis
- Runtime logged for each method

---

#### SP2-T09: Run Baselines - Scenario 2
**Priority:** Critical
**Estimate:** 4 hours
**Dependencies:** SP2-T02 through SP2-T07

**Tasks:**
- [ ] Create experiments/scenario_2_sector.py
- [ ] Run all 6 baselines on sector rotation task
- [ ] Test on all 200 stocks (aggregate results)
- [ ] Calculate all metrics
- [ ] Store results in results/tables/scenario_2_baselines.csv

**Acceptance Criteria:**
- All 6 baselines run on all stocks
- Results aggregated by sector
- Per-stock results available
- Runtime logged

---

#### SP2-T10: Run Baselines - Scenario 3
**Priority:** High
**Estimate:** 4 hours
**Dependencies:** SP2-T02 through SP2-T07

**Tasks:**
- [ ] Create experiments/scenario_3_intraday.py
- [ ] Run baselines on intraday illiquidity task
- [ ] Handle high-frequency data efficiently
- [ ] Calculate all metrics
- [ ] Store results in results/tables/scenario_3_baselines.csv

**Acceptance Criteria:**
- All baselines run on intraday data
- Computational time reasonable (<2 hours)
- Results table complete
- Memory usage optimized

---

#### SP2-T11: Baseline Visualization & Analysis
**Priority:** High
**Estimate:** 4 hours
**Dependencies:** SP2-T08, SP2-T09, SP2-T10

**Tasks:**
- [ ] Create visualization scripts in results/
- [ ] Generate plots:
  - Baseline comparison bar charts (all metrics)
  - Predictions vs actuals scatter plots
  - Error distributions
  - Time series of predictions
- [ ] Save figures to results/figures/baselines/
- [ ] Create preliminary analysis notebook

**Acceptance Criteria:**
- Clear visualizations for all 3 scenarios
- Plots are publication-ready
- Preliminary insights documented

---

#### SP2-T12: Baseline Testing & Validation
**Priority:** High
**Estimate:** 3 hours
**Dependencies:** SP2-T02 through SP2-T07

**Tasks:**
- [ ] Create tests/test_baselines.py
- [ ] Sanity checks:
  - Forward fill never predicts different values for same input
  - ARIMA residuals are reasonable
  - RF feature importances sum to 1
  - LSTM doesn't output NaN
- [ ] Cross-validate on toy datasets
- [ ] Run all tests

**Acceptance Criteria:**
- All baseline tests pass
- Sanity checks catch obvious errors
- Test coverage >70%

---

### Sprint 2 Success Criteria
- ✅ All 6 baselines implemented and tested
- ✅ All baselines run on all 3 scenarios
- ✅ Results tables generated with all metrics
- ✅ Visualizations created
- ✅ Preliminary analysis shows reasonable baseline performance
- ✅ Code is tested and documented

**Estimated Total:** 52 hours

---

## Sprint 3: MICE Implementation (Week 3)
**Goal:** Implement all MICE variants and run experiments across all scenarios

### Tickets

#### SP3-T01: MICE Infrastructure
**Priority:** Critical
**Estimate:** 4 hours
**Dependencies:** Sprint 2 complete

**Tasks:**
- [ ] Create models/mice_variants.py
- [ ] Design MICEPredictor base class:
  - fit_predict(X_train, X_test)
  - _get_estimator()
  - _simulate_missing()
- [ ] Set up multiple imputation framework
- [ ] Document MICE methodology

**Acceptance Criteria:**
- Base MICE class ready for variants
- Missing data simulation works correctly
- Multiple imputation framework tested

---

#### SP3-T02: MICE Variant 1 - Basic PMM
**Priority:** Critical
**Estimate:** 5 hours
**Dependencies:** SP3-T01

**Tasks:**
- [ ] Implement MICE with Predictive Mean Matching
- [ ] Use BayesianRidge as base estimator
- [ ] Set max_iter=10, random_state=42
- [ ] Test on toy data with known missingness
- [ ] Validate imputation quality

**Acceptance Criteria:**
- MICE-PMM runs without errors
- Imputations are reasonable (within data range)
- Convergence achieved within 10 iterations
- Unit tests pass

---

#### SP3-T03: MICE Variant 2 - Random Forest
**Priority:** Critical
**Estimate:** 4 hours
**Dependencies:** SP3-T01

**Tasks:**
- [ ] Implement MICE with RandomForest estimator
- [ ] Use n_estimators=10 for speed
- [ ] Compare to PMM version
- [ ] Document differences

**Acceptance Criteria:**
- MICE-RF runs without errors
- Captures non-linear relationships
- Performance comparable to MICE-PMM
- Unit tests pass

---

#### SP3-T04: MICE Variant 3 - XGBoost
**Priority:** High
**Estimate:** 5 hours
**Dependencies:** SP3-T01

**Tasks:**
- [ ] Implement MICE with XGBoost estimator
- [ ] Tune hyperparameters (learning_rate, max_depth)
- [ ] Handle categorical variables if present
- [ ] Document XGBoost configuration

**Acceptance Criteria:**
- MICE-XGB runs without errors
- Hyperparameters tuned on validation set
- Performance logged
- Unit tests pass

---

#### SP3-T05: MICE Variant 4 - Multiple Imputations
**Priority:** High
**Estimate:** 6 hours
**Dependencies:** SP3-T02

**Tasks:**
- [ ] Implement multiple imputation (M=5)
- [ ] Run 5 separate imputations with different seeds
- [ ] Average predictions across imputations
- [ ] Calculate prediction uncertainty (std dev)
- [ ] Implement confidence intervals

**Acceptance Criteria:**
- 5 imputations generated
- Mean and std dev calculated
- 95% confidence intervals constructed
- Uncertainty quantification working

---

#### SP3-T06: MICE Variant 5 - Time-Aware
**Priority:** Medium
**Estimate:** 5 hours
**Dependencies:** SP3-T01

**Tasks:**
- [ ] Add time features to data:
  - day_of_week, month, days_since_epoch
  - time_of_day (for scenario 3)
- [ ] Implement MICE with time features
- [ ] Compare to basic MICE
- [ ] Ablation: with vs without time features

**Acceptance Criteria:**
- Time features correctly encoded
- MICE uses temporal information
- Ablation study shows impact
- Unit tests pass

---

#### SP3-T07: Run MICE - Scenario 1 (Holidays)
**Priority:** Critical
**Estimate:** 5 hours
**Dependencies:** SP3-T02 through SP3-T06

**Tasks:**
- [ ] Update experiments/scenario_1_holidays.py
- [ ] Run all 5 MICE variants
- [ ] Simulate US holiday missing pattern
- [ ] Calculate all metrics
- [ ] Store results in results/tables/scenario_1_mice.csv
- [ ] Compare to baselines

**Acceptance Criteria:**
- All MICE variants run successfully
- Results comparable to baselines
- Predictions logged for analysis
- Runtime acceptable (<1 hour per variant)

---

#### SP3-T08: Run MICE - Scenario 2 (Sector)
**Priority:** Critical
**Estimate:** 6 hours
**Dependencies:** SP3-T02 through SP3-T06

**Tasks:**
- [ ] Update experiments/scenario_2_sector.py
- [ ] Run all 5 MICE variants on 200 stocks
- [ ] Aggregate results by sector
- [ ] Calculate all metrics
- [ ] Store results in results/tables/scenario_2_mice.csv

**Acceptance Criteria:**
- All MICE variants run on all stocks
- Sector-level aggregation complete
- Per-stock results available
- Runtime acceptable (<3 hours total)

---

#### SP3-T09: Run MICE - Scenario 3 (Intraday)
**Priority:** High
**Estimate:** 6 hours
**Dependencies:** SP3-T02 through SP3-T06

**Tasks:**
- [ ] Update experiments/scenario_3_intraday.py
- [ ] Run MICE variants on intraday data
- [ ] Handle high-frequency efficiently
- [ ] Calculate all metrics
- [ ] Store results in results/tables/scenario_3_mice.csv

**Acceptance Criteria:**
- All MICE variants run successfully
- Memory usage optimized for high-frequency
- Results complete
- Runtime acceptable (<2 hours)

---

#### SP3-T10: MICE Visualization & Comparison
**Priority:** High
**Estimate:** 5 hours
**Dependencies:** SP3-T07, SP3-T08, SP3-T09

**Tasks:**
- [ ] Create comprehensive comparison plots:
  - MICE vs baselines (all metrics)
  - MICE variant comparison
  - Prediction uncertainty visualizations
  - Error distributions
- [ ] Generate comparison tables
- [ ] Save to results/figures/mice/

**Acceptance Criteria:**
- Clear visual comparisons across methods
- Publication-ready figures
- Tables formatted for report

---

#### SP3-T11: MICE Testing & Validation
**Priority:** High
**Estimate:** 4 hours
**Dependencies:** SP3-T02 through SP3-T06

**Tasks:**
- [ ] Create tests/test_mice.py
- [ ] Test each variant:
  - Imputations within reasonable range
  - Convergence checks
  - Uncertainty calibration
  - Reproducibility with same seed
- [ ] Run all tests

**Acceptance Criteria:**
- All MICE tests pass
- Imputations validated
- Test coverage >70%

---

#### SP3-T12: Preliminary Statistical Analysis
**Priority:** High
**Estimate:** 5 hours
**Dependencies:** SP3-T10

**Tasks:**
- [ ] Implement statistical tests in evaluation.py:
  - Paired t-tests (MICE vs each baseline)
  - Effect size (Cohen's d)
  - Confidence intervals
- [ ] Run tests for all scenarios
- [ ] Generate significance table
- [ ] Document which hypotheses are supported

**Acceptance Criteria:**
- Statistical tests implemented correctly
- P-values calculated for all comparisons
- Significance table generated
- Preliminary conclusions documented

---

### Sprint 3 Success Criteria
- ✅ All 5 MICE variants implemented and tested
- ✅ MICE run on all 3 scenarios
- ✅ Comprehensive comparison to baselines
- ✅ Statistical significance tests completed
- ✅ Visualizations created
- ✅ Preliminary results indicate whether hypotheses supported

**Estimated Total:** 60 hours

---

## Sprint 4: Analysis & Reporting (Week 4)
**Goal:** Complete ablation studies, statistical analysis, and comprehensive reporting

### Tickets

#### SP4-T01: Ablation Study 1 - Predictor Selection
**Priority:** Critical
**Estimate:** 6 hours
**Dependencies:** Sprint 3 complete

**Tasks:**
- [ ] Create experiments/ablation_studies.py
- [ ] Define predictor sets:
  - Full model (all predictors)
  - No sector
  - No market
  - No volatility
  - Univariate (only target lag)
  - Market only
  - Sector only
- [ ] Run MICE with each predictor set
- [ ] Compare performance
- [ ] Store results in results/tables/ablation_predictors.csv

**Acceptance Criteria:**
- All 7 predictor configurations tested
- Clear performance differences documented
- Hypothesis about multivariate relationships tested
- Results visualized

---

#### SP4-T02: Ablation Study 2 - Number of Iterations
**Priority:** High
**Estimate:** 4 hours
**Dependencies:** Sprint 3 complete

**Tasks:**
- [ ] Test MICE with varying iterations: [1, 3, 5, 10, 20]
- [ ] Measure convergence
- [ ] Plot performance vs iterations
- [ ] Identify optimal iteration count
- [ ] Store results in results/tables/ablation_iterations.csv

**Acceptance Criteria:**
- All iteration counts tested
- Convergence curve plotted
- Optimal iterations identified
- Diminishing returns documented

---

#### SP4-T03: Ablation Study 3 - Missing Data Amount
**Priority:** High
**Estimate:** 5 hours
**Dependencies:** Sprint 3 complete

**Tasks:**
- [ ] Artificially create missing data: [10%, 30%, 50%, 70%, 90%]
- [ ] Run MICE and best baseline on each
- [ ] Compare performance degradation
- [ ] Test hypothesis: MICE advantage increases with missingness
- [ ] Store results in results/tables/ablation_missing.csv

**Acceptance Criteria:**
- All missingness levels tested
- MICE vs baseline gap analyzed
- Hypothesis tested
- Results visualized

---

#### SP4-T04: Ablation Study 4 - Market Regime
**Priority:** High
**Estimate:** 6 hours
**Dependencies:** Sprint 3 complete

**Tasks:**
- [ ] Define market regimes:
  - Bull market (returns > 0.5% cumulative)
  - Bear market (returns < -0.5% cumulative)
  - High volatility (VIX > 25)
  - Low volatility (VIX < 15)
- [ ] Split test set by regime
- [ ] Run MICE and baselines on each regime
- [ ] Compare performance across regimes
- [ ] Store results in results/tables/ablation_regimes.csv

**Acceptance Criteria:**
- All 4 regimes tested
- Sufficient data in each regime (>20 samples)
- Performance differences documented
- Robustness hypothesis tested

---

#### SP4-T05: Comprehensive Statistical Analysis
**Priority:** Critical
**Estimate:** 6 hours
**Dependencies:** SP4-T01 through SP4-T04

**Tasks:**
- [ ] Consolidate all statistical tests
- [ ] For each hypothesis (H0, H1, H2, H3):
  - State hypothesis
  - Present evidence
  - Calculate p-values
  - Make conclusion (accept/reject)
- [ ] Calculate effect sizes (Cohen's d)
- [ ] Bonferroni correction for multiple comparisons
- [ ] Generate comprehensive statistics table

**Acceptance Criteria:**
- All hypotheses formally tested
- Multiple comparison correction applied
- Effect sizes calculated
- Clear accept/reject decisions for each hypothesis

---

#### SP4-T06: Trading Strategy Backtest
**Priority:** Medium
**Estimate:** 5 hours
**Dependencies:** Sprint 3 complete

**Tasks:**
- [ ] Implement simple trading strategy:
  - If MICE predicts up: Buy
  - If MICE predicts down: Short (or stay out)
- [ ] Calculate returns for each scenario
- [ ] Calculate Sharpe ratio
- [ ] Compare to buy-and-hold baseline
- [ ] Account for transaction costs
- [ ] Store results in results/tables/trading_performance.csv

**Acceptance Criteria:**
- Trading strategy implemented
- Sharpe ratio calculated correctly
- Comparison to buy-and-hold
- Realistic transaction costs included

---

#### SP4-T07: Uncertainty Calibration Analysis
**Priority:** Medium
**Estimate:** 4 hours
**Dependencies:** SP3-T05 (Multiple Imputations)

**Tasks:**
- [ ] For MICE Variant 4 (multiple imputations):
  - Calculate 95% confidence intervals
  - Check if actual values fall within CI
  - Calculate coverage rate
- [ ] Test calibration: should be 90-98%
- [ ] Plot prediction intervals vs actuals
- [ ] Store results in results/tables/calibration.csv

**Acceptance Criteria:**
- Confidence intervals calculated
- Coverage rate measured
- Calibration plot created
- Pass/fail on calibration criterion

---

#### SP4-T08: Results Visualization Suite
**Priority:** High
**Estimate:** 6 hours
**Dependencies:** SP4-T05, SP4-T06, SP4-T07

**Tasks:**
- [ ] Create comprehensive figure set:
  - Main results: MICE vs baselines (all scenarios)
  - Ablation results (4 studies)
  - Prediction examples (actual vs predicted)
  - Error distributions
  - Uncertainty calibration plots
  - Trading strategy returns
  - Statistical significance heatmap
- [ ] Ensure all figures publication-ready
- [ ] Save to results/figures/

**Acceptance Criteria:**
- Minimum 15 publication-ready figures
- All figures have clear labels and legends
- Color schemes consistent
- Figures tell the story without text

---

#### SP4-T09: Write Comprehensive Report
**Priority:** Critical
**Estimate:** 10 hours
**Dependencies:** SP4-T05, SP4-T08

**Tasks:**
- [ ] Create results/report.md following template
- [ ] Sections:
  - Executive Summary (did it work?)
  - Methodology (data, design, metrics)
  - Results (all 3 scenarios)
  - Ablation Studies (all 4 studies)
  - Statistical Analysis (hypothesis testing)
  - Discussion (why it worked/didn't work)
  - Limitations and caveats
  - Conclusion (accept/reject hypotheses)
  - Future work
  - Appendix (full tables)
- [ ] Include all figures and tables
- [ ] Write clear, honest conclusions

**Acceptance Criteria:**
- Report >20 pages (detailed)
- All sections complete
- Results honestly reported (including negatives)
- Publication-ready quality
- Peer-reviewable

---

#### SP4-T10: Code Documentation & Cleanup
**Priority:** High
**Estimate:** 5 hours
**Dependencies:** All previous tickets

**Tasks:**
- [ ] Add docstrings to all functions
- [ ] Update README.md with:
  - How to reproduce results
  - Dependencies and installation
  - Data sources
  - Key findings summary
- [ ] Clean up commented code
- [ ] Ensure all scripts runnable
- [ ] Create requirements.txt with exact versions
- [ ] Add LICENSE file

**Acceptance Criteria:**
- All functions documented
- README has clear reproduction steps
- Code is clean and readable
- New user can run experiments

---

#### SP4-T11: Create Main Execution Script
**Priority:** High
**Estimate:** 4 hours
**Dependencies:** SP4-T10

**Tasks:**
- [ ] Create run_all_experiments.py
- [ ] Script should:
  - Download data
  - Run all baselines
  - Run all MICE variants
  - Run ablation studies
  - Generate all figures
  - Produce final report
- [ ] Add command-line arguments for flexibility
- [ ] Log all outputs
- [ ] Estimate total runtime

**Acceptance Criteria:**
- Single command runs entire experiment
- Progress logged clearly
- Handles errors gracefully
- Estimated runtime documented (<24 hours)

---

#### SP4-T12: Final Validation & Testing
**Priority:** Critical
**Estimate:** 5 hours
**Dependencies:** SP4-T11

**Tasks:**
- [ ] Run full test suite
- [ ] Validate all results reproduce
- [ ] Check all figures render correctly
- [ ] Spell-check report
- [ ] Verify all citations/references
- [ ] Test on fresh environment (Docker or clean VM)
- [ ] Create final checklist

**Acceptance Criteria:**
- All tests pass
- Results reproduce with same random seed
- Report has no spelling errors
- Code runs in fresh environment
- Ready for publication/review

---

#### SP4-T13: Create Presentation Materials
**Priority:** Medium
**Estimate:** 4 hours
**Dependencies:** SP4-T09

**Tasks:**
- [ ] Create presentation deck (10-15 slides):
  - Problem statement
  - Experimental design
  - Key results
  - Main findings
  - Conclusions
- [ ] Include best visualizations
- [ ] Practice presentation (time to 15 min)
- [ ] Save as PDF in results/

**Acceptance Criteria:**
- Professional slide deck
- Clear narrative arc
- Best figures included
- Under 15 minutes to present

---

### Sprint 4 Success Criteria
- ✅ All 4 ablation studies completed
- ✅ Statistical analysis finalized (all hypotheses tested)
- ✅ Comprehensive report written
- ✅ All code documented and tested
- ✅ Results fully reproducible
- ✅ Ready for publication/review
- ✅ Presentation materials created

**Estimated Total:** 70 hours

---

## Summary by Sprint

| Sprint | Focus | Tickets | Est. Hours | Key Deliverable |
|--------|-------|---------|------------|-----------------|
| Sprint 1 | Data Infrastructure | SP1-T01 to SP1-T08 | 52 | Clean data ready for experiments |
| Sprint 2 | Baseline Methods | SP2-T01 to SP2-T12 | 52 | All 6 baselines tested |
| Sprint 3 | MICE Implementation | SP3-T01 to SP3-T12 | 60 | MICE variants evaluated |
| Sprint 4 | Analysis & Reporting | SP4-T01 to SP4-T13 | 70 | Publication-ready report |
| **Total** | | **47 tickets** | **234 hours** | **Complete experiment** |

---

## Critical Path

```
SP1-T01 → SP1-T02 → SP1-T05 → SP1-T06 → SP1-T07 →
SP2-T01 → SP2-T07 → SP2-T08 →
SP3-T01 → SP3-T02 → SP3-T07 →
SP4-T05 → SP4-T09 → SP4-T12
```

---

## Risk Mitigation by Sprint

### Sprint 1 Risks
- **Data unavailable:** Use alternative sources (CRSP, Quandl)
- **API limits:** Cache data, use multiple keys
- **Storage issues:** Use compressed formats (parquet)

### Sprint 2 Risks
- **ARIMA convergence:** Implement fallback to simpler model
- **LSTM training time:** Use GPU if available, reduce data size
- **Computational limits:** Parallelize where possible

### Sprint 3 Risks
- **MICE too slow:** Reduce iterations, use faster estimators
- **Memory issues:** Batch processing, use generators
- **Poor results:** This is okay! Document why

### Sprint 4 Risks
- **Analysis time underestimated:** Prioritize core analyses
- **Writing takes longer:** Start report early in sprint
- **Reproducibility issues:** Test early and often

---

## Success Metrics

### Must Have (Minimum Viable)
- [ ] All 3 scenarios implemented
- [ ] At least 4 baselines working
- [ ] At least 3 MICE variants working
- [ ] Statistical comparison complete
- [ ] Report written with clear conclusions

### Should Have (Target)
- [ ] All 6 baselines working
- [ ] All 5 MICE variants working
- [ ] All 4 ablation studies complete
- [ ] Trading strategy backtested
- [ ] Publication-ready report

### Nice to Have (Stretch)
- [ ] Uncertainty calibration perfect
- [ ] Code deployable as library
- [ ] Interactive visualization dashboard
- [ ] Submitted to journal/conference

---

## Daily Standup Format

**What did I complete yesterday?**
- List completed tickets

**What am I working on today?**
- Current ticket(s)

**Any blockers?**
- Data issues, technical problems, questions

**Am I on track for sprint goals?**
- Yes/No with brief explanation
