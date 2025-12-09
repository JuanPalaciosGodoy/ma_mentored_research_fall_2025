import pandas as pd
import numpy as np
from scipy.stats import boxcox


# constants
BASE_TEMPERATURE_C = 18

def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived weather variables to the DataFrame.

    Uses:
      * Heating Degrees: max(18 - Temp, 0)
      * Cooling Degrees: max(Temp - 18, 0)
      * Dew Point (approx): Temp - (100 - Humidity)/5
      * Sunshine Fraction: 100 - Cloud cover
      * Rain flag : 1 if Precipitation > 0, else 0
      * Wind squared: Wind speed ** 2
      * Interaction term between Temperature and Humidity
    """
    df = df.copy()

    temp = df["temperature_2m_mean"]
    hum = df["relative_humidity_2m_mean"]
    cloud = df["cloud_cover_mean"]
    precip = df["precipitation_sum"]
    wind = df["wind_speed_10m_mean"]

    # Heating/Cooling Degree Hours (base 18°C)
    df["heating_degrees"] = np.maximum(BASE_TEMPERATURE_C - temp, 0.0)
    df["cooling_degrees"] = np.maximum(temp - BASE_TEMPERATURE_C, 0.0)

    # Simple dew-point approximation: Temp - (100 - RH)/5
    df["dew_point_simple"] = temp - (100.0 - hum) / 5.0

    # Sunshine fraction in %, given cloud cover in %
    df["sunshine_fraction"] = 100.0 - cloud

    # Rain indicator
    df["rain_flag"] = (precip > 0.0).astype(int)

    # Wind squared
    df["wind_squared"] = wind ** 2

    return df



def boxcox_series(
    s: pd.Series,
    lmbda: float | None = None,
    eps: float = 1e-6,
) -> tuple[pd.Series, dict]:
    """
    Apply Box–Cox to a pandas Series.

    * Shifts data if needed so that all values > 0
    * Ignores NaNs when fitting
    * Returns transformed series + {lambda, shift}
    """
    # Work on a copy as float
    x = s.to_numpy(dtype=float)
    mask = np.isfinite(x)
    x_valid = x[mask]

    if x_valid.size == 0:
        # Nothing to transform
        return s.copy().astype(float), {"lambda": lmbda, "shift": 0.0}

    # Shift so min > 0 (Box–Cox requirement)
    min_x = np.min(x_valid)
    shift = 0.0
    if min_x <= 0:
        shift = -min_x + eps

    x_pos = x_valid + shift

    # Apply Box–Cox
    if lmbda is None:
        x_bc, fitted_lambda = boxcox(x_pos)   # finds optimal lambda
    else:
        x_bc = boxcox(x_pos, lmbda=lmbda)
        fitted_lambda = lmbda

    # Rebuild full array with NaNs in original NaN positions
    result = np.full_like(x, np.nan, dtype=float)
    result[mask] = x_bc

    transformed = pd.Series(result, index=s.index, name=s.name)
    return transformed, {"lambda": float(fitted_lambda), "shift": float(shift)}


def apply_boxcox_to_columns(
    df: pd.DataFrame,
    cols: list[str],
) -> tuple[pd.DataFrame, dict]:
    """
    Apply Box–Cox to multiple columns.

    Returns:
      * new DataFrame with <col>_boxcox columns
      * dict mapping col -> {'lambda': ..., 'shift': ...}
    """
    df_bc = df.copy()
    params: dict[str, dict] = {}

    for col in cols:
        transformed, meta = boxcox_series(df[col])
        new_col = f"{col}_boxcox"
        df_bc[new_col] = transformed
        params[col] = meta

    return df_bc, params
