This project scrapes the website Flight Aware for flight information and from each arrival, gets the tracklog information.

The inspiration was the need to create the database for a local project for Campolide neighborhood in Lisbon, Portugal, where the aircrafts fly above before landing. Because of noise pollution, some projects study these events to help and propose improvements for quality of living in Lisbon.

This scraper can be done in any airport, as long as it uses the website’s acronym for that specific airport.

Challenges found on this project:
1. The website information is not classified in the html code, so the date is not easily scrapable. BeautifulSoup library is handy when a website uses CSS classes to identify span or div tags, but this is not the case.

- The solution: since the information is presented in a table format, each row is considered a record and from there, BeautifulSoup treats each line as a list and each cell as an item in that list. So, using this module is possible to identify repetitive patterns on the table.

2. The table where all the information is presented only shows the day of the week and the time of arrival for the flights list and the tracklog page for each flight. The date can be obtained from the url of the flight, but with overnight flights the date on the URL is the date of departure, so some calculation has to be done to get a cleaner database, which is based on time of arrival.

- The solution: a tester runs to check if the day of the week of arrival is the same as the departure, if true, nothing to set up, if false, means that it is a overnight flight, and what needs to be done is transform the date from the URL into a datetime format and do some calculations on the date, adding a day to the date and returning the string. A string format for the date was chosen for ease of visualization and to refer as a foreign key if used on a relational database.

Two CSV files are created from the scraping. One with the flight number, aircraft, city of origin, arrival time and an identification to match the other CSV file, with the flight number and the date.

The second CSV brings the tracklog for the flight, with the flight number and date, the same as the other CSV, the time of the specific event, latitude, longitude, speed in mph, and altitude.

With the tracklog information it is possible to trace lines of geographical visualization of the flight.

With the dataframes from the CSVs, two bigger CSVs are fed with information from previous scraping.

A txt file is created in the end to tell the scraper to stop when a flight that is already on the database is found, meaning it has reached the last flight that needed to be scraped from the website.

Modules used on this project:
- BeautifulSoup, to read the HTML from the websites
- Requests, to work with URLs and redirects
- Regex, to read pattern data from the HTML code
- Datetime, to work with dates and times
- Pandas, for Data Frames handling
- Numpy, to deal with missing data from the website
