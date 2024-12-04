import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from calendar import monthrange
import re
import pygame


driver = webdriver.Chrome()
wait = WebDriverWait(driver, 30)

def play_music():
    pygame.mixer.init()

    # Load and play an MP3 file
    pygame.mixer.music.load('music.mp3')
    pygame.mixer.music.play()

    # Wait for the music to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def custom_split(x):
    x = x.replace('CET','')
    x = x.replace('CEST','')
    date_time = re.sub(r'\s*([A-Za-z]+)\s*$', '', x.split('-')[0].strip())
    date = date_time.split(' ')[0]
    time = date_time.split(' ')[1]
    time_obj = datetime.strptime(time, "%H:%M")
    formatted_time = time_obj.strftime("%I:%M:%S %p")
    return date+' '+formatted_time

def getData():
    try:
        dates = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.usytpelementsg-1xekhk3")))
        prices = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.usytpelementsg-1wowaen")))
        return dates,prices
    except Exception as e:
        return None,None

def writeData(writer):
    try:
        dates,prices = getData()
        if(len(dates)!=24):
            play_music()
            print(dates[0].text,len(dates))
        for i in range(len(dates)):
            writer.writerow({'Date': custom_split(dates[i].text), 'Price': prices[i].text})
    except Exception as e:
        print(f"Error extracting data: {e}")

def changeDate(new_date):
    retries = 3
    for attempt in range(retries):
        try:
            input_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.uuelements-1vd42w9")))
            input_field.clear()
            for char in new_date:
                input_field.send_keys(char)
                time.sleep(0.01) 

            # time.sleep(2)
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} to change date failed: {e}")
            if attempt == retries - 1:
                raise

url = "https://newtransparency.entsoe.eu/market/energyPrices?appState=%7B%22sa%22%3A%5B%22BZN%7C10YLT-1001A0008Q%22%5D%2C%22st%22%3A%22BZN%22%2C%22mm%22%3Atrue%2C%22ma%22%3Afalse%2C%22sp%22%3A%22HALF%22%2C%22dt%22%3A%22TABLE%22%2C%22df%22%3A%222015-01-01%22%2C%22tz%22%3A%22CET%22%7D"
driver.get(url)
with open('energy_prices LT.csv', 'w', newline='') as csvfile:
    fieldnames = ['Date', 'Price']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    try:
        for year in range(2015, datetime.today().date().year + 1):
            for month in range(1, 13):
                for day in range(1, monthrange(year, month)[1] + 1):
                    date_str = f"{day:02}/{month:02}/{year}"
                    changeDate(date_str)
                    writeData(writer)
            print(f"{year}/{month} completed")  
                
    except Exception as e:
        print(f"Failed to locate or interact with the date input field: {e}")

time.sleep(2)
driver.quit()
