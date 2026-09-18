import tkinter as tk
import requests
from datetime import datetime


# -----------------------------
# Configuration
# -----------------------------

current_unit = "C"


# -----------------------------
# Weather conditions
# -----------------------------

def get_weather_condition(code):
    conditions = {
        0: ("Clear sky", "☀️"),
        1: ("Mainly clear", "🌤️"),
        2: ("Partly cloudy", "⛅"),
        3: ("Overcast", "☁️"),
        45: ("Fog", "🌫️"),
        48: ("Depositing rime fog", "🌫️"),
        51: ("Light drizzle", "🌦️"),
        53: ("Moderate drizzle", "🌦️"),
        55: ("Dense drizzle", "🌧️"),
        61: ("Slight rain", "🌧️"),
        63: ("Moderate rain", "🌧️"),
        65: ("Heavy rain", "🌧️"),
        71: ("Slight snow", "🌨️"),
        73: ("Moderate snow", "❄️"),
        75: ("Heavy snow", "❄️"),
        80: ("Slight rain showers", "🌦️"),
        81: ("Moderate rain showers", "🌧️"),
        82: ("Violent rain showers", "⛈️"),
        95: ("Thunderstorm", "⛈️"),
        96: ("Thunderstorm with hail", "⛈️"),
        99: ("Thunderstorm with heavy hail", "⛈️")
    }

    return conditions.get(
        code,
        ("Unknown conditions", "🌡️")
    )


# -----------------------------
# Temperature conversion
# -----------------------------

def convert_temperature(celsius):
    if current_unit == "F":
        return (celsius * 9 / 5) + 32

    return celsius


def format_temperature(celsius):
    temperature = convert_temperature(celsius)
    return f"{round(temperature)}°{current_unit}"


# -----------------------------
# Search weather
# -----------------------------

def get_weather():
    city = city_entry.get().strip()

    error_label.config(text="")

    if not city:
        error_label.config(
            text="Please enter a city."
        )
        return

    try:
        # -----------------------------
        # Geocoding
        # -----------------------------

        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geo_response = requests.get(
            geo_url,
            params=geo_params,
            timeout=5
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        if "results" not in geo_data:
            error_label.config(
                text=(
                    f'We couldn\'t find "{city}". '
                    "Check the spelling and try again."
                )
            )
            return

        location = geo_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]
        city_name = location["name"]
        country = location.get("country", "")

        # -----------------------------
        # Weather API
        # -----------------------------

        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,

            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "wind_speed_10m,"
                "weather_code"
            ),

            "daily": (
                "weather_code,"
                "temperature_2m_max,"
                "temperature_2m_min,"
                "sunrise,"
                "sunset"
            ),

            "forecast_days": 7,

            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",

            "timezone": "auto"
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=5
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        current = weather_data["current"]
        daily = weather_data["daily"]

        # -----------------------------
        # Current weather
        # -----------------------------

        temperature = current["temperature_2m"]
        feels_like = current["apparent_temperature"]
        humidity = current["relative_humidity_2m"]
        wind_speed = current["wind_speed_10m"]
        weather_code = current["weather_code"]

        condition, icon = get_weather_condition(
            weather_code
        )

        location_label.config(
            text=f"{city_name}, {country}"
        )

        icon_label.config(
            text=icon
        )

        temperature_label.config(
            text=format_temperature(temperature)
        )

        condition_label.config(
            text=condition
        )

        feels_like_label.config(
            text=f"Feels like {format_temperature(feels_like)}"
        )

        humidity_label.config(
            text=f"Humidity\n{humidity}%"
        )

        wind_label.config(
            text=f"Wind\n{wind_speed} km/h"
        )

        # -----------------------------
        # Sunrise / Sunset
        # -----------------------------

        sunrise = format_time(
            daily["sunrise"][0]
        )

        sunset = format_time(
            daily["sunset"][0]
        )

        sunrise_label.config(
            text=f"Sunrise\n{sunrise}"
        )

        sunset_label.config(
            text=f"Sunset\n{sunset}"
        )

        # -----------------------------
        # 7-day forecast
        # -----------------------------

        update_forecast(daily)

    except requests.RequestException:
        error_label.config(
            text=(
                "Unable to retrieve weather data. "
                "Please check your internet connection and try again."
            )
        )

    except (KeyError, IndexError):
        error_label.config(
            text=(
                "Something went wrong while processing "
                "the weather data. Please try again."
            )
        )


