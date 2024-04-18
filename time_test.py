from datetime import datetime, timedelta
import config
import random
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

    


country = random.choice(config.african_countries)
# print(country)
get_African_history(country)