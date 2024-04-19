from datetime import datetime, timedelta
import config
import random
import requests
import json

# Get air quality data for the last 30 days for an African country
def get_African_history(country):
    #gET current date
    #create a loop that goes back one day 30 times
    #put aqi values into a list. 
    #Put list into a dictionary with key as country

    country_trend_data = {}

    current_datetime = datetime.now()
    iso_current_datetime = current_datetime.isoformat()

    for i in range(30):
        print(i, ". ", iso_current_datetime)
        current_datetime = current_datetime - timedelta(days = 1)
        iso_current_datetime = current_datetime.isoformat()


    location = get_location_coordinates(location)
    if not location:
        print("Location parameter is missing or invalid")
        
    print("location", location)
    current_conditions_data = current_conditions(
        client,
        location,
        include_local_AQI=False,
        include_dominent_pollutant_conc=True,
        include_all_pollutants=True
    )   

def new_get_location_coordinates(country):
    url = config.geolocator_url
    geolocator_query = f"q={country}"
    api_key = config.geolocator_api_key

    coordinates_url = url+geolocator_query + api_key
    
    try:
        response = requests.get(coordinates_url)
        if(response.status_code == 200):
            result = response.json()

            country_coordinates = result["results"][0]["geometry"]["location"]
            latitude = country_coordinates["lat"]
            longitude = country_coordinates["lng"]

            # result = json.loads(result)
            # print(country_coordinates)
            return {"longitude":longitude,"latitude":latitude}
        else:
            print("Exception occurred here")
            return None
    except Exception as e:
        print("Exception occurred ", e)
        return None



country = random.choice(config.african_countries)
print(country)
# get_African_history(country)
# Use the get_request function to fetch location coordinates
location_data = new_get_location_coordinates(country)
if location_data:
    print("Location Data:", location_data)
else:
    print("Failed to fetch location data")


