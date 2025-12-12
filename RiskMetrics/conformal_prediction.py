from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.stattools import jarque_bera
from xgboost import XGBRegressor
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


@dataclass
class RiskEstimate:
    """Container for backtest result"""
    timestamp: pd.Timestamp
    point_forecast: float
    lower_bound: float
    upper_bound: float
    confidence_level: float
    method: str

@dataclass
class BacktestResult:
    method:str
    coverage:float
    target_coverage:float
    avg_interval_width:float
    violations:int
    total_observations:int
    violation_rate:float
    conditional_coverage_pvalue:float
    kupiec_pvalue:float

    def __repr__(self):
        return (f"BacktestResult({self.method}): "
                f"Coverage={self.coverage:.3f} (target={self.target_coverage:.3f}), "
                f"Violations={self.violations}/{self.total_observations}")

class RiskModel(ABC):

    @abstractmethod
    def fit(self, data: np.ndarray) -> None:
        pass

    @abstractmethod
    def predict_risk(self, alpha:float=0.05) -> tuple[float, float]:
        pass

    @abstractmethod
    def update(self, new_observations:float) -> None:
        pass


######################
# CLASSICAL VAR MODELS
######################

class HistoricalVaR:
    def __init__(self, window_size:int=250):
        self.window_size = window_size
        self.data = None

    def fit(self, data:np.ndarray) -> None:
        self.data = data[-self.window_size:].copy()

    def predict_risk(self, alpha:float=0.05) -> tuple[float, float]:
        if self.data is None or len(self.data) == 0:
            return (np.nan, np.nan)

        lower = np.percentile(self.data, alpha * 100)
        upper = np.percentile(self.data, (1-alpha) * 100)
        return (lower, upper)

    def update(self, new_observation:float, alpha:float=0.05) -> None:
        if self.data is None:
            self.data = np.array([new_observation])
        else:
            self.data = np.append(self.data, new_observation)
            if len(self.data) > self.window_size:
                self.data = self.data[-self.window_size:]

class ParametricVaR:
    def __init__(self, window_size:int=250):
        self.window_size = window_size
        self.data = None
        self.mu = 0
        self.sigma = 1

    def fit(self, data:np.ndarray) -> None:
        self.data = data[-self.window_size:].copy()
        self.mu = np.mean(self.data)
        self.sigma = np.std(self.data, ddof=1)

    def predict_risk(self, alpha:float=0.05) -> tuple[float, float]:
        z = stats.norm.ppf(alpha)
        lower = self.mu + z * self.sigma
        upper = self.mu - z * self.sigma
        return (lower, upper)

    def update(self, new_observation:float, alpha:float=0.05) -> None:
        if self.data is None:
            self.data = np.array([new_observation])
        else:
            self.data = np.append(self.data, new_observation)

            if len(self.data) > self.window_size:
                self.data = self.data[-self.window_size:]

        self.mu = np.mean(self.data)
        self.sigma = np.std(self.data, ddof=1)

class EWMAVaR:
    def __init__(self, decay_factor:float=0.94, window_size:int=250):
        self.decay_factor = decay_factor
        self.window_size = window_size
        self.data = None
        self.ewma_var = None
        self.mu = 0

    def fit(self, data:np.ndarray) -> None:
        self.data = data[-self.window_size:].copy()
        self.mu = np.mean(self.data)
        self.ewma_var = np.var(self.data, ddof=1)
        for r in self.data:
            self.ewma_var = self.decay_factor * self.ewma_var + (1-self.decay_factor)*(r-self.mu) ** 2

    def predict_risk(self, alpha:float=0.05) -> tuple[float, float]:
        if self.ewma_var is None:
            return (np.nan, np.nan)

        sigma = np.sqrt(self.ewma_var)
        z = stats.norm.ppf(alpha)
        lower = self.mu + z * sigma
        upper = self.mu - z * sigma

        return (lower, upper)

    def update(self, new_observation:float, alpha:float=0.05) -> None:
        if self.data is None:
            self.data = np.array([new_observation])
            self.ewma_var = 0

        else:
            self.data = np.append(self.data, new_observation)
            if len(self.data) > self.window_size:
                self.data = self.data[-self.window_size:]

        self.mu = np.mean(self.data)
        if self.ewma_var is not None:
            self.ewma_var = self.decay_factor * self.ewma_var + (1-self.decay_factor)*(new_observation - self.mu) ** 2

        else:
            self.ewma_var = (new_observation - self.mu) ** 2

################
# AR MODEL
################

