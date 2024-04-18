import requests
import io
import smtplib
import os
from dotenv import load_dotenv
# importing geopy library and Nominatim class
from geopy.geocoders import Nominatim

from datetime import datetime, timedelta
import random

# Config file with some unwieldy variables defined
import config 

load_dotenv() 



    


def current_conditions(
    client,
    location,
    include_local_AQI=False,
    include_health_suggestion=False,
    include_all_pollutants=True,
    include_additional_pollutant_info=False,
    include_dominent_pollutant_conc=True,
    language=None,
):
    """
    See documentation for this API here
    https://developers.google.com/maps/documentation/air-quality/reference/rest/v1/currentConditions/lookup
    """
    params = {}

    if isinstance(location, dict):
        params["location"] = location
    else:
        raise ValueError(
            "Location argument must be a dictionary containing latitude and longitude"
        )

    extra_computations = []
    if include_local_AQI:
        extra_computations.append("LOCAL_AQI")

    if include_health_suggestion:
        extra_computations.append("HEALTH_RECOMMENDATIONS")

    if include_additional_pollutant_info:
        extra_computations.append("POLLUTANT_ADDITIONAL_INFO")

    if include_all_pollutants:
        extra_computations.append("POLLUTANT_CONCENTRATION")

    if include_dominent_pollutant_conc:
        extra_computations.append("DOMINANT_POLLUTANT_CONCENTRATION")

    if language:
        params["language"] = language

    params["extraComputations"] = extra_computations

    return client.request_post("/v1/currentConditions:lookup", params)




class Client(object):
    DEFAULT_BASE_URL = "https://airquality.googleapis.com"

    def __init__(self, key):
        self.session = requests.Session()
        self.key = key

    def request_post(self, url, params):
        request_url = self.compose_url(url)
        request_header = self.compose_header()
        request_body = params

        response = self.session.post(
            request_url,
            headers=request_header,
            json=request_body,
        )

        return self.get_body(response)

    def compose_url(self, path):
        return self.DEFAULT_BASE_URL + path + "?" + "key=" + self.key

    @staticmethod
    def get_body(response):
        body = response.json()

        if "error" in body:
            return body["error"]

        return body

    @staticmethod
    def compose_header():
        return {
            "Content-Type": "application/json",
        }
    

# set up client
client = Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

def get_location_coordinates(location):
    # Initialize Nominatim geocoder
    geolocator = Nominatim(user_agent="my_geocoder")

    # Get location information
    location_info = geolocator.geocode(location)

    # Extract latitude and longitude
    latitude = location_info.latitude
    longitude = location_info.longitude

    return {"longitude":longitude,"latitude":latitude}


def fetch_air_quality(location):
    location = get_location_coordinates(location)
    current_conditions_data = current_conditions(
        client,
        location,
        include_health_suggestion=True,
        include_additional_pollutant_info=True
)   
    return current_conditions_data['indexes'][0]['aqiDisplay']


def fetch_air_quality_queries(location):
    location = get_location_coordinates(location)
    if not location:
        print("Location parameter is missing or invalid")
        
    print("location", location)
    current_conditions_data = current_conditions(
        client,
        location,
        include_health_suggestion=True,
        include_local_AQI=False,
        include_additional_pollutant_info=False,
        include_dominent_pollutant_conc=True,
        include_all_pollutants=True
)   
    return current_conditions_data

def hourly_conditions(client,
                      location,
                      datetime):
    """Get condition data for a particular hour"""
    
    params = {}

    params["dateTime"] = datetime


    if isinstance(location, dict):
        params["location"] = location
    else:
        raise ValueError(
            "Location argument must be a dictionary containing latitude and longitude"
        )
    
    return client.request_post("/v1/history:lookup", params)


# Get air quality data for the last 30 days for an African country
def get_african_history():
    #gET current date
    #create a loop that goes back one day 30 times
    #put aqi values into a list. 
    #Put list into a dictionary with key as country
    country = random.choice(config.african_countries)


    current_datetime = datetime.now()
    current_datetime = current_datetime - timedelta(days = 1)
    iso_current_datetime = current_datetime.isoformat() + "Z"



    country_trend_data = {}
    country_trend_data[country] = []

    for i in range(30):
        # print(i, ". ", iso_current_datetime)
        location = get_location_coordinates(country)

        # print("LOCATION CHANGED - ", location)

        hourly_conditions_data = hourly_conditions(
            client,
            location,
            iso_current_datetime
        )   
        # country_trend_data[country] = hourly_conditions_data

        current_datetime = current_datetime - timedelta(days = 1)
        iso_current_datetime = current_datetime.isoformat() + "Z"

        country_trend_data[country].append(hourly_conditions_data["hoursInfo"][0]["indexes"][0]["aqiDisplay"])
    # country_trend_data[country] = hourly_conditions_data[country]['hoursInfo'][1]["indexes"][0]["aqiDisplay"]
    # print("Country Trend data")
    # print(country_trend_data)
    return country_trend_data


def get_common_air_pollutant():
    pollutant_list = []

    for country in config.african_countries:
        if country == "Algeria":
            continue
        location = get_location_coordinates(country)

        # print("LOCATION CHANGED - ", location)

        current_conditions_data = current_conditions(
            client,
            location,
        )   


        pollutant_list.append(current_conditions_data["indexes"][0]["dominantPollutant"])
        

        # count
    most_common_pollutant = max(set(pollutant_list), key = pollutant_list.count)
    return str(most_common_pollutant)


def get_common_air_quality():
    air_quality_list = []

    for country in config.african_countries:
        if country == "Algeria":
            continue
        location = get_location_coordinates(country)

        # print("LOCATION CHANGED - ", location)

        current_conditions_data = current_conditions(
            client,
            location,
        )   


        air_quality_list.append(current_conditions_data["indexes"][0]["category"])
        

        # count
    most_common_pollutant = max(set(air_quality_list), key = air_quality_list.count)
    return str(most_common_pollutant)













def send_emails(email, location, air_quality):
    subject = "Air Quality Threshold reached"
    smtpServer = "smtp.gmail.com"
    port = 587
    senderEmail ="referency85@gmail.com"
    senderPassword = os.getenv('EMAIL_PASSWORD')
    server = smtplib.SMTP(smtpServer, port)
    server.starttls()
    server.login(senderEmail, senderPassword)
    body = f"Alert: Air quality in {location} {air_quality} exceeds threshold for user {email}"
    message = f'Subject: {subject}\n\n{body}'
    server.sendmail(senderEmail, email, message)
    server.quit()
