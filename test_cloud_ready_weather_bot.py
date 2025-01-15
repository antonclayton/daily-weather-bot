import asyncio
import logging
from cloud_ready_weather_bot import main  # assuming your main function is in app.py

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Run the test
if __name__ == "__main__":
    try:
        main()
        print("Test completed successfully!")
    except Exception as e:
        print(f"Test failed: {str(e)}")