def get_predictor(predictor_name: str, predictor_params: dict):
    """
    Factory for base time-series predictors.

    Parameters
    ----------
    predictor_name : {'ar', 'sarimax'}
    predictor_params : dict
        For 'ar':
            {'lags': int}
        For 'sarimax':
            {
                'order': (p,d,q),
                'seasonal_order': (P,D,Q,s),
                'trend': 'n'|'c'|'t'|'ct',
                'enforce_stationarity': bool,
                'enforce_invertibility': bool,
            }
    """
    predictor_params = predictor_params or {}

    if predictor_name == 'ar':
        # Default to lags=3 if not provided
        if 'lags' not in predictor_params:
            predictor_params['lags'] = 3
        return SimpleARPredictor(**predictor_params)

    elif predictor_name == 'sarimax':
        # Provide some sane defaults if any missing
        predictor_params.setdefault('order', (1, 0, 0))
        predictor_params.setdefault('seasonal_order', (0, 0, 0, 0))
        predictor_params.setdefault('trend', 'c')
        predictor_params.setdefault('enforce_stationarity', False)
        predictor_params.setdefault('enforce_invertibility', False)
        return SimpleSARIMAXPredictor(**predictor_params)
    
    elif predictor_name == 'xgboost':
        predictor_params.setdefault('lags', 5)
        predictor_params.setdefault('n_estimators', 100)
        predictor_params.setdefault('max_depth', 3)
        predictor_params.setdefault('learning_rate', 0.1)
        return SimpleXGBoostPredictor(**predictor_params)
    
    elif predictor_name == 'lstm':
        predictor_params.setdefault('seq_length', 10)
        predictor_params.setdefault('hidden_size', 50)
        predictor_params.setdefault('num_layers', 2)
        predictor_params.setdefault('epochs', 50)
        return SimpleLSTMPredictor(**predictor_params)

    else:
        raise ValueError("predictor_name must be 'ar', 'sarimax', 'xgboost', or 'lstm'")



class SimpleARPredictor:

    def __init__(self, lags:int=1):
        self.lags=lags
        self.coefficients=None
        self.intercept=0
        self.residuals=None

    def fit(self, data:np.ndarray, X: Optional[np.ndarray] = None) -> None:
        if len(data) < self.lags + 2:
            self.coefficients = np.zeros(self.lags)
            self.intercept = np.mean(data) if len(data) > 0 else 0
            self.residuals = np.zeros(1)
            return

        # Create lagged features
        Xlag = np.column_stack([data[self.lags-i-1:-i-1] for i in range(self.lags)])
        y = data[self.lags:]

        # add intercept
        Xlag = np.column_stack([np.ones(len(Xlag)), Xlag])

        # OLS solution
        try:
            beta = np.linalg.lstsq(Xlag, y, rcond=None)[0]
            self.intercept = beta[0]
            self.coefficients = beta[1:]

            # calculate residuals
            y_pred = Xlag @ beta
            self.residuals = y - y_pred

        except:
            self.coefficients = np.zeros(self.lags)
            self.intercept = np.mean(data)
            self.residuals = np.zeros(1)

    def predict(self, data:np.ndarray, X: Optional[np.ndarray] = None) -> float:
        if self.coefficients is None:
            return np.mean(data) if len(data)>0 else 0
        recent = data[-self.lags:]
        return self.intercept + np.dot(self.coefficients, recent[::-1])


################
# SARIMAX MODEL
################


