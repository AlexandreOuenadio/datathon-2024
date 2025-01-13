from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import datetime
import os
import time
import json
import re
import csv
from opencage.geocoder import OpenCageGeocode
import locale
import contextlib
import os
import dateparser


# Set the LC_TIME environment variable to French
os.environ['LC_TIME'] = 'fr_FR.UTF-8'

# Set the locale to French
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    print("Locale set to 'fr_FR.UTF-8'")
except locale.Error as e:
    print(f"Error setting locale: {e}")

print("Starting the scraping process...")

# Initialize the OpenCage geocoder with your API key
api_key = "YOUR-API-KEY"
geocoder = OpenCageGeocode(api_key)


# Chrome && Chrome driver installation on WSL2 : 
# https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2#step-2-install-latest-chrome-for-testing-for-linux


homedir = homedir = os.path.expanduser("~")
chrome_driver_path = f"{homedir}/chromedriver-linux64/chromedriver"
chrome_binary_path = f"{homedir}/chrome-linux64/chrome"

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
chrome_options.binary_location = chrome_binary_path



# Set up the Chrome driver using webdriver_manager
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# File directories
BASE_DIR = os.path.dirname(os.path.abspath("__file__"))

# Date range for scraping
initial_date = "2023-12-16"
end_date = "2024-03-23"
STEP_DAYS = 5

start_date = datetime.datetime.strptime(initial_date, "%Y-%m-%d")
end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

urls = []
current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")
    url = f"https://ambassadeurs.onlylyon.com/fr/agenda/past?published=1&happen_on={date_str}"
    urls.append((url, date_str))
    current_date += datetime.timedelta(days=STEP_DAYS)


def find_events(html_content, events_list):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Trouver tous les éléments de carte d'événement
    event_cards = soup.find_all('a', attrs={"data-tag-id": "agenda-publishing-occurrence-card"})
    
    def clean_date(date_str):
        # Supprimer tout ce qui se trouve après le caractère \n
        cleaned_date = re.sub(r'\n.*', '', date_str)
        return cleaned_date

    def get_coordinates(address, max_retries=5, backoff_factor=0.3):
        retries = 0
        while retries < max_retries:
            try:
                result = geocoder.geocode(address)
                if result and len(result):
                    location = result[0]['geometry']
                    return location['lat'], location['lng']
                else:
                    return None, None
            except Exception as e:
                retries += 1
                time.sleep(backoff_factor * (2 ** retries))
        return None, None
    
    def clean_date_period(date_period_str):
        # Remove newline characters and time information
        cleaned_str = re.sub(r'\n\s*-.*', '', date_period_str)
        
        # Extract start and end dates
        date_period_parts = cleaned_str.split(" au ")
        start_date_str = date_period_parts[0].strip()
        end_date_str = date_period_parts[1].strip()
        
        return start_date_str, end_date_str

    def generate_dates(start_date_str, end_date_str, date_format="%a. %d %b. %Y"):
        start_date = dateparser.parse(start_date_str)
        end_date = dateparser.parse(end_date_str)
        delta = end_date - start_date
        return [(start_date + datetime.timedelta(days=i)).strftime("%d-%m-%Y") for i in range(delta.days + 1)]
    
    # Extraire les informations pour chaque événement
    for card in event_cards:
        # Nom de l'événement
        event_name = card.find('h2').text.strip()
        
        # Lieu et adresse
        location = card.find('p', class_='mb-2 d-flex align-center grey--text text--darken-1').text.strip()
        
        # Coordonnées géographiques
        latitude, longitude = get_coordinates(location)
        

        # Date
        date = card.find('div', attrs={"data-tag-id": "date-from-to"}).text.strip()
        date = clean_date(date)

        start_date_str, end_date_str = clean_date_period(date)
        dates = generate_dates(start_date_str, end_date_str)

        for date in dates:
            event = {
                "name": event_name,
                "location": location,
                "longitude": longitude,
                "latitude": latitude,
                "date": date
            }
            events_list.append(event)
        
        

def convert_to_csv(events, path):
    
    # Écrire les données dans un fichier CSV
    with open(path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        # Écrire l'en-tête du CSV
        writer.writerow(["name", "address", "longitude", "latitude","date"])
        
        # Écrire les lignes de données
        for event in events:
            writer.writerow([event["name"], event["location"], event["longitude"], event["latitude"], event["date"]])



# Scrape the data
events_list = []
for url, date in urls:
    driver.get(url)
    time.sleep(10)  # Wait for the page to load

    html_content = driver.page_source

    find_events(html_content, events_list)



convert_to_csv(events_list, os.path.join(BASE_DIR, f"events.csv"))
# # Save the data to a JSON file
# with open(os.path.join(BASE_DIR, f"events.csv"), "w", encoding="utf-8") as file:
#     json.dump(events_list, file, ensure_ascii=False, indent=4)




driver.quit()

print("Scraping process completed successfully!")