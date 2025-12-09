from dataclasses import dataclass
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from scipy import stats



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
    def predict_risk(self, alpha:float=0.05) -> Tuple[float, float]:
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

    def predict_risk(self, alpha:float=0.05) -> Tuple[float, float]:
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

    def predict_risk(self, alpha:float=0.05) -> Tuple[float, float]:
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

    def predict_risk(self, alpha:float=0.05) -> Tuple[float, float]:
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