class SimpleSARIMAXPredictor:
    """
    SARIMAX wrapper with a SimpleARPredictor-style interface, now supporting exogenous variables.

    - __init__(...) sets SARIMAX structure.
    - fit(data, X=None) fits the model (optionally with exogenous features).
    - predict(data, X_future=None) produces a 1-step-ahead forecast.

    Parameters
    ----------
    order : (p, d, q)
    seasonal_order : (P, D, Q, s)
    trend : 'n', 'c', 't', or 'ct'
    """

    def __init__(
        self,
        order: Tuple[int, int, int] = (1, 0, 0),
        seasonal_order: Tuple[int, int, int, int] = (0, 0, 0, 0),
        trend: str = "c",
        enforce_stationarity: bool = False,
        enforce_invertibility: bool = False,
    ):
        self.order = order
        self.seasonal_order = seasonal_order
        self.trend = trend
        self.enforce_stationarity = enforce_stationarity
        self.enforce_invertibility = enforce_invertibility

        # Fitted objects
        self.model_ = None
        self.result_ = None

        # Diagnostics
        self.residuals: Optional[np.ndarray] = None
        self.mean_ = 0.0
        self.is_fitted = False

        # Exogenous info
        self.has_exog = False
        self.n_exog_features: Optional[int] = None

    def fit(self, data: np.ndarray, X: Optional[np.ndarray] = None) -> None:
        """
        Fit the SARIMAX model to a 1D numpy array, optionally with exogenous variables.

        Parameters
        ----------
        data : 1D np.ndarray
            Target time series.
        X : 2D np.ndarray, optional
            Exogenous regressors (same number of rows as data).
        """
        y = np.asarray(data, dtype=float).ravel()

        # Basic exog checks
        if X is not None:
            X = np.asarray(X, dtype=float)
            if X.ndim == 1:
                X = X.reshape(-1, 1)
            if len(X) != len(y):
                raise ValueError("X and data must have the same length.")
            self.has_exog = True
            self.n_exog_features = X.shape[1]
        else:
            self.has_exog = False
            self.n_exog_features = None

        # Fallback for too-short series (similar spirit to SimpleARPredictor)
        min_obs = max(
            10,
            sum(self.order) + self.seasonal_order[3] * sum(self.seasonal_order[:3]) + 1,
        )
        if len(y) < min_obs:
            self.model_ = None
            self.result_ = None
            self.residuals = np.zeros(1)
            self.mean_ = float(np.mean(y)) if len(y) > 0 else 0.0
            self.is_fitted = False
            return

        try:
            self.mean_ = float(np.mean(y))

            self.model_ = SARIMAX(
                y,
                exog=X if self.has_exog else None,
                order=self.order,
                seasonal_order=self.seasonal_order,
                trend=self.trend,
                enforce_stationarity=self.enforce_stationarity,
                enforce_invertibility=self.enforce_invertibility,
            )
            self.result_ = self.model_.fit(disp=False)

            # One-step-ahead residuals
            self.residuals = np.asarray(self.result_.resid, dtype=float)
            self.is_fitted = True

        except Exception as e:
            print(f"[SimpleSARIMAXPredictor] Fit failed: {e}")
            self.model_ = None
            self.result_ = None
            self.residuals = np.zeros(1)
            self.mean_ = float(np.mean(y)) if len(y) > 0 else 0.0
            self.is_fitted = False

    def predict(self, data: np.ndarray, X: Optional[np.ndarray] = None) -> float:
        """
        One-step-ahead prediction.

        Parameters
        ----------
        data : np.ndarray
            Kept for API symmetry with SimpleARPredictor.
            Used only for fallback behavior if model not fitted.
        X_future : np.ndarray, optional
            Exogenous value(s) for the *next* time step.
            If the model was fit with exogenous variables, you must pass
            one row with the same number of features used in fit().

        Returns
        -------
        float
            Forecast for the next time step.
        """
        # If model is not fitted, fall back to mean of provided data
        if not self.is_fitted or self.result_ is None:
            data = np.asarray(data, dtype=float)
            if len(data) == 0:
                return 0.0
            return float(np.mean(data))

        # Prepare exogenous for forecasting, if needed
        exog_fc = None
        if self.has_exog:
            if X is None:
                # No exog provided, fall back to unconditional mean
                print("[SimpleSARIMAXPredictor] X_future is required for exogenous model; using mean fallback.")
                return self.mean_

            X = np.asarray(X, dtype=float)
            # Ensure shape (1, n_features)
            if X.ndim == 1:
                X = X.reshape(1, -1)

            if X.shape[1] != self.n_exog_features:
                raise ValueError(
                    f"X_future must have {self.n_exog_features} features, "
                    f"got {X.shape[1]}"
                )
            exog_fc = X

        try:
            fc = self.result_.get_forecast(steps=1, exog=exog_fc)
            pm = fc.predicted_mean

            # Handle Series, 1-element array, or scalar
            if hasattr(pm, "iloc"):                 # pandas Series
                return float(pm.iloc[0])
            elif isinstance(pm, (list, np.ndarray)):  # numpy array or list
                return float(pm[0])
            else:                                    # scalar fallback
                return float(pm)

        except Exception as e:
            print(f"[SimpleSARIMAXPredictor] Predict failed, using fallback mean: {e}")
            return self.mean_

    def print_diagnostics(
        self,
        lags: int = 24,
        alpha: float = 0.05,
        show_plots: bool = False,
    ) -> None:
        """
        Print diagnostics for a fitted SARIMAX model wrapped by SimpleSARIMAXPredictor.

        Parameters
        ----------
        predictor : SimpleSARIMAXPredictor or similar
            Must have attributes: result_ (SARIMAXResults), order, seasonal_order.
        lags : int
            Number of lags for Ljung–Box test.
        alpha : float
            Significance level for hypothesis tests.
        show_plots : bool
            If True, calls result_.plot_diagnostics() to show standard residual plots.
        """
        # Basic checks
        if self.result_ is None:
            print("[Diagnostics] Predictor is not fitted or result_ is missing.")
            return

        res = self.result_

        print("=" * 60)
        print("SARIMAX Model Diagnostics")
        print("=" * 60)

        # Basic info
        order = self.order
        seasonal_order = self.seasonal_order

        print(f"Order:           {order}")
        print(f"Seasonal order:  {seasonal_order}")
        print(f"Trend:           {self.trend}")
        print("-" * 60)

        # Information criteria
        print(f"AIC:  {res.aic:.3f}")
        print(f"BIC:  {res.bic:.3f}")
        if hasattr(res, "hqic"):
            print(f"HQIC: {res.hqic:.3f}")
        print(f"Log-likelihood: {res.llf:.3f}")
        print("-" * 60)

        # Residual summary
        resid = np.asarray(res.resid)
        resid_mean = np.nanmean(resid)
        resid_std = np.nanstd(resid, ddof=1)
        resid_min = np.nanmin(resid)
        resid_max = np.nanmax(resid)

        print("Residual summary:")
        print(f"  Mean: {resid_mean:.6f}")
        print(f"  Std:  {resid_std:.6f}")
        print(f"  Min:  {resid_min:.6f}")
        print(f"  Max:  {resid_max:.6f}")
        print("-" * 60)

        # Ljung–Box test for autocorrelation
        try:
            lb_test = acorr_ljungbox(resid, lags=[lags], return_df=True)
            lb_stat = lb_test["lb_stat"].iloc[0]
            lb_pvalue = lb_test["lb_pvalue"].iloc[0]
            print(f"Ljung–Box test (lag={lags}):")
            print(f"  Statistic: {lb_stat:.3f}")
            print(f"  p-value:   {lb_pvalue:.3f}")
            if lb_pvalue < alpha:
                print("  => Reject H0: residuals show autocorrelation.")
            else:
                print("  => Fail to reject H0: no strong evidence of autocorrelation.")
        except Exception as e:
            print(f"Ljung–Box test failed: {e}")

        print("-" * 60)

        # Jarque–Bera normality test
        try:
            jb_stat, jb_pvalue, skew, kurt = jarque_bera(resid)
            print("Jarque–Bera normality test:")
            print(f"  Statistic: {jb_stat:.3f}")
            print(f"  p-value:   {jb_pvalue:.3f}")
            print(f"  Skewness:  {skew:.3f}")
            print(f"  Kurtosis:  {kurt:.3f}")
            if jb_pvalue < alpha:
                print("  => Reject H0: residuals are not normally distributed.")
            else:
                print("  => Fail to reject H0: residuals consistent with normality.")
        except Exception as e:
            print(f"Jarque–Bera test failed: {e}")

        print("=" * 60)

        # Optional: standard statsmodels diagnostic plots
        if show_plots:
            try:
                res.plot_diagnostics(figsize=(10, 8), lags=lags)
                print(res.summary())
            except Exception as e:
                print(f"[Diagnostics] plot_diagnostics failed: {e}")

