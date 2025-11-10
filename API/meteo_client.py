import requests
from typing import Optional, List, Union, Dict, Any
from datetime import datetime, date
from enum import Enum
import polars as pl

class OpenMeteoClient:
    """Client for Open-Meteo API"""

    BASE_URL = "https://api.open-meteo.com/v1"
    HISTORICAL_URL = "https://archive-api.open-meteo.com/v1"
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1"
    AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1"

    def __init__(self):
        self.session = requests.Session()

    def get_weather_forecast(
        self,
        latitude: float,
        longitude: float,
        hourly: Optional[List[Union[str, Enum]]] = None,
        daily: Optional[List[Union[str, Enum]]] = None,
        current: Optional[List[Union[str, Enum]]] = None,
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
        precipitation_unit: str = "mm",
        timezone: str = "auto",
        past_days: int = 0,
        forecast_days: int = 7,
        start_date: Optional[Union[str, date]] = None,
        end_date: Optional[Union[str, date]] = None,
        models: Optional[Union[str, List[str]]] = None,
        cell_selection: str = "nearest",
        apikey: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get weather forecast data from Open-Meteo API

        Parameters:
        -----------
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            hourly: List of hourly weather variables
            daily: List of daily weather variables
            current: List of current weather variables
            temperature_unit: Temperature unit (celsius/fahrenheit)
            wind_speed_unit: Wind speed unit (kmh/ms/mph/kn)
            precipitation_unit: Precipitation unit (mm/inch)
            timezone: Timezone (auto or IANA timezone)
            past_days: Number of past days to include (0-92)
            forecast_days: Number of forecast days (1-16)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            models: Weather model(s) to use
            cell_selection: Cell selection method (land/sea/nearest)
            apikey: API key for commercial usage

        Returns:
        --------
            Dictionary containing weather data

        Example:
            >>> client = OpenMeteoClient()
            >>> data = client.get_weather_forecast(
            ...     latitude=52.52,
            ...     longitude=13.41,
            ...     hourly=["temperature_2m", "precipitation"],
            ...     daily=["temperature_2m_max", "temperature_2m_min"],
            ...     current=["temperature_2m", "wind_speed_10m"]
            ... )
        """
        url = f"{self.BASE_URL}/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "temperature_unit": temperature_unit,
            "wind_speed_unit": wind_speed_unit,
            "precipitation_unit": precipitation_unit,
            "timezone": timezone,
            "cell_selection": cell_selection
        }

        # Add hourly parameters
        if hourly:
            params["hourly"] = self._format_parameters(hourly)

        # Add daily parameters
        if daily:
            params["daily"] = self._format_parameters(daily)

        # Add current parameters
        if current:
            params["current"] = self._format_parameters(current)

        # Add time range parameters
        if past_days > 0:
            params["past_days"] = past_days

        if forecast_days != 7:
            params["forecast_days"] = forecast_days

        if start_date:
            params["start_date"] = self._format_date(start_date)

        if end_date:
            params["end_date"] = self._format_date(end_date)

        # Add models
        if models:
            if isinstance(models, list):
                params["models"] = ",".join(models)
            else:
                params["models"] = models

        # Add API key if provided
        if apikey:
            params["apikey"] = apikey

        return self._make_request(url, params)

    def get_air_quality(
        self,
        latitude: float,
        longitude: float,
        hourly: Optional[List[Union[str, Enum]]] = None,
        domains: str = "auto",
        timezone: str = "auto",
        past_days: int = 0,
        forecast_days: int = 7
    ) -> Dict[str, Any]:
        """
        Get air quality data from Open-Meteo API

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            hourly: List of air quality variables
            domains: Forecast domain (auto/cams_europe/cams_global)
            timezone: Timezone
            past_days: Number of past days
            forecast_days: Number of forecast days

        Returns:
            Dictionary containing air quality data
        """
        url = f"{self.AIR_QUALITY_URL}/air-quality"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "domains": domains
        }

        if hourly:
            params["hourly"] = self._format_parameters(hourly)

        if past_days > 0:
            params["past_days"] = past_days

        if forecast_days != 7:
            params["forecast_days"] = forecast_days

        return self._make_request(url, params)

    def get_marine_forecast(
        self,
        latitude: float,
        longitude: float,
        hourly: Optional[List[Union[str, Enum]]] = None,
        daily: Optional[List[Union[str, Enum]]] = None,
        timezone: str = "auto",
        past_days: int = 0,
        forecast_days: int = 7,
        length_unit: str = "metric"
    ) -> Dict[str, Any]:
        """
        Get marine weather forecast

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            hourly: List of hourly marine variables
            daily: List of daily marine variables
            timezone: Timezone
            past_days: Number of past days
            forecast_days: Number of forecast days
            length_unit: Length unit (metric/imperial)

        Returns:
            Dictionary containing marine data
        """
        url = f"{self.BASE_URL}/marine"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "length_unit": length_unit
        }

        if hourly:
            params["hourly"] = self._format_parameters(hourly)

        if daily:
            params["daily"] = self._format_parameters(daily)

        if past_days > 0:
            params["past_days"] = past_days

        if forecast_days != 7:
            params["forecast_days"] = forecast_days

        return self._make_request(url, params)

    def get_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: Union[str, date],
        end_date: Union[str, date],
        hourly: Optional[List[Union[str, Enum]]] = None,
        daily: Optional[List[Union[str, Enum]]] = None,
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
        precipitation_unit: str = "mm",
        timezone: str = "auto"
    ) -> Dict[str, Any]:
        """
        Get historical weather data

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            hourly: List of hourly variables
            daily: List of daily variables
            temperature_unit: Temperature unit
            wind_speed_unit: Wind speed unit
            precipitation_unit: Precipitation unit
            timezone: Timezone

        Returns:
            Dictionary containing historical weather data
        """
        url = f"{self.HISTORICAL_URL}/archive"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": self._format_date(start_date),
            "end_date": self._format_date(end_date),
            "temperature_unit": temperature_unit,
            "wind_speed_unit": wind_speed_unit,
            "precipitation_unit": precipitation_unit,
            "timezone": timezone
        }

        if hourly:
            params["hourly"] = self._format_parameters(hourly)

        if daily:
            params["daily"] = self._format_parameters(daily)

        return self._make_request(url, params)

    def get_geocoding(
        self,
        name: str,
        count: int = 10,
        language: str = "en",
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Search for locations by name

        Args:
            name: Location name to search
            count: Number of results (1-100)
            language: Language code (en, de, fr, etc.)
            format: Response format (json/protobuf)

        Returns:
            Dictionary containing location results
        """
        url = f"{self.GEOCODING_URL}/search"

        params = {
            "name": name,
            "count": count,
            "language": language,
            "format": format
        }

        return self._make_request(url, params)

    def get_elevation(
        self,
        latitude: Union[float, List[float]],
        longitude: Union[float, List[float]]
    ) -> Dict[str, Any]:
        """
        Get elevation data for coordinates

        Args:
            latitude: Single latitude or list of latitudes
            longitude: Single longitude or list of longitudes

        Returns:
            Dictionary containing elevation data
        """
        url = f"{self.BASE_URL}/elevation"

        params = {}

        if isinstance(latitude, list):
            params["latitude"] = ",".join(map(str, latitude))
        else:
            params["latitude"] = latitude

        if isinstance(longitude, list):
            params["longitude"] = ",".join(map(str, longitude))
        else:
            params["longitude"] = longitude

        return self._make_request(url, params)

    def _format_parameters(self, params: List[Union[str, Enum]]) -> str:
        """Convert parameter list to comma-separated string"""
        formatted = []
        for param in params:
            if isinstance(param, Enum):
                formatted.append(param.value)
            else:
                formatted.append(param)
        return ",".join(formatted)

    def _format_date(self, date_input: Union[str, date]) -> str:
        """Format date to YYYY-MM-DD string"""
        if isinstance(date_input, date):
            return date_input.strftime("%Y-%m-%d")
        return date_input

    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to API"""
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def close(self):
        """Close the session"""
        self.session.close()


# Example usage function
def example_usage():
    """Example demonstrating how to use the OpenMeteoClient"""

    # Initialize client
    client = OpenMeteoClient()

    try:
        # Example 1: Get current weather and forecast
        print("=== Weather Forecast ===")
        weather_data = client.get_weather_forecast(
            latitude=52.52,
            longitude=13.41,
            hourly=["temperature_2m", "precipitation", "wind_speed_10m"],
            daily=["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            current=["temperature_2m", "relative_humidity_2m", "wind_speed_10m"],
            timezone="Europe/Berlin",
            forecast_days=7
        )
        print(f"Location: {weather_data.get('latitude')}, {weather_data.get('longitude')}")
        print(f"Timezone: {weather_data.get('timezone')}")
        if 'current' in weather_data:
            print(f"Current Temperature: {pl.DataFrame(weather_data['current'])}")

        # Example 2: Get air quality
        print("\n=== Air Quality ===")
        air_quality = client.get_air_quality(
            latitude=52.52,
            longitude=13.41,
            hourly=["pm10", "pm2_5", "carbon_monoxide", "ozone"],
            forecast_days=3
        )
        print(f"Air Quality Data Retrieved: {pl.DataFrame(air_quality.get('hourly', {}))}")

        # Example 3: Search for location
        print("\n=== Geocoding ===")
        locations = client.get_geocoding(name="Berlin", count=5)
        if 'results' in locations:
            for loc in locations['results']:
                print(f"{loc.get('name')}, {loc.get('country')} - "
                      f"Lat: {loc.get('latitude')}, Lon: {loc.get('longitude')}")

        # Example 4: Get elevation
        print("\n=== Elevation ===")
        elevation = client.get_elevation(latitude=52.52, longitude=13.41)
        print(f"Elevation: {elevation.get('elevation', [None])} meters")

        # Example 5: Get historical weather
        print("\n=== Historical Weather ===")
        historical = client.get_historical_weather(
            latitude=52.52,
            longitude=13.41,
            start_date="2024-01-01",
            end_date="2024-01-07",
            daily=["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]
        )
        print(f"Historical data points: {pl.DataFrame(historical.get('daily', {}))}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the session
        client.close()


if __name__ == "__main__":
    example_usage()