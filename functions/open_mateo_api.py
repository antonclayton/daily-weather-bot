import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

def get_weather_data(LATITUDE, LONGITUDE):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": ["temperature_2m", "precipitation"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "daylight_duration", "uv_index_max", "precipitation_hours", "precipitation_probability_max"],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "America/Los_Angeles",
        "forecast_days": 1
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    return response

def generate_hourly_df(response):
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["precipitation"] = hourly_precipitation

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    return hourly_dataframe

def generate_daily_df(response):
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_sunrise = daily.Variables(2).ValuesAsNumpy()
    daily_sunset = daily.Variables(3).ValuesAsNumpy()
    daily_daylight_duration = daily.Variables(4).ValuesAsNumpy()
    daily_uv_index_max = daily.Variables(5).ValuesAsNumpy()
    daily_precipitation_hours = daily.Variables(6).ValuesAsNumpy()
    daily_precipitation_probability_max = daily.Variables(7).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["sunrise"] = daily_sunrise
    daily_data["sunset"] = daily_sunset
    daily_data["daylight_duration"] = daily_daylight_duration
    daily_data["uv_index_max"] = daily_uv_index_max
    daily_data["precipitation_hours"] = daily_precipitation_hours
    daily_data["precipitation_probability_max"] = daily_precipitation_probability_max

    daily_dataframe = pd.DataFrame(data = daily_data)
    return daily_dataframe