################
# XGBOOST MODEL
################

class SimpleXGBoostPredictor:
    """
    XGBoost wrapper for time series prediction with conformal prediction.
    Creates lagged features and uses XGBoost for point forecasts.
    """

    def __init__(
        self,
        lags: int = 5,
        n_estimators: int = 100,
        max_depth: int = 3,
        learning_rate: float = 0.1,
        **xgb_params
    ):
        self.lags = lags
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.xgb_params = xgb_params
        
        self.model = None
        self.residuals = None
        self.mean_ = 0.0
        self.is_fitted = False

    def _create_features(self, data: np.ndarray, X: Optional[np.ndarray] = None):
        """Create lagged features for time series"""
        n = len(data)
        if n < self.lags + 1:
            return None
        
        # Create lag features
        features = []
        for i in range(self.lags):
            features.append(data[self.lags-i-1:-i-1])
        
        X_lag = np.column_stack(features)
        
        # Add exogenous features
        if X is not None:
            X = np.asarray(X)
            if X.ndim == 1:
                X = X.reshape(-1, 1)
            X_subset = X[self.lags:]
            X_lag = np.column_stack([X_lag, X_subset])
        
        return X_lag
    
    def fit(self, data: np.ndarray, X: Optional[np.ndarray] = None):
        """Fit XGBoost model on time series data"""
        data = np.asarray(data, dtype=float).ravel()
        self.mean_ = float(np.mean(data)) if len(data) > 0 else 0.0
        
        if len(data) < self.lags + 2:
            self.is_fitted = False
            self.residuals = np.zeros(1)
            return
        
        X_features = self._create_features(data, X)
        if X_features is None:
            self.is_fitted = False
            self.residuals = np.zeros(1)
            return
        
        y = data[self.lags:]
        
        try:
            self.model = XGBRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                objective='reg:squarederror',
                **self.xgb_params
            )
            self.model.fit(X_features, y, verbose=False)
            
            # Calculate residuals
            y_pred = self.model.predict(X_features)
            self.residuals = y - y_pred
            self.is_fitted = True
            
        except Exception as e:
            print(f"[SimpleXGBoostPredictor] Fit failed: {e}")
            self.is_fitted = False
            self.residuals = np.zeros(1)
    
    def predict(self, data: np.ndarray, X: Optional[np.ndarray] = None) -> float:
        """One-step-ahead prediction"""
        if not self.is_fitted or self.model is None:
            return self.mean_
        
        data = np.asarray(data, dtype=float).ravel()
        if len(data) < self.lags:
            return self.mean_
        
        # Create features
        recent = data[-self.lags:][::-1].reshape(1, -1)
        
        # Add exogenous features
        if X is not None:
            X = np.asarray(X, dtype=float)
            if X.ndim == 1:
                X = X.reshape(1, -1)
            recent = np.column_stack([recent, X])
        
        try:
            pred = self.model.predict(recent)
            return float(pred[0])
        except Exception as e:
            print(f"[SimpleXGBoostPredictor] Predict failed: {e}")
            return self.mean_
        
 ################
