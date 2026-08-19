"""
Weather Lookup Tool for NOVA Agent using Open-Meteo API.
Requires no API key. First geocodes the city, then fetches current weather metrics.
"""
from typing import Any, Dict
import requests

WMO_WEATHER_CODES = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌧️",
    53: "Moderate drizzle 🌧️",
    55: "Dense drizzle 🌧️",
    56: "Light freezing drizzle 🌨️",
    57: "Dense freezing drizzle 🌨️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    66: "Light freezing rain 🌨️",
    67: "Heavy freezing rain 🌨️",
    71: "Slight snowfall ❄️",
    73: "Moderate snowfall ❄️",
    75: "Heavy snowfall ❄️",
    77: "Snow grains ❄️",
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌦️",
    82: "Violent rain showers 🌧️",
    85: "Slight snow showers 🌨️",
    86: "Heavy snow showers 🌨️",
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with slight hail ⛈️",
    99: "Thunderstorm with heavy hail ⛈️",
}


def get_weather(city: str) -> Dict[str, Any]:
    """
    Look up current weather for any city worldwide using Open-Meteo.
    
    Args:
        city: Name of the city to look up (e.g. 'Mumbai', 'Tokyo', 'San Francisco').
        
    Returns:
        A dictionary containing temperature, wind speed, weather condition, location details, or error info.
    """
    if not city or not city.strip():
        return {
            "status": "error",
            "city": city,
            "error": "Please provide a valid city name.",
        }

    city_cleaned = city.strip()

    try:
        # Step 1: Geocoding lookup
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {
            "name": city_cleaned,
            "count": 1,
            "language": "en",
            "format": "json",
        }
        headers = {"User-Agent": "NOVA-Agent/1.0"}

        geo_resp = requests.get(geo_url, params=geo_params, headers=headers, timeout=10)
        
        if geo_resp.status_code != 200:
            return {
                "status": "error",
                "city": city_cleaned,
                "error": f"Geocoding service returned status code {geo_resp.status_code}.",
            }

        geo_data = geo_resp.json()
        results = geo_data.get("results")

        if not results or len(results) == 0:
            return {
                "status": "error",
                "city": city_cleaned,
                "error": f"Could not find coordinates for city '{city_cleaned}'. Please check the city spelling.",
            }

        place = results[0]
        lat = place.get("latitude")
        lon = place.get("longitude")
        resolved_name = place.get("name", city_cleaned)
        country = place.get("country", "")
        admin1 = place.get("admin1", "")

        location_parts = [p for p in [resolved_name, admin1, country] if p]
        full_location = ", ".join(location_parts)

        # Step 2: Current weather lookup
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "timezone": "auto",
        }

        weather_resp = requests.get(weather_url, params=weather_params, headers=headers, timeout=10)

        if weather_resp.status_code != 200:
            return {
                "status": "error",
                "city": city_cleaned,
                "location": full_location,
                "error": f"Weather service returned status code {weather_resp.status_code}.",
            }

        weather_data = weather_resp.json()
        current = weather_data.get("current_weather", {})

        if not current:
            return {
                "status": "error",
                "city": city_cleaned,
                "location": full_location,
                "error": "No current weather metrics returned from service.",
            }

        temp_c = current.get("temperature")
        wind_speed = current.get("windspeed")
        wind_dir = current.get("winddirection")
        weather_code = current.get("weathercode", 0)
        is_day = bool(current.get("is_day", 1))
        obs_time = current.get("time", "")

        condition = WMO_WEATHER_CODES.get(weather_code, f"Weather Code {weather_code}")
        temp_f = round(temp_c * 9 / 5 + 32, 1) if temp_c is not None else None

        return {
            "status": "success",
            "city": resolved_name,
            "location": full_location,
            "latitude": lat,
            "longitude": lon,
            "temperature_c": temp_c,
            "temperature_f": temp_f,
            "wind_speed_kmh": wind_speed,
            "wind_direction_deg": wind_dir,
            "condition": condition,
            "is_day": is_day,
            "observed_time": obs_time,
            "error": None,
        }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "city": city_cleaned,
            "error": "Weather lookup timed out. Please try again.",
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "city": city_cleaned,
            "error": "Network connection error while contacting weather service.",
        }
    except Exception as e:
        return {
            "status": "error",
            "city": city_cleaned,
            "error": f"Unexpected weather lookup error: {str(e)}",
        }
