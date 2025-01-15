import sys
import os

# error logging for deployment
import logging

# env
from dotenv import load_dotenv

# open weather api
import requests

# open mateo weather api
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# data plot creation and data processing
# import pandas as pd # imported earlier
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO

# discord
import discord

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('weather_app.log')
    ]
)
logger = logging.getLogger(__name__)

# load env variables
load_dotenv()


# constants
API_KEY=os.getenv("API_KEY")
CITY="Milpitas"
STATE_CODE="06"
NAME="Anton"
USER_ID = os.getenv("DISCORD_USER_ID")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

def get_geocodes(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            if not data:
                logger.error(f"No geocoding data found for {CITY}, {STATE_CODE}")
                return None, None
            # print(data[0])
            latitude = data[0]['lat']
            longitude = data[0]['lon']
            if latitude is not None and longitude is not None:  
                return latitude,longitude
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting geocodes: {str(e)}")
        return None, None

def get_weather_data(LATITUDE, LONGITUDE):
    try:
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        # Validate input parameters
        if not isinstance(LATITUDE, (int, float)) or not isinstance(LONGITUDE, (int, float)):
            raise ValueError("Latitude and longitude must be numeric values")

        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "hourly": ["temperature_2m", "precipitation"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "daylight_duration", "uv_index_max", "precipitation_hours", "precipitation_probability_max"],
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "timezone": "America/Los_Angeles",
            "forecast_days": 1
        }
        responses = openmeteo.weather_api(url, params=params)
        if not responses:
            raise ValueError("No data received from Open Mateo API")
        
        response = responses[0]
        return response
    except ValueError as e:
        logger.error(f"Validation Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_weather_data: {str(e)}")
        raise

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

# discord message creation
def create_weather_message(user_id, daily_weather_df, NAME):
    daily_high_temp = round(daily_weather_df.loc[0, "temperature_2m_max"],1)
    formatted_daily_high_temp = f"{daily_high_temp:.1f}"
    # print(formatted_daily_high_temp)

    daily_low_temp = round(daily_weather_df.loc[0, "temperature_2m_min"],1)
    formatted_daily_low_temp = f"{daily_low_temp:.1f}"
    # print(formatted_daily_low_temp)

    # useless data (nothing here)
    # daily_sunrise = daily_weather_df.loc[0,'sunrise']
    # daily_sunset = daily_weather_df.loc[0,'sunset']

    daily_UV_index = round(daily_weather_df.loc[0,'uv_index_max'],1)
    # print(daily_UV_index)

    if (daily_UV_index < 3):
        UV_index_string = f"{daily_UV_index:.1f} - Low Risk"
    elif (daily_UV_index < 6):
        UV_index_string = f"{daily_UV_index:.1f} - Medium Risk"
    elif (daily_UV_index < 8):
        UV_index_string = f"{daily_UV_index:.1f} - High Risk"
    elif (daily_UV_index < 11):
        UV_index_string = f"{daily_UV_index:.1f} - Very High Risk"
    else:
        UV_index_string = f"{daily_UV_index:.1f} - Extreme Risk"
    


    weather_message = (
        f"<@{user_id}>\n"
        f"Good morning {NAME}!\n\n"
        "Today's forecast:\n"
        f"- High: {formatted_daily_high_temp} °F\n"
        f"- Low: {formatted_daily_low_temp} °F\n"
        f"- UV Index: {UV_index_string}\n"
        "\n\n"
    )
    return weather_message