# LSTM MODEL
################       
class SimpleLSTMPredictor:
    """
    LSTM wrapper for time series prediction with conformal prediction.
    """
    
    def __init__(
        self,
        seq_length: int = 10,
        hidden_size: int = 50,
        num_layers: int = 2,
        epochs: int = 50,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        verbose: int = 0
    ):
        
        self.seq_length = seq_length
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.verbose = verbose
        
        self.model = None
        self.residuals = None
        self.mean_ = 0.0
        self.std_ = 1.0
        self.is_fitted = False
        self.n_exog_features = 0
    
    def _build_model(self, input_size: int):
        """Build LSTM model using Keras"""
        model = keras.Sequential()
        
        # 1st layer
        model.add(layers.LSTM(
            self.hidden_size,
            return_sequences=(self.num_layers > 1),
            input_shape=(self.seq_length, input_size)
        ))
        
        # 2nd layers
        for i in range(1, self.num_layers):
            return_seq = (i < self.num_layers - 1)
            model.add(layers.LSTM(self.hidden_size, return_sequences=return_seq))
        
        # Output layer
        model.add(layers.Dense(1))
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse'
        )
        
        return model
    
    def _create_sequences(self, data: np.ndarray, X: Optional[np.ndarray] = None):
        """Create sequences for LSTM training"""
        data = np.asarray(data, dtype=float).ravel()
        n = len(data)
        
        if n < self.seq_length + 1:
            return None, None
        
        sequences = []
        targets = []
        
        # Normalize data
        self.mean_ = float(np.mean(data))
        self.std_ = float(np.std(data)) if np.std(data) > 0 else 1.0
        data_norm = (data - self.mean_) / self.std_
        
        # Determine input size
        input_size = 1
        if X is not None:
            X = np.asarray(X, dtype=float)
            if X.ndim == 1:
                X = X.reshape(-1, 1)
            self.n_exog_features = X.shape[1]
            input_size += self.n_exog_features
        
        for i in range(n - self.seq_length):
            # Target series sequence
            seq = data_norm[i:i+self.seq_length].reshape(-1, 1)
            
            # Add exogenous features
            if X is not None:
                exog_seq = X[i:i+self.seq_length]
                seq = np.concatenate([seq, exog_seq], axis=1)
            
            sequences.append(seq)
            targets.append(data_norm[i+self.seq_length])
        
        return np.array(sequences, dtype=np.float32), np.array(targets, dtype=np.float32)
    
    def fit(self, data: np.ndarray, X: Optional[np.ndarray] = None) -> None:
        """Fit LSTM model on time series data"""
        sequences, targets = self._create_sequences(data, X)
        
        if sequences is None:
            self.is_fitted = False
            self.residuals = np.zeros(1)
            return
        
        input_size = sequences.shape[2]
        
        try:
            # Train model
            self.model = self._build_model(input_size)
            
            self.model.fit(
                sequences,
                targets,
                epochs=self.epochs,
                batch_size=self.batch_size,
                verbose=self.verbose
            )
            
            # Calculate residuals
            predictions = self.model.predict(sequences, verbose=0).flatten()
            
            # Denormalize predictions
            predictions_denorm = predictions * self.std_ + self.mean_
            targets_denorm = targets * self.std_ + self.mean_
            self.residuals = targets_denorm - predictions_denorm
            self.is_fitted = True
            
        except Exception as e:
            print(f"[SimpleLSTMPredictor] Fit failed: {e}")
            self.is_fitted = False
            self.residuals = np.zeros(1)
    
    def predict(self, data: np.ndarray, X: Optional[np.ndarray] = None) -> float:
        """One-step-ahead prediction"""
        if not self.is_fitted or self.model is None:
            return self.mean_
        
        data = np.asarray(data, dtype=float).ravel()
        if len(data) < self.seq_length:
            return self.mean_
        
        # Prepare sequence
        recent = data[-self.seq_length:]
        recent_norm = (recent - self.mean_) / self.std_
        seq = recent_norm.reshape(1, self.seq_length, 1)
        
        # Add exogenous features
        if X is not None and self.n_exog_features > 0:
            X = np.asarray(X, dtype=float)
            if X.ndim == 1:
                X = X.reshape(1, -1)
            # Repeat X for sequence length
            X_seq = np.repeat(X, self.seq_length, axis=0).reshape(1, self.seq_length, -1)
            seq = np.concatenate([seq, X_seq], axis=2)
        
        try:
            pred_norm = self.model.predict(seq, verbose=0)[0, 0]
            
            # Denormalize
            pred = pred_norm * self.std_ + self.mean_
            return float(pred)
        except Exception as e:
            print(f"[SimpleLSTMPredictor] Predict failed: {e}")
            return self.mean_

    

