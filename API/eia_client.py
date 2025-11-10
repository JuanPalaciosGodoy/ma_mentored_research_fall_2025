import requests
from typing import Optional, List, Union, Dict, Any
from datetime import datetime, date
from enum import Enum
import polars as pl

class EIAClient:
    """Client for EIA API"""

    URL_EIA = "https://api.eia.gov/v2/"
    API_EIA_KEY = "BwrKg7pSPEb0RLobj0ZdAqnILyR3Ug77LRT9ULAe"

    def __init__(self):
        self.session = requests.Session()


    def get_markets(self) -> dict:
        """
        Get EIA available markets in API

        Returns
        -------
            (dict): available market ids with description
        """

        # add EIA key
        params = {"api_key": self.API_EIA_KEY}

        return self._make_request(url=self.URL_EIA, params=params)

    def get_routes_in_market(self, market_id: str) -> dict:
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
        query = f"{self.URL_EIA}{market_id}"

        # add EIA key
        params = {"api_key": self.API_EIA_KEY}

        return self._make_request(url=query, params=params)

    def get_subroutes_in_market(self, market_id:str, route_id:str) -> dict:
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
        query = f"{self.URL_EIA}{market_id}/{route_id}"

        # add EIA key
        params = {"api_key": self.API_EIA_KEY}

        return self._make_request(url=query, params=params)

    def get_available_data_in_market(self, market_id:str, route_id:str, subroute_id:str=None) -> dict:
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
        query = f"{self.URL_EIA}{market_id}/{route_id}/{subroute_id}" if subroute_id else f"{self.URL_EIA}{market_id}/{route_id}"

        # add EIA key
        params = {"api_key": self.API_EIA_KEY}

        response = self._make_request(url=query, params=params)

        # validate data field is found in response
        if "data" in response["response"]:
            return response["response"]

        # no data fields found.
        available_subroutes = pl.DataFrame(response["response"]["routes"])
        with pl.Config(tbl_rows=-1):
            print(available_subroutes)
        raise ValueError(f"Please make sure to pass the parameter subroute_id. You can choose among the following list of subroutes for the market {market_id} and route {route_id}: {available_subroutes['id'].to_list()}")

    def _get_available_data_field_in_market(self, market_id:str, route_id:str, field:str, subroute_id:str=None) -> dict:
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
        available_data = self.get_available_data_in_market(market_id=market_id, route_id=route_id, subroute_id=subroute_id)

        return available_data[field]

    def get_available_data_fields_in_market(self, market_id:str, route_id:str, subroute_id:str=None) -> dict:
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

        return self._get_available_data_field_in_market(market_id=market_id, route_id=route_id, subroute_id=subroute_id, field="data")

    def get_available_frequency_in_market(self, market_id:str, route_id:str, subroute_id:str=None) -> dict:
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

        return self._get_available_data_field_in_market(market_id=market_id, route_id=route_id, subroute_id=subroute_id, field="frequency")

    def get_available_facets_in_market(self, market_id:str, route_id:str, subroute_id:str=None) -> dict:
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

        return self._get_available_data_field_in_market(market_id=market_id, route_id=route_id, subroute_id=subroute_id, field="facets")


    def get_available_info_in_market(self, market_id:str, route_id:str, subroute_id:str=None) -> dict:
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
        available_data = self.get_available_data_in_market(market_id=market_id, route_id=route_id, subroute_id=subroute_id)

        return {key: available_data[key] for key in ["id", "description", "startPeriod", "endPeriod"]}

    # ----- EIA DATA -----

    def get_eia_data(
        self,
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
            response = self.get_routes_in_market(market_id=market_id)
            available_routes = pl.DataFrame(response["response"]["routes"])
            with pl.Config(tbl_rows=-1):
                print(available_routes)
            raise ValueError(f"Please make sure to pass the parameter route_id. You can choose among the following list of routes for the market {market_id}: {available_routes['id'].to_list()}")

        # validate data is passed
        if not data:
            data_fields = pl.DataFrame(self.get_available_data_fields_in_market(market_id=market_id, route_id=route_id, subroute_id=subroute_id))
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

        # add EIA key
        params["api_key"] = self.API_EIA_KEY

        # create template string
        payload = f"{self.URL_EIA}{market_id}/{route_id}"
        payload = payload + f"/{subroute_id}" if subroute_id else payload

        # add data url
        payload = payload + "/data/?"

        return self._make_request(url=payload, params=params, headers=headers)


    def _make_request(self, url: str, params: Dict[str, Any]={}, headers: Dict[str, Any]={}) -> Dict[str, Any]:
        """Make HTTP request to API"""
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print("query: ", url)
            print("response text: ", response.text)
            print("response code: ", response.status_code)
            print("response: ", response)
            raise Exception(f"API request failed: {str(e)}")

    def close(self):
        """Close the session"""
        self.session.close()


# Example usage function
def example_usage():
    """Example demonstrating how to use the EIAClient"""

    # Initialize client
    client = EIAClient()

    try:
        # Example 1: Get available markets
        print("=== Available Markets ===")
        markets = client.get_markets()
        print(f"Available Markets: {pl.DataFrame(markets['response']['routes'])}")

        # Example 2: Get available market specific routes
        print("=== Available Natural Gas Routes ===")
        routes = client.get_routes_in_market(market_id='natural-gas')
        print(f"Available Natural Gas Routes: {pl.DataFrame(routes['response']['routes'])}")

        # Example 3: Get available market specific and route subroutes
        subroutes = client.get_subroutes_in_market(market_id='natural-gas', route_id='pri')
        print(f"Available Natural Gas - pri - subroutes: {pl.DataFrame(subroutes['response']['routes'])}")

        # Example 4: what information is available inside a sub-route
        info = client.get_available_info_in_market(market_id='natural-gas', route_id='pri', subroute_id='fut')
        print(f"Available Natural Gas - pri - fut information: {pl.DataFrame(info)}")

        # Example 5: what data types are available inside a sub-route
        data_fields = client.get_available_data_fields_in_market(market_id='natural-gas', route_id='pri', subroute_id='fut')
        print(f"Available Natural Gas - pri - fut data fields: {pl.DataFrame(data_fields)}")

        # Example 6: what frequencies are available inside a sub-route
        frequencies = client.get_available_frequency_in_market(market_id='natural-gas', route_id='pri', subroute_id='fut')
        print(f"Available Natural Gas - pri - fut frequencies: {pl.DataFrame(frequencies)}")

        # Example 7: what frequencies are available inside a sub-route
        facets = client.get_available_facets_in_market(market_id='natural-gas', route_id='pri', subroute_id='fut')
        print(f"Available Natural Gas - pri - fut facets: {pl.DataFrame(facets)}")

        # Example 8: get EIA data
        response = client.get_eia_data(
            market_id='natural-gas',
            route_id='pri',
            subroute_id='fut',
            data=['value'],
            frequency="daily",
            start_date="2025-01-01"
        )
        data = pl.DataFrame(response['response']['data'])
        print(f"Natural Gas - pri - fut - daily - value - 2025-01-01: {data}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the session
        client.close()


if __name__ == "__main__":
    example_usage()