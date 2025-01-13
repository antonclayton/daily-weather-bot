import requests

def get_geocodes(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # print(data[0])
        latitude = data[0]['lat']
        longitude = data[0]['lon']
        if latitude is not None and longitude is not None:  
            return latitude,longitude
    return None, None