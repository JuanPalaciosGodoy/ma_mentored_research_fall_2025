import datetime
import polars as pl
import pandas as pd

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
START = "2020-01-01"
END = "2025-11-01"
TIME_ZONE = "US/Central"

# EIA PARAMS
eia_params = {
    # 1: corresponds to natural gas spot prices
    1: {
        "market_id": "natural-gas",
        "route_id": "pri",
        "subroute_id": "fut",
        "data": ["value"],
        "frequency": "daily"
    },
    # 2: corresponds to petroleum
    2: {
        "market_id": "petroleum",
        "route_id": "pri",
        "subroute_id": "spt",
        "data": ["value"],
        "frequency": "daily"
    }
}

# METEO PARAMS
meteo_historical_weather_params = {
    # 1: corresponds to HOUSTON load zone
    1: {
        "latitude": 29.76,
        "longitude": 95.36,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "cloud_cover_mean",
            "precipitation_sum",
            "wind_speed_10m_mean",
        ],
        "location": "LZ_HOUSTON"
        }
}

# ERCOT PARAMS
ercot_spp_params = {
    1: {
        "dataset": "ercot_spp_day_ahead_hourly",
        "filter_column": "location",
        "filter_value": "LZ_HOUSTON",
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
    df_daily = df_ercot.groupby(by=['time','location','location_type','market']).mean().reset_index() # transform to daily data

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
    df = pd.merge(df_daily, df_meteo, on=['time', 'location'], how='inner')
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

        # concatenate data
        df = pd.concat([df, df_i], axis=0)

    df.rename(columns={'period': 'time'}, inplace=True)

    # add time zone
    df['time'] = pd.to_datetime(df['time']).dt.tz_localize(TIME_ZONE)

    df = df.pivot(columns='series', index='time', values="value")
    df.reset_index(inplace=True)

    return df

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