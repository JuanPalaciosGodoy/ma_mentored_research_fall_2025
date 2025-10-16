# IMPORTS
import requests
from keys import API_EIA_KEY, URL_EIA
import polars as pl

def get_json(url:str, params:dict={}, headers:dict={}) -> dict:

    # setup api key
    params["api_key"] = API_EIA_KEY

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

# ----- EIA METADATA -----

def get_markets() -> dict:
    """
    Get EIA available markets in API

    Returns
    -------
        (dict): available market ids with description
    """
    return get_json(url=URL_EIA)

def get_routes_in_market(market_id: str) -> dict:
    """
    Get EIA available routes in market

    Parameters
    ----------
        market_id (str): market id consistent with EIA's API. To find valid IDs use the function `get_markets()`

    Returns
    -------
        (dict): available routes inside of specified market
    """

    # create template string
    query = f"{URL_EIA}{market_id}"

    return get_json(url=query)

def get_subroutes_in_market(market_id:str, route_id:str) -> dict:
    """
    Get EIA available subroutes in field of market

    Parameters
    ----------
        market_id (str): market id consistent with EIA's API (e.g. `electricity`). To find valid IDs use the function `get_markets()`

        route_id (str): route id consistent with EIA's API (e.g. `retail-sales`). To find valid IDs use the function `get_routes_in_market()`

    Returns
    -------
        (dict): available subroutes inside of specified market and route id.
    """

    # create template string
    query = f"{URL_EIA}{market_id}/{route_id}"

    return get_json(url=query)

def get_available_data_in_market(market_id:str, route_id:str, subroute_id:str=None) -> dict:
    """
    Get EIA available data in field of market

    Parameters
    ----------
        market_id (str): market id consistent with EIA's API (e.g. `natural-gas`). To find valid IDs use the function `get_markets()`

        route_id (str): route id consistent with EIA's API (e.g. `pri`). To find valid IDs use the function `get_routes_in_market()`

        subroute_id (str) (optional): subroute id consistent with EIA's API (e.g. `fut`). To find valid IDs use the function `get_routes_in_market()`

    Returns
    -------
        (dict): available data inside of specified market, route id, and subroute id if specified.
    """

    # create template string
    query = f"{URL_EIA}{market_id}/{route_id}/{subroute_id}" if subroute_id else f"{URL_EIA}{market_id}/{route_id}"

    response = get_json(url=query)

    # validate data field is found in response
    if "data" in response["response"]:
        return response["response"]

    # no data fields found.
    available_subroutes = pl.DataFrame(response["response"]["routes"])
    with pl.Config(tbl_rows=-1):
        print(available_subroutes)
    raise ValueError(f"Please make sure to pass the parameter subroute_id. You can choose among the following list of subroutes for the market {market_id} and route {route_id}: {available_subroutes['id'].to_list()}")

def _get_available_data_field_in_market(market_id:str, route_id:str, field:str, subroute_id:str=None) -> dict:
    """
    Get EIA available data fields in market

    Parameters
    ----------
        market_id (str): market id consistent with EIA's API (e.g. `natural-gas`). To find valid IDs use the function `get_markets()`

        route_id (str): route id consistent with EIA's API (e.g. `pri`). To find valid IDs use the function `get_routes_in_market()`

        subroute_id (str) (optional): subroute id consistent with EIA's API (e.g. `fut`). To find valid IDs use the function `get_routes_in_market()`

    Returns
    -------
        (dict): available data fields inside of specified market, route id, and subroute id if specified.
    """

    # get available data
    available_data = get_available_data_in_market(market_id=market_id, route_id=route_id, subroute_id=subroute_id)

    return available_data[field]

def get_available_data_fields_in_market(market_id:str, route_id:str, subroute_id:str=None) -> dict:
    """
    Get EIA available data fields in market

    Parameters
    ----------
        market_id (str): market id consistent with EIA's API (e.g. `natural-gas`). To find valid IDs use the function `get_markets()`

        route_id (str): route id consistent with EIA's API (e.g. `pri`). To find valid IDs use the function `get_routes_in_market()`

        subroute_id (str) (optional): subroute id consistent with EIA's API (e.g. `fut`). To find valid IDs use the function `get_routes_in_market()`

    Returns
    -------
        (dict): available data fields inside of specified market, route id, and subroute id if specified.
    """

    return _get_available_data_field_in_market(market_id=market_id, route_id=route_id, subroute_id=subroute_id, field="data")

