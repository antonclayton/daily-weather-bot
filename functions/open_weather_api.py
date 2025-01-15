import requests

def get_geocodes(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            if not data:
                print(f"No geocoding data found for inputted area")
                return None, None
            # print(data[0])
            latitude = data[0]['lat']
            longitude = data[0]['lon']
            if latitude is not None and longitude is not None:  
                return latitude,longitude
    except requests.exceptions.RequestException as e:
        print(f"Error getting geocodes: {str(e)}")
        return None, None