# -----------------------------
# Format date
# -----------------------------

def format_day(date_string):
    date = datetime.strptime(
        date_string,
        "%Y-%m-%d"
    )

    return date.strftime("%a")


def format_time(time_string):
    date = datetime.fromisoformat(
        time_string
    )

    return date.strftime("%H:%M")


# -----------------------------
# Update forecast
# -----------------------------

def update_forecast(daily):
    for widget in forecast_frame.winfo_children():
        widget.destroy()

    dates = daily["time"]
    weather_codes = daily["weather_code"]
    max_temperatures = daily["temperature_2m_max"]
    min_temperatures = daily["temperature_2m_min"]

    # Make all 7 columns share the available width equally
    for column in range(7):
        forecast_frame.grid_columnconfigure(
            column,
            weight=1
        )

    for index in range(7):
        day_frame = tk.Frame(
            forecast_frame,
            bg="white",
            padx=8,
            pady=8
        )

        day_frame.grid(
            row=0,
            column=index,
            padx=2,
            sticky="nsew"
        )

        day_label = tk.Label(
            day_frame,
            text=format_day(dates[index]),
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#374151"
        )

        day_label.pack()

        _, icon = get_weather_condition(
            weather_codes[index]
        )

        icon_label_forecast = tk.Label(
            day_frame,
            text=icon,
            font=("Arial", 22),
            bg="white"
        )

        icon_label_forecast.pack(
            pady=4
        )

        max_label = tk.Label(
            day_frame,
            text=format_temperature(
                max_temperatures[index]
            ),
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#111827"
        )

        max_label.pack()

        min_label = tk.Label(
            day_frame,
            text=format_temperature(
                min_temperatures[index]
            ),
            font=("Arial", 9),
            bg="white",
            fg="#9ca3af"
        )

        min_label.pack()


# -----------------------------
# Change temperature unit
# -----------------------------

def change_unit(unit):
    global current_unit

    current_unit = unit

    get_weather()


# -----------------------------
# Enter key
# -----------------------------

def search_with_enter(event):
    get_weather()


# -----------------------------
# Window
# -----------------------------

root = tk.Tk()

root.title("Weather App")
root.geometry("850x760")

root.resizable(False, False)

root.configure(
    bg="#f5f7fa"
)


# -----------------------------
# Header
# -----------------------------

title_label = tk.Label(
    root,
    text="Weather App",
    font=("Arial", 26, "bold"),
    bg="#f5f7fa",
    fg="#1f2937"
)

title_label.pack(
    pady=(25, 5)
)


subtitle_label = tk.Label(
    root,
    text="Check the current weather anywhere",
    font=("Arial", 11),
    bg="#f5f7fa",
    fg="#6b7280"
)

subtitle_label.pack(
    pady=(0, 15)
)


# -----------------------------
# Search
# -----------------------------

search_frame = tk.Frame(
    root,
    bg="#f5f7fa"
)

search_frame.pack(
    pady=8
)


city_entry = tk.Entry(
    search_frame,
    font=("Arial", 14),
    width=24,
    justify="center",
    relief="solid",
    bd=1
)

city_entry.pack(
    side="left",
    padx=(0, 8)
)

city_entry.bind(
    "<Return>",
    search_with_enter
)


search_button = tk.Button(
    search_frame,
    text="Search",
    font=("Arial", 10, "bold"),
    command=get_weather,
    padx=12,
    cursor="hand2"
)

search_button.pack(
    side="left"
)


# -----------------------------
# Unit selector
# -----------------------------

unit_frame = tk.Frame(
    search_frame,
    bg="#f5f7fa"
)

unit_frame.pack(
    side="left",
    padx=(15, 0)
)