class ConformalPIDPredictor:
    """
    Conformal PID Control for Time Series Risk Measurement

    Implements the framework from Angelopoulos et al. (2023).

    Now supports both AR and SARIMAX predictors, with optional exogenous variables X.
    """

    def __init__(
        self,
        window_size: int = 250,
        learning_rate: float = 0.1,
        use_integrator: bool = True,
        use_scorecaster: bool = True,
        integrator_type: str = 'tan',
        K_I: float = 0.5,
        C_sat: float = 10.0,
        predictor_name: str = 'ar',
        predictor_params: dict | None = None,
        refit_frequency: int = 10
    ):
        self.window_size = window_size
        self.learning_rate = learning_rate
        self.use_integrator = use_integrator
        self.use_scorecaster = use_scorecaster
        self.integrator_type = integrator_type
        self.K_I = K_I
        self.C_sat = C_sat
        self.predictor_name = predictor_name
        self.refit_frequency = refit_frequency

        self.data = None           # y
        self.X = None              # exogenous (if any)

        # Build predictor_params with sensible defaults
        self.predictor_params = dict(predictor_params) if predictor_params is not None else {}

        # base predictor (AR or SARIMAX)
        self.predictor = get_predictor(
            predictor_name=self.predictor_name,
            predictor_params=self.predictor_params
        )

        # minimal history needed before we start using predictions
        if predictor_name == 'ar':
            # Look for lags or ar_lags in params
            self.min_history = self.predictor_params.get(
                'lags',
                self.predictor_params.get('ar_lags', 1)
            )
        elif predictor_name == 'sarimax':
            order = self.predictor_params.get('order', (1, 0, 0))
            seasonal_order = self.predictor_params.get('seasonal_order', (0, 0, 0, 0))
            self.min_history = self.predictor_params.get(
                'min_history',
                max(10, sum(order) + seasonal_order[3] * sum(seasonal_order[:3]))
            )
        else:
            self.min_history = 1

        # conformal state
        self.conformity_scores = []
        self.cumulative_error = 0.0
        self.current_quantile = None
        self.coverage_history = []
        self.update_count = 0
        self.score_window = 20

    def fit(self, data: np.ndarray, X: Optional[np.ndarray] = None) -> None:
        """Fit predictor on last window_size observations, with optional exogenous X."""
        self.data = data[-self.window_size:].copy()

        if X is not None:
            X = np.asarray(X)
            self.X = X[-self.window_size:].copy()
            self.predictor.fit(self.data, self.X)
        else:
            self.X = None
            self.predictor.fit(self.data)

        # initialize from residuals
        if self.predictor.residuals is not None and len(self.predictor.residuals) > 0:
            self.conformity_scores = list(np.abs(self.predictor.residuals))
            self.current_quantile = np.percentile(self.conformity_scores, 95)
        else:
            self.current_quantile = np.std(self.data) * 2 if len(self.data) > 0 else 1.0

    def _tan_integrator(self, x: float, t: int) -> float:
        if t <= 1:
            return 0.0
        arg = x * np.log(t) / (t * self.C_sat)
        arg = np.clip(arg, -np.pi/2 + 0.01, np.pi/2 - 0.01)
        return self.K_I * np.tan(arg)

    def _linear_integrator(self, x: float, t: int) -> float:
        return self.learning_rate * x

    def _scorecast(self) -> float:
        if len(self.conformity_scores) < self.score_window:
            return np.mean(self.conformity_scores) if self.conformity_scores else 0.0
        recent_scores = self.conformity_scores[-self.score_window:]
        weights = np.exp(-0.1 * np.arange(self.score_window)[::-1])
        weights /= weights.sum()
        return np.dot(weights, recent_scores)

    def predict_risk(
        self,
        alpha: float = 0.05,
        X_future: Optional[np.ndarray] = None
    ) -> tuple[float, float]:
        if self.data is None or len(self.data) < self.min_history:
            return (np.nan, np.nan)

        # point forecast (passes exogenous for next step if provided)
        point_forecast = self.predictor.predict(self.data, X==X_future)

        # time index for PID control
        t = len(self.conformity_scores) + 1

        # D control: scorecaster
        if self.use_scorecaster and len(self.conformity_scores) > 0:
            q_hat = self._scorecast()
        else:
            q_hat = self.current_quantile if self.current_quantile is not None else 0.0

        # I control: integrator
        if self.use_integrator:
            if self.integrator_type == 'tan':
                integrator_term = self._tan_integrator(self.cumulative_error, t)
            else:
                integrator_term = self._linear_integrator(self.cumulative_error, t)
            q_t = q_hat + integrator_term
        else:
            q_t = q_hat

        q_t = max(q_t, 0.0)

        return (point_forecast - q_t, point_forecast + q_t)

    def update(
        self,
        new_observation: float,
        alpha: float = 0.05,
        X_new: Optional[np.ndarray] = None
    ) -> None:
        self.update_count += 1

        if self.data is not None and len(self.data) >= self.min_history:
            # point forecast using exogenous info if available
            point_forecast = self.predictor.predict(self.data, X=X_new)

            # conformity score
            score = np.abs(new_observation - point_forecast)
            self.conformity_scores.append(score)

            # check coverage (use same X_new for the prediction interval)
            lower, upper = self.predict_risk(alpha=alpha, X_future=X_new)
            covered = lower <= new_observation <= upper
            err_t = 0 if covered else 1

            # I control: update cumulative error
            self.cumulative_error += (err_t - alpha)

            # P control: update base quantile
            if self.current_quantile is not None:
                self.current_quantile += self.learning_rate * (err_t - alpha)
                self.current_quantile = max(self.current_quantile, 0.0)

            self.coverage_history.append(covered)

        # update stored data and exogenous history
        if self.data is None:
            self.data = np.array([new_observation])
        else:
            self.data = np.append(self.data, new_observation)
            if len(self.data) > self.window_size:
                self.data = self.data[-self.window_size:]

        if X_new is not None:
            X_new = np.asarray(X_new).reshape(1, -1)
            if self.X is None:
                self.X = X_new
            else:
                self.X = np.vstack([self.X, X_new])
                if len(self.X) > self.window_size:
                    self.X = self.X[-self.window_size:]

        # periodic refit
        if self.update_count % self.refit_frequency == 0:
            if self.X is not None:
                self.predictor.fit(self.data, self.X)
            else:
                self.predictor.fit(self.data)


