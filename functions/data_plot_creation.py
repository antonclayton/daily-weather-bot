import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO


# create plot
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
    fig, ax = plt.subplots(figsize=(10,6))
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

    ax.set_xticks(range(0, 25, 2))
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