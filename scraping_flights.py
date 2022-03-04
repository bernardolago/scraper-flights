import requests
from bs4 import BeautifulSoup
import re
from re import search
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta


# Variables to start the scraper. airport variable can be set from the acronym fom the Flight Aware website
# Examples: London Heathrow: EGLL, Berlin Brandenburg: EDDB, Madrid Barajas: LEMD
t = ''
airport = 'LPPT'
full_list = []
info_flight = []
# headers provide a "disguise" so the site server reconizes the scraper as a user, not a machine
headers = {'user-agent': 'Mozilla/5.0'}

# pages tells the range of pages that the scraper should work. The more it has, the longer it takes to srape data
pages = 1

for i in range(pages):
    # Looking for the data from the airport page, goes to each row of the table with the data
    arrival_list = BeautifulSoup(requests.get(
        'https://uk.flightaware.com/live/airport/{}/arrivals?;offset={};order=actualarrivaltime;sort=DESC'.format(airport, i*20), headers=headers).text, 'html.parser')
    arrival_list = arrival_list.find_all(
        'table', {'class': 'prettyTable fullWidth'})[0]
    arrival_list = arrival_list.find_all('tr')

    # The first two lines are always headers, so they are ignored with the [2:]
    for i in arrival_list[2:]:
        flight_num = i.contents[0].text[1:]
        url_flight = 'https://uk.flightaware.com' + i.contents[0].a['href']
        # using Requests module to get the redirected url from the flight
        url_tracklog = str(requests.get(url_flight, headers=headers).url)
        url_tracklog = url_tracklog + '/tracklog'
        # list_flight creates a list with the HTML code for the table and the data that we want to colect
        list_flight = []
        list_flight = BeautifulSoup(requests.get(
            url_tracklog, headers=headers).text, 'html.parser')
        list_flight = list_flight.find_all(
            'table', {'class': 'prettyTable fullWidth'})[0]
        list_flight = list_flight.find_all(
            'tr', {'class': re.compile("smallrow[12]")})

        url_flight = requests.get(url_tracklog, allow_redirects=True)
        # from the URL, we can get the date for the flight
        pos = re.search("history/", url_flight.url).end()
        day = url_flight.url[pos:pos+8]

        # a simple checker to see if the flight was a overnight flight, one of the challenges to fix date information
        if list_flight[3].contents[1].contents[0].text[:3] != list_flight[-1].contents[1].contents[0].text[:3]:
            overnight = True
        else:
            overnight = False
        for j in list_flight:
            if not 'flight' in j['class'][-1]:
                # When it is a overnight flight, there is a one day addition to the date collected on the URL, since the URL reflects the date of departure, and we need the date of arrival. If not overnight, get the 8 caractersafter /history/ on the URL, with the variable pos
                if overnight == True:
                    day = datetime.strftime(datetime.strptime(
                        url_flight.url[pos:pos+8], "%Y%m%d") + timedelta(days=1), '%Y%m%d')
                else:
                    day = url_flight.url[pos:pos+8]

                # flight_date will be a identifier of the flight to relate the two dataframes created on this projec. It is created with an identifier with the flight number and the day of arrival
                flight_date = flight_num + '_' + day
                # this next if statement fixes the date on the URL, getting information from the date and the date that is shown on the table that is being scraped
                if datetime.strptime(datetime.strftime(datetime.strptime(day, "%Y%m%d") + timedelta(days=-1), '%Y%m%d'), "%Y%m%d").strftime('%A')[:3] == j.contents[1].contents[0].text[:3]:
                    day_adjustment = datetime.strftime(datetime.strptime(
                        day, "%Y%m%d") + timedelta(days=-1), '%Y%m%d')
                    event = day_adjustment + \
                        j.contents[1].contents[0].text[3:12]
                else:
                    event = day + j.contents[1].contents[0].text[3:12]
                # latitude longitude mph and altitude are straight forward information from the table
                latitude = j.contents[3].contents[0].text
                longitude = j.contents[5].contents[0].text
                mph = j.contents[13].text
                altitude = j.contents[15].contents[0].text
                # last_flight.txt tells the scraper when to spot. A simple text file with the most recent flight scraped
                with open('last_flight.txt') as f:
                    t = f.read()
                if t == flight_date:
                    break
                # creating a list with all the data collected, to be exported into a CSV file next
                info_flight.append(
                    (flight_date, event, latitude, longitude, mph, altitude))

        # Some flights don't have all the information, like aircraft model, so aircraft and arigin are set to deal with scraping errors
        if len(i.contents[1].text) > 0:
            aircraft = i.contents[1].text
        else:
            aircraft = np.nan
        if i.contents[2].find('a') is not None:
            origin = i.contents[2].find('a').text
        else:
            origin = np.nan
        arrival = day + i.contents[4].text[3:9]
        id_flight = flight_date
        # Same tester to check if the scraper has reached the last flight scraped previously
        with open('last_flight.txt') as f:
            t = f.read()
        if t == flight_date:
            break
        # creating a list with all the data collected, to be exported into a CSV file next
        full_list.append((flight_num, aircraft, origin, arrival, id_flight))

# Now a new flight number and date is written on the text file for the next scraping
if info_flight[0][0] != None:
    with open('last_flight.txt', 'w') as f:
        f.write(info_flight[0][0])


# The rest of the code transforms the lists into Pandas dataframes and exports them to CSV files. Two CSVs with the latest scraped, identified with the date, and two larger CSVs with all the scraping done in the past
df_flights = pd.DataFrame(
    full_list, columns=['flight', 'aircraft', 'origin', 'arrival', 'id_flight'])
df_flights.to_csv('flights{}.csv'.format(
    datetime.strftime(datetime.today(), '%Y%m%d')))
full_flights_df = pd.read_csv('flights.csv')
pd.concat([df_flights, full_flights_df],
          ignore_index=True).to_csv('flights.csv')

df_info_flights = pd.DataFrame(info_flight, columns=[
                               'flight_date', 'event', 'latitude', 'longitude', 'mph', 'altitude'])
df_info_flights.to_csv('info_flights{}.csv'.format(
    datetime.strftime(datetime.today(), '%Y%m%d')))
full_info_flights_df = pd.read_csv('info_flights.csv')
pd.concat([df_info_flights, full_info_flights_df],
          ignore_index=True).to_csv('info_flights.csv')