celsius_button = tk.Button(
    unit_frame,
    text="°C",
    font=("Arial", 10, "bold"),
    command=lambda: change_unit("C"),
    padx=7,
    cursor="hand2"
)

celsius_button.pack(
    side="left"
)


fahrenheit_button = tk.Button(
    unit_frame,
    text="°F",
    font=("Arial", 10, "bold"),
    command=lambda: change_unit("F"),
    padx=7,
    cursor="hand2"
)

fahrenheit_button.pack(
    side="left"
)


# -----------------------------
# Error message
# -----------------------------

error_label = tk.Label(
    root,
    text="",
    font=("Arial", 10),
    bg="#f5f7fa",
    fg="#dc2626"
)

error_label.pack(
    pady=(5, 0)
)


# -----------------------------
# Current weather card
# -----------------------------

weather_frame = tk.Frame(
    root,
    bg="white",
    padx=30,
    pady=15,
    relief="solid",
    bd=1
)

weather_frame.pack(
    padx=35,
    pady=15,
    fill="x"
)


location_label = tk.Label(
    weather_frame,
    text="Search for a city",
    font=("Arial", 18, "bold"),
    bg="white",
    fg="#1f2937"
)

location_label.pack(
    pady=(0, 5)
)


icon_label = tk.Label(
    weather_frame,
    text="🌍",
    font=("Arial", 42),
    bg="white"
)

icon_label.pack()


temperature_label = tk.Label(
    weather_frame,
    text="--°C",
    font=("Arial", 38, "bold"),
    bg="white",
    fg="#111827"
)

temperature_label.pack()


condition_label = tk.Label(
    weather_frame,
    text="",
    font=("Arial", 15),
    bg="white",
    fg="#374151"
)

condition_label.pack(
    pady=(2, 0)
)


feels_like_label = tk.Label(
    weather_frame,
    text="",
    font=("Arial", 10),
    bg="white",
    fg="#6b7280"
)

feels_like_label.pack(
    pady=(0, 12)
)


# -----------------------------
# Weather details
# -----------------------------

info_frame = tk.Frame(
    weather_frame,
    bg="white"
)

info_frame.pack(
    fill="x"
)


humidity_label = tk.Label(
    info_frame,
    text="Humidity\n--%",
    font=("Arial", 10),
    bg="white",
    fg="#374151",
    width=14
)

humidity_label.pack(
    side="left",
    expand=True
)


wind_label = tk.Label(
    info_frame,
    text="Wind\n-- km/h",
    font=("Arial", 10),
    bg="white",
    fg="#374151",
    width=14
)

wind_label.pack(
    side="left",
    expand=True
)


sunrise_label = tk.Label(
    info_frame,
    text="Sunrise\n--:--",
    font=("Arial", 10),
    bg="white",
    fg="#374151",
    width=14
)

sunrise_label.pack(
    side="left",
    expand=True
)


sunset_label = tk.Label(
    info_frame,
    text="Sunset\n--:--",
    font=("Arial", 10),
    bg="white",
    fg="#374151",
    width=14
)

sunset_label.pack(
    side="left",
    expand=True
)


# -----------------------------
# Forecast title
# -----------------------------

forecast_title = tk.Label(
    root,
    text="7-Day Forecast",
    font=("Arial", 15, "bold"),
    bg="#f5f7fa",
    fg="#1f2937"
)

forecast_title.pack(
    pady=(5, 8)
)


# -----------------------------
# Forecast
# -----------------------------

forecast_frame = tk.Frame(
    root,
    bg="white",
    padx=8,
    pady=8,
    relief="solid",
    bd=1
)

forecast_frame.pack(
    padx=35,
    fill="x"
)


# -----------------------------
# Footer
# -----------------------------

footer_label = tk.Label(
    root,
    text="Powered by Open-Meteo",
    font=("Arial", 9),
    bg="#f5f7fa",
    fg="#9ca3af"
)

footer_label.pack(
    pady=10
)


# -----------------------------
# Initial focus
# -----------------------------

city_entry.focus()


root.mainloop()