# create plots
def create_temperature_plot(hourly_weather_df):
    date = hourly_weather_df['date'].dt.date.iloc[0]

    # Define precipitation thresholds and colors
    def get_precipitation_color(precip):
        if precip == 0:
            return '#1f77b4'  # blue
        elif precip <= 2.5:
            return '#2ecc71'  # green
        elif precip <= 7.6:
            return '#f1c40f'  # yellow
        elif precip <= 50:
            return '#e74c3c'  # red
        else:
            return '#c0392b'  # dark red
    
    # Apply color mapping to precipitation
    hourly_weather_df['point_color'] = hourly_weather_df['precipitation'].apply(get_precipitation_color)

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8,6))
    sns.lineplot(
        x='hour',
        y='temperature_2m',
        data=hourly_weather_df,
        color='gray',
        alpha=0.5
    )
    sns.scatterplot(
        x='hour',
        y='temperature_2m',
        data=hourly_weather_df,
        color=hourly_weather_df['point_color'],
        s=100,
        ax=ax
    )

    # Add color legend for precipitation
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#1f77b4', label='No precipitation', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ecc71', label='Light (≤2.5mm)', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#f1c40f', label='Medium (≤7.6mm)', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#e74c3c', label='Heavy (≤50mm)', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#c0392b', label='Extreme (>50mm)', markersize=10),
    ]
    ax.legend(handles=legend_elements, title='Precipitation', loc='upper right')


    ax.set_title(f"Temperature for {date}", fontsize=16, pad=20, fontweight='bold')
    ax.set_xlabel("Hour of Day", fontsize=13, fontweight='bold', labelpad=15)
    ax.set_ylabel("Temperature (°F)", fontsize=13, fontweight='bold', labelpad=10)

    ax.set_xticks(range(6, 25, 2))
    # Set y-axis limits
    ax.set_ylim(25, 110)
    ax.tick_params(axis='both', labelsize=12)
    plt.tight_layout()

    return fig

def save_plot_to_buffer(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0) # move to the start of buffer
    plt.close(fig) # close the figure to free memory
    return buffer

async def start_discord_weather_bot(user_id, weather_message, hourly_weather_df):
    try:
        # Set up Discord client
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)
        
        # Create plot
        fig = create_temperature_plot(hourly_weather_df)
        buffer = save_plot_to_buffer(fig)
        
        @client.event
        async def on_ready():
            try:
                logger.info(f'Logged in as {client.user}')
                user = await client.fetch_user(int(user_id))
                await user.send(weather_message, file=discord.File(buffer, 'plot.png'))
                logger.info("Weather message and plot sent successfully")
                await client.close()
            except discord.errors.NotFound:
                logger.error(f"User with ID {user_id} not found")
                await client.close()
            except discord.errors.Forbidden:
                logger.error("Bot doesn't have permission to send messages to this user")
                await client.close()
            except Exception as e:
                logger.error(f"Error in on_ready: {str(e)}")
                await client.close()
        
        # Get bot token and validate
        bot_token = os.getenv("DISCORD_BOT_TOKEN")
        if not bot_token:
            raise ValueError("Discord bot token not found in environment variables")
            
        # Run the client
        await client.start(bot_token)        
    except discord.errors.LoginFailure:
        logger.error("Failed to login to Discord - invalid token")
        raise
    except Exception as e:
        logger.error(f"Error in send_weather_discord_message: {str(e)}")
        raise
    finally:
        # Ensure the buffer is closed
        if 'buffer' in locals():
            buffer.close()

def main():
    try:
        logger.info("Starting weather update application...")

        # city to geocode first (lat and lon)
        URL=f"http://api.openweathermap.org/geo/1.0/direct?q={CITY},{STATE_CODE}&limit=2&appid={API_KEY}"

        LATITUDE,LONGITUDE = get_geocodes(URL)

        if LATITUDE is None or LONGITUDE is None:
            sys.exit("Error getting latitude and longitude!")

        open_mateo_response = get_weather_data(LATITUDE, LONGITUDE)
        
        daily_weather_df = generate_daily_df(open_mateo_response)
        hourly_weather_df = generate_hourly_df(open_mateo_response)
        # print(hourly_weather_df)
        # print(daily_weather_df)

        hourly_weather_df['date'] = pd.to_datetime(hourly_weather_df['date']).dt.tz_convert('America/Los_Angeles')  # convert to PST time zone
        hourly_weather_df['hour'] = hourly_weather_df['date'].dt.hour       # separate hourly column for plot creation purposes
        hourly_weather_df = hourly_weather_df[hourly_weather_df['hour'] >= 6]   # Only hourly weather from 6am and after

        weather_message = create_weather_message(USER_ID, daily_weather_df, NAME)

        import asyncio
        asyncio.run(start_discord_weather_bot(USER_ID, weather_message, hourly_weather_df))
    except Exception as e:
        logger.error(f"Main process failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
