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

class SimpleARPredictor:

    def __init__(self, lags:int=1):
        self.lags=lags
        self.coefficients=None
        self.intercept=0
        self.residuals=None

    def fit(self, data:np.ndarray) -> None:
        if len(data) < self.lags + 2:
            self.coefficients = np.zeros(self.lags)
            self.intercept = np.mean(data) if len(data) > 0 else 0
            self.residuals = np.zeros(1)
            return

        # Create lagged features
        X = np.column_stack([data[self.lags-i-1:-i-1] for i in range(self.lags)])
        y = data[self.lags:]

        # add intercept
        X = np.column_stack([np.ones(len(X)), X])

        # OLS solution
        try:
            beta = np.linalg.lstsq(X, y, rcond=None)[0]
            self.intercept = beta[0]
            self.coefficients = beta[1:]

            # calculate residuals
            y_pred = X @ beta
            self.residuals = y - y_pred

        except:
            self.coefficients = np.zeros(self.lags)
            self.intercept = np.mean(data)
            self.residuals = np.zeros(1)

    def predict(self, data:np.ndarray) -> float:
        if self.coefficients is None:
            return np.mean(data) if len(data)>0 else 0
        recent = data[-self.lags:]
        return self.intercept + np.dot(self.coefficients, recent[::-1])
    

class ConformalPIDPredictor:
    """
    Conformal PID Control for Time Series Risk Measurement

    Implements the framework from Angelopulor et al. (2023):
    - P Control: Quantile tracking via online gradient descent
    - I Control: Error integration with saturation function
    - D Control: Scorecasting to anticipate score trends

    Uses simple AR model for computational efficiency
    """

    def __init__(
        self,
        window_size:int=250,
        learning_rate:float=0.1,
        use_integrator:bool=True,
        use_scorecaster:bool=True,
        integrator_type:str='tan',
        K_I:float=0.5,
        C_sat:float=10.0,
        ar_lags:int=3,
        refit_frequency:int=10
    ):
        self.window_size = window_size
        self.learning_rate = learning_rate
        self.use_integrator = use_integrator
        self.use_scorecaster = use_scorecaster
        self.integrator_type = integrator_type
        self.K_I = K_I
        self.C_sat = C_sat
        self.ar_lags = ar_lags
        self.refit_frequency = refit_frequency

        self.data = None
        self.predictor = SimpleARPredictor(lags=ar_lags)

        # conformal state
        self.conformity_scores = []
        self.cumulative_error = 0.0
        self.current_quantile=None
        self.coverage_history=[]
        self.update_count=0
        self.score_window=20

    def fit(self, data:np.ndarray) -> None:
        self.data = data[-self.window_size:].copy()
        self.predictor.fit(self.data)

        # initialize from residuals
        if self.predictor.residuals is not None and len(self.predictor.residuals) > 0:
            self.conformity_scores = list(np.abs(self.predictor.residuals))
            self.current_quantile = np.percentile(self.conformity_scores, 95)
        else:
            self.current_quantile = np.std(self.data) * 2

    def _tan_integrator(self, x:float, t:int) -> float:
        if t <= 1:
            return 0.0
        arg = x * np.log(t) / (t * self.C_sat)
        arg = np.clip(arg, -np.pi/2 + 0.01, np.pi/2 - 0.01)
        return self.K_I * np.tan(arg)

    def _linear_integrator(self, x:float, t:int) -> float:
        return self.learning_rate * x
    
    def _scorecast(self) -> float:
        if len(self.conformity_scores) < self.score_window:
            return np.mean(self.conformity_scores) if self.conformity_scores else 0.0
        recent_scores = self.conformity_scores[-self.score_window:]
        weights = np.exp(-0.1 * np.arange(self.score_window)[::-1])
        weights /= weights.sum()
        return np.dot(weights, recent_scores)
    
    def predict_risk(self, alpha:float=0.05) -> tuple[float, float]:
        if self.data is None or len(self.data) < self.ar_lags:
            return (np.nan, np.nan)
        
        # point forecast
        point_forecast = self.predictor.predict(self.data)

        # calculate adaptive quantile
        t = len(self.conformity_scores) + 1

        # D control: scorecaster
        if self.use_scorecaster and len(self.conformity_scores) > 0:
            q_hat = self._scorecast()
        else:
            q_hat = self.current_quantile if self.current_quantile else 0.0

        # I control: Integrator
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
    
    def update(self, new_observation:float, alpha:float=0.05) -> None:
        self.update_count += 1

        # get prediction before updating
        if self.data is not None and len(self.data) >= self.ar_lags:
            point_forecast = self.predictor.predict(self.data)

            # conformity score
            score = np.abs(new_observation - point_forecast)
            self.conformity_scores.append(score)

            # check coverage
            lower, upper = self.predict_risk(alpha=alpha)
            covered = lower <= new_observation <= upper
            err_t = 0 if covered else 1

            # I control: Update cumulative error
            self.cumulative_error += (err_t - alpha)

            # P control: Update quantile
            if self.current_quantile is not None:
                self.current_quantile += self.learning_rate * (err_t - alpha)
                self.current_quantile = max(self.current_quantile, 0.0)

            self.coverage_history.append(covered)

            # update data
            if self.data is None:
                self.data = np.array([new_observation])
            else:
                self.data = np.append(self.data, new_observation)
                if len(self.data) > self.window_size:
                    self.data = self.data[-self.window_size:]

            if self.update_count % self.refit_frequency == 0:
                self.predictor.fit(self.data)