class AdaptiveConformalInference:
    """
    Adaptive Conformal Inference (ACI) - Gibbs & Candès (2021)

    Baseline method that adapts alpha_t instead of tracking quantile directly.

    Extended to:
    - accept either AR or SARIMAX as base predictor
    - optionally use exogenous variables X
    """

    def __init__(
        self,
        window_size: int = 250,
        learning_rate: float = 0.005,
        target_alpha: float = 0.05,
        ar_lags: int = 3,
        refit_frequency: int = 10,
        predictor_name: str = 'ar',
        predictor_params: dict | None = None,
    ):
        """
        Parameters
        ----------
        window_size : int
            Rolling window length for fitting the base predictor.
        learning_rate : float
            Step size for updating alpha_t.
        target_alpha : float
            Target miscoverage level.
        ar_lags : int
            Legacy parameter for AR order (kept for backward compatibility).
            If predictor_name='ar' and predictor_params does not specify 'lags'
            or 'ar_lags', this is used.
        refit_frequency : int
            How often to refit the base predictor (in number of updates).
        predictor_name : {'ar', 'sarimax'}
            Which base predictor to use.
        predictor_params : dict, optional
            Parameters for the base predictor. For example:
            - AR:       {'lags': 3}
            - SARIMAX:  {'order': (1,0,0), 'seasonal_order': (1,0,0,12), ...}
        """
        self.window_size = window_size
        self.learning_rate = learning_rate
        self.target_alpha = target_alpha
        self.refit_frequency = refit_frequency
        self.predictor_name = predictor_name

        # Build predictor_params with sensible defaults
        predictor_params = dict(predictor_params) if predictor_params is not None else {}

        if predictor_name == 'ar':
            # Map legacy ar_lags if not present
            if 'lags' not in predictor_params and 'ar_lags' not in predictor_params:
                predictor_params['lags'] = ar_lags
        self.predictor_params = predictor_params

        # Base predictor (AR or SARIMAX)
        self.predictor = get_predictor(predictor_name, predictor_params)

        # Determine minimum history length before we can use the predictor
        if predictor_name == 'ar':
            self.min_history = self.predictor_params.get(
                'lags',
                self.predictor_params.get('ar_lags', ar_lags)
            )
        elif predictor_name == 'sarimax':
            order = self.predictor_params.get('order', (1, 0, 0))
            seasonal_order = self.predictor_params.get('seasonal_order', (0, 0, 0, 0))
            # heuristic minimum history if not explicitly provided
            self.min_history = self.predictor_params.get(
                'min_history',
                max(10, sum(order) + seasonal_order[3] * sum(seasonal_order[:3]))
            )
        else:
            self.min_history = 1  # fallback

        # Internal state
        self.data = None       # target series y
        self.X = None          # exogenous variables, if any
        self.conformity_scores = []
        self.alpha_t = target_alpha
        self.coverage_history = []
        self.update_count = 0

    def fit(self, data: np.ndarray, X: Optional[np.ndarray] = None) -> None:
        """
        Fit the base predictor on the last `window_size` observations, with
        optional exogenous variables X.
        """
        self.data = data[-self.window_size:].copy()

        if X is not None:
            X = np.asarray(X)
            self.X = X[-self.window_size:].copy()
            # predictor.fit(data, X)
            self.predictor.fit(self.data, self.X)
        else:
            self.X = None
            self.predictor.fit(self.data)

        # Initialize conformity scores from residuals (if available)
        if self.predictor.residuals is not None:
            self.conformity_scores = list(np.abs(self.predictor.residuals))

    def predict_risk(
        self,
        alpha: float = 0.05,
        X_future: Optional[np.ndarray] = None
    ) -> tuple[float, float]:
        """
        Produce a prediction interval [lower, upper] for the next observation.

        Parameters
        ----------
        alpha : float
            Not used directly (ACI uses alpha_t internally), but kept for API
            compatibility with other models.
        X_future : np.ndarray, optional
            Exogenous values for the *next* time step. Ignored if base
            predictor does not use exogenous variables.
        """
        if self.data is None or len(self.conformity_scores) == 0:
            return (np.nan, np.nan)

        # One-step-ahead forecast (pass X_future when supported)
        try:
            point_forecast = self.predictor.predict(self.data, X=X_future)
        except TypeError:
            # For AR-only predictor
            point_forecast = self.predictor.predict(self.data)

        # Effective alpha_t is kept in [0.001, 0.999]
        effective_alpha = np.clip(self.alpha_t, 0.001, 0.999)
        quantile_level = 1 - effective_alpha
        q = np.percentile(self.conformity_scores, quantile_level * 100)

        return (point_forecast - q, point_forecast + q)

    def update(
        self,
        new_observation: float,
        alpha: float = 0.05,
        X_new: Optional[np.ndarray] = None
    ) -> None:
        """
        Update ACI state with a new observation and optional exogenous value.
        """
        self.update_count += 1

        if self.data is not None and len(self.data) >= self.min_history:
            # Forecast for conformity score
            try:
                point_forecast = self.predictor.predict(self.data, X=X_new)
            except TypeError:
                point_forecast = self.predictor.predict(self.data)

            score = np.abs(new_observation - point_forecast)
            self.conformity_scores.append(score)

            # Prediction interval for coverage check
            lower, upper = self.predict_risk(alpha=alpha, X_future=X_new)
            covered = lower <= new_observation <= upper
            err_t = 0 if covered else 1

            # ACI update: adjust alpha_t
            self.alpha_t = self.alpha_t - self.learning_rate * (err_t - self.target_alpha)
            self.coverage_history.append(covered)

        # Update stored data history
        if self.data is None:
            self.data = np.array([new_observation])
        else:
            self.data = np.append(self.data, new_observation)
            if len(self.data) > self.window_size:
                self.data = self.data[-self.window_size:]

        # Update exogenous history
        if X_new is not None:
            X_new = np.asarray(X_new).reshape(1, -1)
            if self.X is None:
                self.X = X_new
            else:
                self.X = np.vstack([self.X, X_new])
                if len(self.X) > self.window_size:
                    self.X = self.X[-self.window_size:]

        # Periodic refit of base predictor
        if self.update_count % self.refit_frequency == 0:
            if self.X is not None:
                self.predictor.fit(self.data, self.X)
            else:
                self.predictor.fit(self.data)


