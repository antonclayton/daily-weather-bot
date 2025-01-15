import sys

from dotenv import load_dotenv
import os
load_dotenv()

import pandas as pd


API_KEY=os.getenv("API_KEY")
CITY="Milpitas"
STATE_CODE="06"
NAME="Anton"


# city to geocode first (lat and lon)
URL=f"http://api.openweathermap.org/geo/1.0/direct?q={CITY},{STATE_CODE}&limit=2&appid={API_KEY}"

from functions import get_geocodes
LATITUDE,LONGITUDE = get_geocodes(URL)

# ADD GREATER ERROR HANDLING IN GEO CODE FUNCTION
if LATITUDE is None or LONGITUDE is None:
    sys.exit("Error getting latitude and longitude!")


# open mateo for daily weather forecast
from functions import get_weather_data, generate_daily_df, generate_hourly_df

open_mateo_response = get_weather_data(LATITUDE, LONGITUDE)

daily_weather_df = generate_daily_df(open_mateo_response)
hourly_weather_df = generate_hourly_df(open_mateo_response)
# print(hourly_weather_df)
# print(daily_weather_df)


# add hours column to df
hourly_weather_df['date'] = pd.to_datetime(hourly_weather_df['date']).dt.tz_convert('America/Los_Angeles')  # convert to PST time zone
hourly_weather_df['hour'] = hourly_weather_df['date'].dt.hour
hourly_weather_df = hourly_weather_df[hourly_weather_df['hour'] >= 6]


# discord messaging
USER_ID = os.getenv("DISCORD_USER_ID")
# BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# create weather message function
from functions import create_weather_message
weather_message = create_weather_message(USER_ID, daily_weather_df, NAME)


# run discord bot's functions
from functions import start_bot
start_bot(USER_ID, weather_message, hourly_weather_df)