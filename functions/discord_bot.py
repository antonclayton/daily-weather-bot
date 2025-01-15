# discord messaging
import discord
import os
from functions import create_temperature_plot,save_plot_to_buffer

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# globals so that they can be used in: on_ready function
USER_ID = None
weather_message = None  # Initialize to None
hourly_weather_df = None

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# function to send message
async def send_dm_to_user(user_id, weather_message, hourly_weather_df):
    fig = create_temperature_plot(hourly_weather_df)
    buffer = save_plot_to_buffer(fig)


    try:
        # Get the user by their Discord user ID
        user = await client.fetch_user(user_id)

        # Send a DM
        await user.send(weather_message, file=discord.File(buffer, 'plot.png'))
        print("Plot sent Successfully")
        print("Message sent!")
    except Exception as e:
        print(f"Failed to send message: {e}")
        await client.close()

# on_ready event handler
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    await send_dm_to_user(USER_ID, weather_message, hourly_weather_df)

    await client.close()

# authenticates bot with discord, allowing it to function
def start_bot(user_id, message, hourly_df):
    # declare variables as global to pass them to on_ready function
    global USER_ID, weather_message, hourly_weather_df

    USER_ID = user_id
    weather_message = message
    hourly_weather_df = hourly_df

    client.run(BOT_TOKEN)