###################################
# STATISTICAL TESTS AND BACKTESTING
###################################

def kupiec_pof_test(
    violations: int,
    n:int,
    alpha: float,
    ) -> float:
    """
    Kupiec Proportion of Failures (POF) test.
    violations: 0/1 series. 1 -> VaR violated.
    """
    eps = 1e-10
    p_hat = np.clip(violations / n, eps, 1-eps)
    alpha_clipped = np.clip(alpha, eps, 1-eps)

    lr = -2 * (
        (n - violations) * np.log(1 - alpha_clipped) + violations * np.log(alpha_clipped) -
        (n - violations) * np.log(1 - p_hat) - violations * np.log(p_hat)
    )
    return 1 - stats.chi2.cdf(lr, df=1)


def christoffersen_test(
    violations: np.ndarray,
    ) -> float:
    """
    Christoffersen conditional coverage test:
    independence + correct unconditional coverage.
    """
    n = len(violations)
    if n < 2:
        return 1.0

    # Transition counts
    n00 = n01 = n10 = n11 = 0
    for i in range(1, n):
        if violations[i-1] == 0 and violations[i] == 0:
            n00 += 1
        elif violations[i-1] == 0 and violations[i] == 1:
            n01 += 1
        elif violations[i-1] == 1 and violations[i] == 0:
            n10 += 1
        else:
            n11 += 1

    # If transitions are degenerate
    if (n00 + n01 == 0) or (n10 + n11 == 0):
        return 1.0

    pi01 = n01 / (n00 + n01) if (n00 + n01) > 0 else 0
    pi11 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0
    pi = (n01 + n11) / n

    if pi ==0 or pi == 1 or pi01 == 0 or pi01 == 1 or pi11 == 0 or pi11 == 1:
        return 1.0

    try:
        ll_null = (
            n00 * np.log(1-pi) +
            n01 * np.log(pi) +
            n10 * np.log(1 - pi) +
            n11 * np.log(pi)
        )
        ll_alt = (
            n00 * np.log(1-pi01) +
            n01 * np.log(pi01) +
            n10 * np.log(1 - pi11) +
            n11 * np.log(pi11)
        )

        lr_ind = -2 * (ll_null - ll_alt)
        return 1 - stats.chi2.cdf(lr_ind, df=1)
    except:
        return 1.0


def backtest_model(
        model,
        data: np.ndarray,
        dates: np.ndarray,
        train_size: int = 250,
        alpha: float = 0.05,
        model_name: str = 'Model',
        X: Optional[np.ndarray] = None
    ):
    n = len(data)

    # Fit with or without exogenous X
    if X is not None:
        try:
            model.fit(data[:train_size], X[:train_size])
            # show diagnostics
            if hasattr(model, 'predictor'):
                if hasattr(model.predictor, 'print_diagnostics') and callable(getattr(model.predictor, 'print_diagnostics')):
                    model.predictor.print_diagnostics(lags=100, alpha=0.05, show_plots=True)
        except TypeError:
            model.fit(data[:train_size])
    else:
        model.fit(data[:train_size])

    results = []
    violations = []

    for t in range(train_size, n):
        x_future = X[t] if X is not None else None

        # Prediction interval
        try:
            lower, upper = model.predict_risk(alpha, X_future=x_future)
        except TypeError:
            lower, upper = model.predict_risk(alpha)

        actual = data[t]
        is_violation = (actual < lower) or (actual > upper)
        violations.append(1 if is_violation else 0)

        interval_width = upper - lower if not np.isnan(upper - lower) else np.nan
        results.append({
            'time': dates[t],
            'actual': actual,
            'lower': lower,
            'upper': upper,
            'interval_width': interval_width,
            'violation': is_violation
        })

        # Update model with new observation (and possibly exogenous)
        try:
            model.update(actual, alpha, X_new=x_future)
        except TypeError:
            model.update(actual, alpha)

    results_df = pd.DataFrame(results)
    violations_array = np.array(violations)
    total_violations = violations_array.sum()
    coverage = 1 - total_violations / len(violations)
    avg_width = results_df['interval_width'].mean()

    kupiec_p = kupiec_pof_test(total_violations, len(violations), alpha)
    christoffersen_p = christoffersen_test(violations_array)

    return BacktestResult(
        method=model_name,
        coverage=coverage,
        target_coverage=1 - alpha,
        avg_interval_width=avg_width,
        violations=total_violations,
        total_observations=len(violations),
        violation_rate=total_violations / len(violations),
        conditional_coverage_pvalue=christoffersen_p,
        kupiec_pvalue=kupiec_p
    ), results_df
