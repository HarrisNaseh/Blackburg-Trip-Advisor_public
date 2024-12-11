import requests
from datetime import datetime
import pytz 
import icalendar
from TripAdvisor.models import Event
import os
from dotenv import find_dotenv, load_dotenv

path = find_dotenv()

load_dotenv(path)

# Function to get GobblerConnect events
def getEvent():
    ics_url = "https://gobblerconnect.vt.edu/events.ics"

    response = requests.get(ics_url)

    if response.status_code == 200:
        est = pytz.timezone('America/New_York')
        gcal = icalendar.Calendar.from_ical(response.text)
        
        events = []



        for event in gcal.walk("VEVENT"):

            begindt = datetime.fromisoformat(str(event.get("DTSTART").dt))
            
            begin = begindt.replace(tzinfo=pytz.utc).astimezone(est).strftime('%B %d %Y %I:%M%p')
            
            enddt = datetime.fromisoformat(str(event.get("DTEND").dt))
            end = enddt.replace(tzinfo=pytz.utc).astimezone(est).strftime('%B %d %Y %I:%M%p')

            name = event.get("SUMMARY")
            location = event.get("LOCATION")
            description = event.get("DESCRIPTION")
            
            try:
                category_list = [category.to_ical().decode('utf-8') for category in event.get("CATEGORIES", [])]
            except Exception as e:
                # print(f"Error processing entry: {e}")
                category_list = []
            

            events.append({
                'id': -1,
                'Name': name,
                'Start': begin,
                'End': end,
                'Location': location,
                'Description' : description,
                'Categories': category_list,
                'Gobbler': True

            })
        
        return events
    else:
        return 


# Function to get TripAdvisor restaurants
def getRestaurants():
    url = f"https://api.content.tripadvisor.com/api/v1/location/search?key={os.getenv('TRIP_ADVISOR_KEY')}&searchQuery=restaurants+in+Blacksburg,VA&category=restaurants&limit=100"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
            restaurants = []

            for item in data.get('data', []):
                restaurant_data = {
                    'Name': item.get('name'),
                    'Address': item.get('address_obj', {}).get('address_string'),
                    'LocationID': item.get('location_id')
                }
                restaurants.append(restaurant_data)

            return restaurants
        except Exception as e:
            print(f"Error while parsing the TripAdvisor data: {e}")
            return []

    return []

getEvent()