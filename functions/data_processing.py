# seaborn and pandas data manipulation:
import pandas as pd


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

    daily_UV_index = daily_weather_df.loc[0,'uv_index_max']

    if (daily_UV_index < 3):
        UV_index_string = f"{daily_UV_index} - Low Risk"
    elif (daily_UV_index < 6):
        UV_index_string = f"{daily_UV_index} - Medium Risk"
    elif (daily_UV_index < 8):
        UV_index_string = f"{daily_UV_index} - High Risk"
    elif (daily_UV_index < 11):
        UV_index_string = f"{daily_UV_index} - Very High Risk"
    else:
        UV_index_string = f"{daily_UV_index} - Extreme Risk"
    

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