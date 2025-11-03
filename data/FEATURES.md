# Feature Engineering Documentation

Generated: 2025-11-03 01:57:15

## Feature Categories

### 1. Return Features
- `return_1d`: 1-day simple return
- `return_5d`: 5-day simple return
- `return_20d`: 20-day simple return
- `log_return_Nd`: Log returns for periods 1, 5, 20

### 2. Moving Average Features
- `sma_N`: Simple moving average (N = 5, 10, 20, 50)
- `ema_N`: Exponential moving average (N = 5, 10, 20, 50)
- `price_to_sma_N`: Normalized deviation from SMA

### 3. Volatility Features
- `volatility_Nd`: Rolling standard deviation of returns (N = 5, 20)
- `hist_vol_Nd`: Annualized historical volatility

### 4. Momentum Features
- `roc_Nd`: Rate of change over N days (N = 5, 10, 20)
- `momentum_Nd`: Simple price momentum
- `rsi_14`: Relative Strength Index (14-day)

### 5. Volume Features
- `avg_volume_Nd`: Average volume over N days (N = 5, 20)
- `volume_ratio_Nd`: Current volume / average volume
- `volume_trend_5d`: Volume trend indicator

### 6. Time Features
- `day_of_week`: Day of week (0 = Monday, 4 = Friday)
- `month`: Month (1-12)
- `quarter`: Quarter (1-4)
- `year`: Year
- `days_since_epoch`: Days since 1970-01-01
- `is_month_end`: Binary indicator for month end
- `is_quarter_end`: Binary indicator for quarter end

## Data Leakage Prevention

**Critical:** All features use only historical data (no future information)
- Moving averages: Calculated from past data only
- Returns: Based on past prices
- Volatility: Rolling windows look backwards only

## Feature Engineering Pipeline

1. Load preprocessed data
2. Create return features
3. Create moving averages
4. Create volatility features
5. Create momentum indicators
6. Create volume features (if available)
7. Create time features
8. Save featured data