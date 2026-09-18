# Weather App

A desktop weather application built with Python, Tkinter, and the Open-Meteo API.

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
* Input validation
* API error handling
* Weather data retrieved from an external API

## Tech Stack

| Technology     | Purpose                   |
| -------------- | ------------------------- |
| Python         | Application logic         |
| Tkinter        | Graphical user interface  |
| Requests       | HTTP requests to the APIs |
| Open-Meteo API | Weather data              |

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

Python 3.x

Tkinter

requests

Install requests:

pip install requests

### Run the application

Clone the repository:

git clone https://github.com/itstxti/python-mini-projects.git

Navigate to the project:

cd python-mini-projects/weather-app

Run the application:

python weather_app.py
```

The application will open a desktop window where you can search for a city.

## How It Works

When a city is entered, the application first uses the Open-Meteo Geocoding API to find its coordinates.

```text
Madrid
   ↓
Geocoding API
   ↓
Latitude + Longitude
   ↓
Weather API
   ↓
Current Weather + 7-Day Forecast
```

The returned JSON data is then processed by the application and displayed through the Tkinter interface.

Weather codes returned by the API are converted into readable conditions and corresponding icons.

For example:

```text
0  → Clear sky → ☀️
2  → Partly cloudy → ⛅
61 → Slight rain → 🌧️
95 → Thunderstorm → ⛈️
```

## Error Handling

The application handles common problems directly within the interface, including:

* Empty city searches
* Cities that cannot be found
* Connection errors
* Unexpected API responses

## Screenshot

<p align="center">
   <img width="48%" alt="image" src="https://github.com/user-attachments/assets/6d94ba6c-49ab-4dbd-999a-c3dd948e8f87" />
   <img width="48%" alt="image" src="https://github.com/user-attachments/assets/42e06806-2e31-49b3-aef7-3986061faeac" />
</p>


