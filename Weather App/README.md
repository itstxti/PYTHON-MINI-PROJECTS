# Weather App

A desktop weather application built with **Python** and **Tkinter** that retrieves real-time weather information and a 7-day forecast using the **Open-Meteo API**.

## Features

* Search weather by city
* Current temperature
* Weather condition and corresponding icon
* Feels-like temperature
* Humidity
* Wind speed
* Sunrise and sunset times
* 7-day weather forecast
* Daily maximum and minimum temperatures
* Celsius / Fahrenheit conversion

## Tech Stack


* Python     
* Tkinter      
* Requests     
* Open-Meteo API 

## APIs

The application uses two Open-Meteo endpoints:

### Geocoding API

Used to convert a city name into geographic coordinates.

```text
City → Latitude + Longitude
```

### Weather API

The coordinates are then used to retrieve current weather and a 7-day forecast.

```text
Latitude + Longitude → Weather data
```

No API key is required.

## Getting Started

### Requirements

* Python 3.x
* Tkinter
* Internet connection

### Install dependencies

Install the `requests` library:

```bash
pip install requests
```

### Run the application

```bash
python weather_app.py
```

The application will open a desktop window where you can search for a city.

## Screenshot

<p align="center">
   <img width="48%" alt="image" src="https://github.com/user-attachments/assets/6d94ba6c-49ab-4dbd-999a-c3dd948e8f87" />
   <img width="48%" alt="image" src="https://github.com/user-attachments/assets/42e06806-2e31-49b3-aef7-3986061faeac" />
</p>


