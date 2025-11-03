"""
Baseline Models for MICE Stock Prediction Experiment
Implements 6 baseline methods for comparison with MICE
"""

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set random seed
np.random.seed(42)


class BaselineModel(ABC):
    """
    Abstract base class for all baseline models

    All baseline models must implement:
    - fit(): Train the model
    - predict(): Make predictions
    - get_params(): Return model parameters
    """

    def __init__(self, name: str):
        """
        Initialize baseline model

        Parameters:
        -----------
        name : str
            Name of the baseline model
        """
        self.name = name
        self.is_fitted = False

    @abstractmethod
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> 'BaselineModel':
        """
        Train the model

        Parameters:
        -----------
        X_train : DataFrame
            Training features
        y_train : Series
            Training targets

        Returns:
        --------
        self : BaselineModel
            Fitted model
        """
        pass

    @abstractmethod
    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Make predictions

        Parameters:
        -----------
        X_test : DataFrame
            Test features

        Returns:
        --------
        predictions : ndarray
            Predicted values
        """
        pass

    def get_params(self) -> Dict[str, Any]:
        """
        Get model parameters

        Returns:
        --------
        params : dict
            Model parameters
        """
        return {'name': self.name, 'is_fitted': self.is_fitted}

    def __repr__(self) -> str:
        return f"{self.name}(fitted={self.is_fitted})"


class ForwardFillBaseline(BaselineModel):
    """
    Baseline 1: Forward Fill
    Uses the last known value as prediction
    """

    def __init__(self):
        super().__init__("ForwardFill")
        self.last_value = None

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> 'ForwardFillBaseline':
        """
        Store the last training value
        """
        self.last_value = y_train.iloc[-1]
        self.is_fitted = True
        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Predict using last known value
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        # Return last value for all predictions
        return np.full(len(X_test), self.last_value)


class LinearInterpolationBaseline(BaselineModel):
    """
    Baseline 2: Linear Interpolation
    Uses linear trend from recent values
    """

    def __init__(self, lookback: int = 5):
        super().__init__("LinearInterpolation")
        self.lookback = lookback
        self.last_values = None

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> 'LinearInterpolationBaseline':
        """
        Store recent values for trend calculation
        """
        self.last_values = y_train.iloc[-self.lookback:].values
        self.is_fitted = True
        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Predict using linear trend
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        # Calculate linear trend from last N values
        x = np.arange(len(self.last_values))
        y = self.last_values

        # Fit linear regression
        coeffs = np.polyfit(x, y, 1)
        slope, intercept = coeffs

        # Predict next values
        predictions = []
        for i in range(len(X_test)):
            next_x = len(self.last_values) + i
            pred = slope * next_x + intercept
            predictions.append(pred)

        return np.array(predictions)


class HistoricalMeanBaseline(BaselineModel):
    """
    Baseline 3: Historical Mean
    Uses rolling average of past N days
    """

    def __init__(self, window: int = 20):
        super().__init__("HistoricalMean")
        self.window = window
        self.mean_value = None

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> 'HistoricalMeanBaseline':
        """
        Calculate mean of recent window
        """
        self.mean_value = y_train.iloc[-self.window:].mean()
        self.is_fitted = True
        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Predict using historical mean
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        return np.full(len(X_test), self.mean_value)

    def get_params(self) -> Dict[str, Any]:
        params = super().get_params()
        params['window'] = self.window
        return params


class ARIMABaseline(BaselineModel):
    """
    Baseline 4: ARIMA
    Univariate time series forecasting
    """

    def __init__(self, order: Tuple[int, int, int] = (5, 1, 0)):
        super().__init__("ARIMA")
        self.order = order
        self.model = None
        self.last_values = None

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> 'ARIMABaseline':
        """
        Fit ARIMA model
        """
        try:
            from statsmodels.tsa.arima.model import ARIMA

            # Fit ARIMA
            self.model = ARIMA(y_train, order=self.order)
            self.model = self.model.fit()
            self.last_values = y_train.values
            self.is_fitted = True

        except ImportError:
            # Fallback to simple moving average if statsmodels not available
            print("Warning: statsmodels not available, using moving average fallback")
            self.last_values = y_train.iloc[-20:].values
            self.model = None
            self.is_fitted = True

        except Exception as e:
            print(f"Warning: ARIMA fitting failed ({str(e)}), using moving average fallback")
            self.last_values = y_train.iloc[-20:].values
            self.model = None
            self.is_fitted = True

        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Forecast using ARIMA
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if self.model is not None:
            # Use ARIMA forecast
            try:
                forecast = self.model.forecast(steps=len(X_test))
                return forecast.values
            except:
                # Fallback to mean
                return np.full(len(X_test), np.mean(self.last_values))
        else:
            # Use simple moving average fallback
            return np.full(len(X_test), np.mean(self.last_values))

    def get_params(self) -> Dict[str, Any]:
        params = super().get_params()
        params['order'] = self.order
        return params


class RandomForestBaseline(BaselineModel):
    """
    Baseline 5: Random Forest
    Multivariate ML baseline
    """

    def __init__(self, n_estimators: int = 100, max_depth: Optional[int] = 10, random_state: int = 42):
        super().__init__("RandomForest")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.model = None
        self.feature_names = None

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> 'RandomForestBaseline':
        """
        Train Random Forest
        """
        from sklearn.ensemble import RandomForestRegressor

        # Remove NaN values
        mask = ~(X_train.isna().any(axis=1) | y_train.isna())
        X_clean = X_train[mask]
        y_clean = y_train[mask]

        self.feature_names = X_clean.columns.tolist()

        # Train model
        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.model.fit(X_clean, y_clean)
        self.is_fitted = True

        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Predict using Random Forest
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        # Handle missing values by forward filling
        X_test_filled = X_test.fillna(method='ffill').fillna(method='bfill')

        return self.model.predict(X_test_filled)

    def get_feature_importance(self) -> pd.Series:
        """
        Get feature importances
        """
        if not self.is_fitted or self.model is None:
            raise ValueError("Model must be fitted first")

        importances = pd.Series(
            self.model.feature_importances_,
            index=self.feature_names
        ).sort_values(ascending=False)

        return importances

    def get_params(self) -> Dict[str, Any]:
        params = super().get_params()
        params.update({
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'random_state': self.random_state
        })
        return params


class LSTMBaseline(BaselineModel):
    """
    Baseline 6: LSTM
    Deep learning baseline for time series
    """

    def __init__(self, units: int = 50, epochs: int = 50, batch_size: int = 32,
                 lookback: int = 20, random_state: int = 42):
        super().__init__("LSTM")
        self.units = units
        self.epochs = epochs
        self.batch_size = batch_size
        self.lookback = lookback
        self.random_state = random_state
        self.model = None
        self.scaler_X = None
        self.scaler_y = None

    def _create_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training
        """
        X_seq, y_seq = [], []

        for i in range(self.lookback, len(X)):
            X_seq.append(X[i-self.lookback:i])
            y_seq.append(y[i])

        return np.array(X_seq), np.array(y_seq)

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> 'LSTMBaseline':
        """
        Train LSTM model
        """
        try:
            import tensorflow as tf
            from tensorflow import keras
            from sklearn.preprocessing import StandardScaler

            # Set random seeds
            np.random.seed(self.random_state)
            tf.random.set_seed(self.random_state)

            # Scale data
            self.scaler_X = StandardScaler()
            self.scaler_y = StandardScaler()

            X_scaled = self.scaler_X.fit_transform(X_train.fillna(0))
            y_scaled = self.scaler_y.fit_transform(y_train.values.reshape(-1, 1)).flatten()

            # Create sequences
            X_seq, y_seq = self._create_sequences(X_scaled, y_scaled)

            # Build model
            self.model = keras.Sequential([
                keras.layers.LSTM(self.units, input_shape=(X_seq.shape[1], X_seq.shape[2])),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(1)
            ])

            self.model.compile(optimizer='adam', loss='mse')

            # Train with early stopping
            early_stop = keras.callbacks.EarlyStopping(
                monitor='loss',
                patience=5,
                restore_best_weights=True
            )

            self.model.fit(
                X_seq, y_seq,
                epochs=self.epochs,
                batch_size=self.batch_size,
                verbose=0,
                callbacks=[early_stop]
            )

            self.is_fitted = True

        except ImportError:
            print("Warning: TensorFlow not available, using simple average fallback")
            self.last_mean = y_train.mean()
            self.model = None
            self.is_fitted = True

        except Exception as e:
            print(f"Warning: LSTM training failed ({str(e)}), using average fallback")
            self.last_mean = y_train.mean()
            self.model = None
            self.is_fitted = True

        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Predict using LSTM
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if self.model is None:
            # Fallback to mean
            return np.full(len(X_test), self.last_mean)

        # Scale test data
        X_scaled = self.scaler_X.transform(X_test.fillna(0))

        # For simplicity, use last lookback from training for first prediction
        # then roll forward (this is a simplified version)
        predictions = []

        for i in range(len(X_test)):
            if i < self.lookback:
                # Not enough history, use mean
                pred = self.last_mean
            else:
                # Create sequence
                seq = X_scaled[i-self.lookback:i].reshape(1, self.lookback, -1)
                pred_scaled = self.model.predict(seq, verbose=0)[0][0]
                pred = self.scaler_y.inverse_transform([[pred_scaled]])[0][0]

            predictions.append(pred)

        return np.array(predictions)

    def get_params(self) -> Dict[str, Any]:
        params = super().get_params()
        params.update({
            'units': self.units,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'lookback': self.lookback
        })
        return params


# Factory function to create baselines
def create_baseline(name: str, **kwargs) -> BaselineModel:
    """
    Factory function to create baseline models

    Parameters:
    -----------
    name : str
        Name of baseline: 'forward_fill', 'linear_interp', 'hist_mean',
                         'arima', 'random_forest', 'lstm'
    **kwargs : dict
        Additional parameters for the baseline

    Returns:
    --------
    baseline : BaselineModel
        Instantiated baseline model
    """
    baselines = {
        'forward_fill': ForwardFillBaseline,
        'linear_interp': LinearInterpolationBaseline,
        'hist_mean': HistoricalMeanBaseline,
        'arima': ARIMABaseline,
        'random_forest': RandomForestBaseline,
        'lstm': LSTMBaseline
    }

    if name not in baselines:
        raise ValueError(f"Unknown baseline: {name}. Choose from {list(baselines.keys())}")

    return baselines[name](**kwargs)