class AdaptiveConformalInference:
    """
    Adaptive Conformal Inference (ACI) - Gibbs & Candes (2021)
    Baseline method that adapts alpha_t instead of tracking quantile directly
    """

    def __init__(
        self,
        window_size:int=250,
        learning_rate:float=0.005,
        target_alpha:float=0.05,
        ar_lags:int=3,
        refit_frequency:int=10,
    ):
        self.window_size = window_size
        self.learning_rate = learning_rate
        self.target_alpha = target_alpha
        self.ar_lags = ar_lags
        self.refit_frequency = refit_frequency

        self.data=None
        self.predictor=SimpleARPredictor()
        self.conformity_scores = []
        self.alpha_t = target_alpha
        self.coverage_history = []
        self.update_count = 0

    def fit(self, data:np.ndarray) -> None:
        self.data = data[-self.window_size:].copy()
        self.predictor.fit(self.data)

        if self.predictor.residuals is not None:
            self.conformity_scores = list(np.abs(self.predictor.residuals))

    def predict_risk(self, alpha:float=0.05) -> tuple[float, float]:
        if self.data is None or len(self.conformity_scores) == 0:
            return (np.nan, np.nan)
        
        point_forecast = self.predictor.predict(self.data)

        effective_alpha = np.clip(self.alpha_t, 0.001, 0.999)
        quantile_level = 1 - effective_alpha
        q = np.percentile(self.conformity_scores, quantile_level * 100)

        return (point_forecast - q, point_forecast + q)
    
    def update(self, new_observation:float, alpha:float=0.05) -> None:
        self.update_count += 1

        if self.data is not None and len(self.data) >= self.ar_lags:
            point_forecast = self.predictor.predict(self.data)
            score = np.abs(new_observation - point_forecast)
            self.conformity_scores.append(score)

            lower, upper = self.predict_risk(alpha=alpha)
            covered = lower <= new_observation <= upper
            err_t = 0 if covered else 1

            # ACI update
            self.alpha_t = self.alpha_t - self.learning_rate * (err_t - self.target_alpha)
            self.coverage_history.append(covered)

            # update data
            if self.data is None:
                self.data = np.array([new_observation])
            else:
                self.data = np.append(self.data, new_observation)
                if len(self.data) > self.window_size:
                    self.data = self.data[-self.window_size:]

            if self.update_count % self.refit_frequency == 0:
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
    if violations == 0 or violations == n:
        return 0.0
    p_hat = violations / n
    lr = -2 * (
        (n - violations) * np.log(1 - alpha) + violations * np.log(alpha) -
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
        lr_ind = -2 * (
            n00 * np.log(1 - pi) + n01 * np.log(pi) +
            n10 * np.log(1 - pi) + n11 * np.log(pi) -
            n00 * np.log(1 - pi01) + n01 * np.log(pi01) -
            n10 * np.log(1 - pi11) + n11 * np.log(pi11)
        )
        return 1 - stats.chi2.cdf(lr_ind, df=1)
    except:
        return 1.0


def backtest_model(
        model,
        data:np.ndarray,
        train_size:int=250,
        alpha:float=0.05,
        model_name:str='Model'
    ):
    n = len(data)
    model.fit(data[:train_size])

    results = []
    violations = []

    for t in range(train_size, n):
        lower, upper = model.predict_risk(alpha)
        actual = data[t]
        is_violation = (actual < lower) or (actual > upper)
        violations.append(1 if is_violation else 0)

        results.append({
            'time':t,
            'actual':actual,
            'lower':lower,
            'upper':upper,
            'interval_width': upper - lower if not np.isnan(upper - lower) else np.nan,
            'violation': is_violation
        })

        model.update(actual, alpha)

    results_df = pd.DataFrame(results)
    violations_array = np.array(violations)
    total_violations = violations_array.sum()
    coverage = 1 - total_violations/len(violations)
    avg_width = results_df['interval_width'].mean()

    kupiec_p = kupiec_pof_test(total_violations, len(violations), alpha)
    christoffersen_p = christoffersen_test(violations_array)

    return BacktestResult(
        method=model_name,
        coverage=coverage,
        target_coverage=1-alpha,
        avg_interval_width=avg_width,
        violations=total_violations,
        total_observations=len(violations),
        violation_rate=total_violations/len(violations),
        conditional_coverage_pvalue=christoffersen_p,
        kupiec_pvalue=kupiec_p
    ), results_df


def generate_returns(
        n:int=1000,
        regime_changes:bool=True,
        seasonality:bool=True
) -> np.ndarray:
    returns = np.zeros(n)
    base_vol = 0.02

    if regime_changes:
        regime_points = [0, 200, 500, 700, n]
        regime_vol_mult = [1.0, 2.0, 0.8, 1.5, 1.0]
    else:
        regime_points = [0, n]
        regime_vol_mult = [1.0, 1.0]

    current_regime = 0

    for t in range(n):
        while current_regime < len(regime_points) - 2 and t >= regime_points[current_regime + 1]:
            current_regime += 1

        vol_t = base_vol * regime_vol_mult[current_regime]

        if t > 0:
            vol_t *= (1+0.3*np.sin(2*np.pi*t/252))

        returns[t] = vol_t * stats.t.rvs(df=5)

    return returns