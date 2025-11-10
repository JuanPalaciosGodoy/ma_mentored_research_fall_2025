import pandas as pd


# constants
BASE_TEMPERATURE_C = 18

def get_HDD(df:pd.DataFrame) -> pd.DataFrame:
    """
    calculate heating degree days calculated as  BASE_TEMPERATURE_C - (temperature_2m_max + temperature_2m_min)/ 2

    Parameters:
    -----------
        df(pd.DataFrame): must contain the columns `temperature_2m_max` in celsius and `temperature_2m_min` in celsius

    Returns:
    --------
        (pd.DataFrame): original dataframe with additional column `hdd` corresponding to the heating degree days
    """

    # calculation
    average_temperature = (df['temperature_2m_max'] + df['temperature_2m_min'])/2
    hdd = BASE_TEMPERATURE_C - average_temperature

    # add hdd to dataframe
    df.loc[:, 'hdd'] = 0
    df.loc[hdd > 0, 'hdd'] = hdd.loc[hdd > 0]

    return df


def get_CDD(df:pd.DataFrame) -> pd.DataFrame:
    """
    calculate cooling degree days calculated as (temperature_2m_max + temperature_2m_min)/ 2 - BASE_TEMPERATURE_C

    Parameters:
    -----------
        df(pd.DataFrame): must contain the columns `temperature_2m_max` in celsius and `temperature_2m_min` in celsius

    Returns:
    --------
        (pd.DataFrame): original dataframe with additional column `cdd` corresponding to the cooling degree days
    """

    # calculation
    average_temperature = (df['temperature_2m_max'] + df['temperature_2m_min'])/2
    cdd = average_temperature - BASE_TEMPERATURE_C

    # add hdd to dataframe
    df.loc[:, 'cdd'] = 0
    df.loc[cdd > 0, 'cdd'] = cdd.loc[cdd > 0]

    return df
