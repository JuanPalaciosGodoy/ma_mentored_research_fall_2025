# IMPORTS
import requests
from keys import API_EIA_KEY, URL_EIA

def get_json(url:str, headers:dict) -> dict:

    # setup api key
    params = {"api_key":API_EIA_KEY}

    # get response
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()  # Assuming the response is JSON
        return data
    else:
        print("query: ", url)
        print("headers: ",  headers)
        print("response text: ", response.text)
        print("response code: ", response.status_code)
        print("response: ", response)

        raise ValueError("Failed to read data from EIA API.")

# QUERY DEFINITIONS

def get_eia_electricity_query(
    route:str,
    data_type:str,
    frequency:str=None,
    start_date:str=None,
    end_date:str=None,
    market_url:str="electricity",
    data:list=['value'],
    limit:str="5000",
    offset:str="0"
) -> dict:

    # create headers
    headers = {
        "offset":offset,
        "length":limit,
        "data": str(data)
        }

    # add optional parameters if defined
    if start_date:
        headers["start"]=start_date
    if end_date:
        headers["end"]=end_date
    if frequency:
        headers["frequency"]=frequency

    # create template string
    query = f"{URL_EIA}{market_url}/{route}/{data_type}/data/?"

    return get_json(url=query, headers=headers)