def get_available_frequency_in_market(market_id:str, route_id:str, subroute_id:str=None) -> dict:
    """
    Get EIA available frequencies in market

    Parameters
    ----------
        market_id (str): market id consistent with EIA's API (e.g. `natural-gas`). To find valid IDs use the function `get_markets()`

        route_id (str): route id consistent with EIA's API (e.g. `pri`). To find valid IDs use the function `get_routes_in_market()`

        subroute_id (str) (optional): subroute id consistent with EIA's API (e.g. `fut`). To find valid IDs use the function `get_routes_in_market()`

    Returns
    -------
        (dict): available frequencies inside of specified market, route id, and subroute id if specified.
    """

    return _get_available_data_field_in_market(market_id=market_id, route_id=route_id, subroute_id=subroute_id, field="frequency")

def get_available_facets_in_market(market_id:str, route_id:str, subroute_id:str=None) -> dict:
    """
    Get EIA available facets in market

    Parameters
    ----------
        market_id (str): market id consistent with EIA's API (e.g. `natural-gas`). To find valid IDs use the function `get_markets()`

        route_id (str): route id consistent with EIA's API (e.g. `pri`). To find valid IDs use the function `get_routes_in_market()`

        subroute_id (str) (optional): subroute id consistent with EIA's API (e.g. `fut`). To find valid IDs use the function `get_routes_in_market()`

    Returns
    -------
        (dict): available facets inside of specified market, route id, and subroute id if specified.
    """

    return _get_available_data_field_in_market(market_id=market_id, route_id=route_id, subroute_id=subroute_id, field="facets")


def get_available_info_in_market(market_id:str, route_id:str, subroute_id:str=None) -> dict:
    """
    Get EIA available info in market

    Parameters
    ----------
        market_id (str): market id consistent with EIA's API (e.g. `natural-gas`). To find valid IDs use the function `get_markets()`

        route_id (str): route id consistent with EIA's API (e.g. `pri`). To find valid IDs use the function `get_routes_in_market()`

        subroute_id (str) (optional): subroute id consistent with EIA's API (e.g. `fut`). To find valid IDs use the function `get_routes_in_market()`

    Returns
    -------
        (dict): available info inside of specified market, route id, and subroute id if specified.
    """

    # get available data
    available_data = get_available_data_in_market(market_id=market_id, route_id=route_id, subroute_id=subroute_id)

    return {key: available_data[key] for key in ["id", "description", "startPeriod", "endPeriod"]}

# ----- EIA DATA -----

def get_eia_data(
    market_id:str,
    route_id:str=None,
    data:list=[],
    subroute_id:str=None,
    params:dict={},
    frequency:str=None,
    start_date:str=None,
    end_date:str=None,
    limit:str="5000",
    offset:str="0"
) -> dict:

    # validate route_id is passed
    if not route_id:
        response = get_routes_in_market(market_id=market_id)
        available_routes = pl.DataFrame(response["response"]["routes"])
        with pl.Config(tbl_rows=-1):
            print(available_routes)
        raise ValueError(f"Please make sure to pass the parameter route_id. You can choose among the following list of routes for the market {market_id}: {available_routes['id'].to_list()}")

    # validate data is passed
    if not data:
        data_fields = pl.DataFrame(get_available_data_fields_in_market(market_id=market_id, route_id=route_id, subroute_id=subroute_id))
        with pl.Config(tbl_rows=-1):
            print("Data Fields: \n", data_fields)
        raise ValueError(f"Please make sure to pass the parameter data. This should be a list containing the desired data fields. For the market {market_id}, you can choose a subset of the following list: {data_fields}")

    # create headers
    headers = {
        "offset":offset,
        "length":limit
    }

    # add data to params
    for i in range(len(data)):
        params[f"data[{i}]"] = data[i]

    # add optional parameters if defined
    if start_date:
        params["start"]=start_date
    if end_date:
        params["end"]=end_date
    if frequency:
        params["frequency"]=frequency

    # create template string
    payload = f"{URL_EIA}{market_id}/{route_id}"
    payload = payload + f"/{subroute_id}" if subroute_id else payload

    # add data url
    payload = payload + "/data/?"

    return get_json(url=payload, params=params, headers=headers)