import datetime
import polars as pl
import pandas as pd
import numpy as np
from typing import Tuple, List

# external APIs
from fredapi import Fred
from API.meteo_client import OpenMeteoClient
from API.eia_client import EIAClient
from gridstatusio import GridStatusClient

# other internal imports
from data_transformations.transformations import add_derived_features, apply_boxcox_to_columns

# KEYS
FRED_API_KEY = "074ca13a0fb775130325ac8392ed51e3"
#GRIDSTATUS_API_KEY = 'e2d40b6dcfff48c6834bd445100cf76e'
GRIDSTATUS_API_KEY = '18148a1b3c274a9eb83e80bed9b7e82c'

# GENERAL PARAMS
START = "2019-01-01"
END = "2025-11-01"
TIME_ZONE = "US/Pacific"

# EIA PARAMS
eia_params = {
    # 1: corresponds to natural gas spot prices
    1: {
        "market_id": "natural-gas",
        "route_id": "pri",
        "subroute_id": "sum",
        "params": {"facets[process][]": "PG1", "facets[duoarea][]": "SCA"},
        "data": ["value"],
        "frequency": "monthly"
    },
}

# METEO PARAMS
meteo_historical_weather_params = {
    # 1: corresponds to HOUSTON load zone
    1: {
        "latitude": 35.37,
        "longitude": -119.01,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "cloud_cover_mean",
            "precipitation_sum",
            "wind_speed_10m_mean",
        ],
        "location": "TH_NP15_GEN-APND"
        }
}

# ERCOT PARAMS
ercot_spp_params = {
    1: {
        "dataset": "caiso_lmp_day_ahead_hourly",
        "filter_column": "location",
        "filter_value": "TH_NP15_GEN-APND",
    }
}

# FRED PARAMS
fred_params = {
    # 1: corresponds to GS10 -> interest rates
    1: {
        "series": 'GS10'
    },
    # 2: corresponds to T5YIE -> inflation
    2: {
        "series": 'T5YIE'
    }
}

# ----- READ ALL FEATURES -----
def read_features(
        meteo_params:dict,
        fred_params:dict,
        ercot_params:dict,
        eia_params:dict
    ) -> pd.DataFrame:

    # read ercot data
    df_ercot = get_ercot_features(params=ercot_params)
    df_ercot = df_ercot.groupby(by=['time','location','location_type','market']).mean().reset_index() # transform to daily data
    df_ercot['time'] = df_ercot['interval_start_local'].dt.date
    df_ercot['time'] = pd.to_datetime(df_ercot['time']).dt.tz_localize(TIME_ZONE)

    # read meteo data
    df_meteo = get_meteo_features(params=meteo_params)
    df_meteo = add_derived_features(df=df_meteo) # calculate tranformations
    df_meteo = df_meteo[[
        'time',
        'location',
        "heating_degrees",
        "cooling_degrees",
        "dew_point_simple",
        "sunshine_fraction",
        "rain_flag",
        "wind_squared",
        ]] # filter data

    # read fred data
    df_fred = get_fred_features(params=fred_params)

    # read eia data
    df_eia = get_eia_features(params=eia_params)

    # merge dataframes
    df = pd.merge(df_ercot, df_meteo, on=['time', 'location'], how='inner')
    df = pd.merge(df, df_fred, on=['time'], how='left')
    df = pd.merge(df, df_eia, on=['time'], how='left')

    return df

# ----- EIA DATA -----
def get_eia_features(params:dict) -> pd.DataFrame:

    # define client
    client = EIAClient()

    # get data
    df = pd.DataFrame()
    for key, param in params.items():
        # extract parameters
        market_id = param['market_id']
        route_id = param['route_id']
        subroute_id = param['subroute_id']
        data = param['data']
        frequency = param['frequency']

        response = client.get_eia_data(
                market_id=market_id,
                route_id=route_id,
                subroute_id=subroute_id,
                data=data,
                frequency=frequency,
                start_date=START,
                end_date=END
            )
        df_i = pd.DataFrame(response['response']['data'])

        df_i = monthly_to_daily_constant(df=df_i)

        # concatenate data
        df = pd.concat([df, df_i], axis=0)

    df.rename(columns={'period': 'time'}, inplace=True)

    # add time zone
    df['time'] = pd.to_datetime(df['time']).dt.tz_localize(TIME_ZONE)

    df = df.pivot(columns='series', index='time', values="value")
    df.reset_index(inplace=True)

    return df

def monthly_to_daily_constant(
    df: pd.DataFrame,
    period_col: str = "period",
    value_col: str = "value",
) -> pd.DataFrame:
    """
    Transform EIA-style monthly data to daily data using constant interpolation.

    Handles:
    - String periods like "2025-04"
    - 'null' / NaN in value
    - Duplicate months in `period` by aggregating them first

    Steps:
    - Parse period as month start.
    - Aggregate duplicate months (value = mean, others = first).
    - Fill missing months via forward/backward fill.
    - Upsample to daily and forward/backward fill again.
    """

    df = df.copy()

    # 1) Parse period as a timestamp (YYYY-MM -> first day of month)
    df[period_col] = pd.to_datetime(df[period_col].astype(str) + "-01")

    # 2) Convert value to numeric (e.g. "null" -> NaN)
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

    # 3) Sort by period
    df = df.sort_values(period_col)

    # 4) Aggregate duplicates by month (period)
    #    value: average (or last), metadata: first
    meta_cols: List[str] = [c for c in df.columns if c not in [period_col, value_col]]

    agg_dict = {value_col: "mean"}
    for col in meta_cols:
        agg_dict[col] = "first"

    df = (
        df.groupby(period_col, as_index=False)
          .agg(agg_dict)
          .sort_values(period_col)
          .set_index(period_col)
    )

    # 5) Build a continuous monthly index from min to max
    monthly_index = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq="MS",  # Month Start
    )

    # 6) Reindex to the full monthly span
    df = df.reindex(monthly_index)

    # 7) Constant interpolation across months (forward/backward fill)
    df[value_col] = df[value_col].ffill().bfill()
    for col in meta_cols:
        df[col] = df[col].ffill().bfill()

    # 8) Upsample from monthly to daily
    daily_index = pd.date_range(
        start=monthly_index.min(),
        end=monthly_index.max(),
        freq="D",
    )
    df_daily = df.reindex(daily_index)

    # 9) Constant interpolation across days
    df_daily[value_col] = df_daily[value_col].ffill().bfill()
    for col in meta_cols:
        df_daily[col] = df_daily[col].ffill().bfill()

    # 10) Move index into a 'date' column
    df_daily = df_daily.reset_index().rename(columns={"index": "period"})

    return df_daily

