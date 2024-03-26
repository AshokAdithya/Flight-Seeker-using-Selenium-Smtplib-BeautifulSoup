from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import requests
import sys
import smtplib
import os

password=os.environ.get("password")
sender_email=os.environ.get("sender_email")
to_email=os.environ.get("to_email")

chrome_options=webdriver.ChromeOptions()
chrome_options.add_argument('--incognito')
chrome_options.add_experimental_option("detach",True)

class BookTicket:

    def __init__(self,option):
        self.option=option
        self.url="https://www.air-port-codes.com/search/results/"

    def book_ticket(self,from_iata,to_iata):
        driver=webdriver.Chrome(options=self.option)
        driver.get("https://www.booking.com/flights/index.en.html")
        driver.maximize_window()

        time.sleep(1)

        one_way=driver.find_element(By.XPATH,'//*[@id="search_type_option_ONEWAY"]')
        one_way.click()

        from_city=driver.find_element(By.XPATH,'//*[@id="basiclayout"]/div/div/div[1]/div/div/div/div/div[2]/div[2]/div/div/div/div/div[1]/div/button[1]')
        from_city.click()

        cross_MAA=driver.find_element(By.XPATH,'//*[@id=":R49mk5b9:"]/div/div/div/div/div/div/div[1]/div/div/div/div/span/span[2]')
        cross_MAA.click()

        time.sleep(1)
        input_from_city=driver.find_element(By.XPATH,'//*[@id=":R49mk5b9:"]/div/div/div/div/div/div/div[1]/div/div/div/div/input')
        input_from_city.click()
        input_from_city.send_keys(from_iata)
        time.sleep(1)

        click_from_city=driver.find_element(By.XPATH,'//*[@id="flights-searchbox_suggestions"]/li[1]')
        click_from_city.click()

        to_city=driver.find_element(By.XPATH,'//*[@id="basiclayout"]/div/div/div[1]/div/div/div/div/div[2]/div[2]/div/div/div/div/div[1]/div/button[3]')
        to_city.click()

        time.sleep(1)
        input_to_city=driver.find_element(By.XPATH,'//*[@id=":R4pmk5b9:"]/div/div/div/div/div/div/div[1]/div/div/div/div/input')
        input_to_city.click()
        input_to_city.send_keys(to_iata)
        time.sleep(1)

        click_to_city=driver.find_element(By.XPATH,'//*[@id="flights-searchbox_suggestions"]/li[1]')
        click_to_city.click()

        search=driver.find_element(By.XPATH,'//*[@id="basiclayout"]/div/div/div[1]/div/div/div/div/div[2]/div[2]/div/div/button')
        search.click()

        time.sleep(5)

        airline_name=driver.find_elements(By.CSS_SELECTOR,'[data-testid="flight_card_carrier_0"]')
        prices = driver.find_elements(By.CSS_SELECTOR, '.Text-module__root--variant-headline_3___ajLMe.Text-module__root--color-neutral___Aqg3v.Title-module__title___ck7RN')
        depature_time=driver.find_elements(By.CSS_SELECTOR,'[data-testid="flight_card_segment_departure_time_0"]')
        arrival_time=driver.find_elements(By.CSS_SELECTOR,'[data-testid="flight_card_segment_destination_time_0"]')
        depature_date=driver.find_elements(By.CSS_SELECTOR,'[data-testid="flight_card_segment_departure_date_0"]')

        website_link=driver.current_url

        flight_data = []

        for i in range(len(depature_time)):
            flight_info = {
            "Airline": airline_name[i].text,
            "Departure_Time": depature_time[i].text,
            "Arrival_Time": arrival_time[i].text,
            "Departure_Date": depature_date[i].text,
            "Price": prices[i].text,
            }
            flight_data.append(flight_info)
            
        if flight_data==[]:
            print(f"There is an error occured while getting informations from the website")
            return None,None,None
            sys.exit()

        driver.close()

        time.sleep(2)
        date=flight_data[0]["Departure_Date"]

        return flight_data,date,website_link

    def iata_code(self,from_city_input,to_city_input):
        from_response=requests.get(self.url+from_city_input)
        to_response=requests.get(self.url+to_city_input)
        soup_from=BeautifulSoup(from_response.text,"html.parser")
        soup_to=BeautifulSoup(to_response.text,"html.parser")

        try:
            from_iata=soup_from.find_all('td')[1].text
            to_iata=soup_to.find_all('td')[1].text 

        except IndexError as i:
            print("No Airports Found")
            sys.exit()
            return None,None

        else:
            return from_iata,to_iata

    def send_mail(self,from_city,to_city,date,data,website):

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email,password)

        flight_details = ""
        for flight in data:
            flight_details += f"Airline: {flight['Airline']}\n"
            flight_details += f"Departure Time: {flight['Departure_Time']}\n"
            flight_details += f"Arrival Time: {flight['Arrival_Time']}\n"
            flight_details += f"Departure Date: {flight['Departure_Date']}\n"
            flight_details += f"Price: {flight['Price']}\n"
            flight_details += "-" * 30 + "\n"  
        
        subject=f"{from_city} to {to_city} on {date}"
        email=f"{flight_details} \n\nTo Book Tickets: {website}"
        message=f"Subject: {subject} \n\n{email}"

        try:
            server.sendmail(sender_email,to_email, message)
        
        except Exception as e:
            print(f"An error occured while sending the mail:{e}")
            sys.exit()

        finally:
            server.quit()
            return flight_details

flight=BookTicket(chrome_options)

from_city=input("Enter the Depature Airport City: ").title()
to_city=input("Enter the Arrival Airport City: ").title()

from_iata,to_iata=flight.iata_code(from_city,to_city)
tickets, date,website=flight.book_ticket(from_iata,to_iata)
details=flight.send_mail(from_city,to_city,date,tickets,website)

print(details)