# ----- ERCOT DATA -----
def get_ercot_features(params: dict) -> pd.DataFrame:

    # define client
    client = GridStatusClient(GRIDSTATUS_API_KEY)

    # get data
    df = pd.DataFrame()
    for key, param in params.items():
        # extract parameters
        dataset = param['dataset']
        filter_column = param['filter_column']
        filter_value = param['filter_value']

        # get dataframe

        df_i = client.get_dataset(
            dataset=dataset,
            start=START,
            end=END,
            timezone=TIME_ZONE,
            filter_column=filter_column,
            filter_value=filter_value,
        )

        # concatenate data
        df = pd.concat([df, df_i], axis=0)

    df['time'] = df['interval_start_local'].dt.date
    df['time'] = pd.to_datetime(df['time']).dt.tz_localize(TIME_ZONE)

    return df

# ----- METEO DATA -----
def get_meteo_features(params: dict) -> pd.DataFrame:

    # define open-meteo client
    client = OpenMeteoClient()

    # get data
    df = pd.DataFrame()
    for key, param in params.items():
        # extract parameters
        latitude = param['latitude']
        longitude = param['longitude']
        daily = param['daily']
        location = param['location']

        # get historical data
        response = client.get_historical_weather(
                latitude=latitude,
                longitude=longitude,
                start_date=START,
                end_date=END,
                daily=daily,
                timezone=TIME_ZONE
            )
        df_i = pd.DataFrame(response.get('daily', {}))

        # add longitude and latitude columns
        df_i.loc[:, 'location'] = location

        # concatenate data
        df = pd.concat([df, df_i], axis=0)

    # add time zone
    df['time'] = pd.to_datetime(df['time']).dt.tz_localize(TIME_ZONE)

    return df

# ----- FRED DATA -----
def get_fred_features(params: dict) -> pd.DataFrame:

    # define FRED client
    client = Fred(api_key=FRED_API_KEY)

    # get data
    df = pd.DataFrame()
    for key, param in params.items():
        # extract parameters
        series = param['series']

        # get data
        df_i = client.get_series(
            series,
            observation_start=START,
            observation_end=END,
        )

        idx = pd.date_range(df_i.index.min(), END, freq='D')
        df_i= df_i.reindex(idx, method='ffill')

        # add series name as column
        df_i = df_i.to_frame()
        df_i.loc[:, 'series'] = series

        # concatenate data
        df = pd.concat([df, df_i], axis=0)

    df.reset_index(inplace=True)
    df.rename(columns={'index': 'time'}, inplace=True)
    df = df.pivot(columns='series', index='time', values=0)
    df.reset_index(inplace=True)

    # add time zone
    df['time'] = pd.to_datetime(df['time']).dt.tz_localize(TIME_ZONE)

    return df

# ----- FEATURES -----
FEATURES = read_features(
    meteo_params=meteo_historical_weather_params,
    ercot_params=ercot_spp_params,
    fred_params=fred_params,
    eia_params=eia_params
)

def prepare_target_and_exog(
    price_col: str = "spp",
    time_col: str = "time",
    exog_cols: list = [],
    use_log_returns: bool = True,
) -> Tuple[np.ndarray, np.ndarray, pd.Index, List[str]]:
    """
    Prepare y (returns) and standardized X (exogenous variables) for SARIMAX / AR models.

    - y: log-returns or simple returns of `price_col`
    - X: standardized exogenous variables after NaN interpolation
    """

    df = FEATURES  # Global dataframe

    # 1) Sort by time to ensure correct ordering
    if time_col in df.columns:
        df = df.sort_values(time_col)
    else:
        df = df.sort_index()

    df = df.copy()

    # 2) Compute returns of price_col
    if use_log_returns:
        df["y"] = np.log(df[price_col]).diff()
    else:
        df["y"] = df[price_col].pct_change()

    # Drop the first row where return is NaN
    df = df.dropna(subset=["y"])

    # 3) Extract exogenous variables
    X = df[exog_cols].copy()

    # Fill missing values (constant interpolation)
    X = X.interpolate(method="pad", limit_direction="forward")
    X = X.fillna(method="bfill").fillna(method="ffill")

    # 4) Standardize exogenous variables (z-score scaling)
    means = X.mean()
    stds = X.std(ddof=0)

    # Avoid division by zero: replace zeros with 1
    stds_replaced = stds.replace(0, 1.0)

    X_standardized = (X - means) / stds_replaced

    # 5) Prepare y (fill just in case)
    y = df["y"].copy()
    y = y.interpolate(method="pad", limit_direction="forward")
    y = y.fillna(method="bfill").fillna(method="ffill")

    # 6) Return arrays and index
    return (
        y.to_numpy(),
        X_standardized.to_numpy(),
        df[time_col],
        exog_cols,
    )