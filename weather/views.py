import os
import requests
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Search

def index(request):
    return render(request, "index.html")

OPEN_METEO_BASE_URL = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1")
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

@api_view(["GET"])
def weather_by_city(request):
    city_input = request.query_params.get("city", "").strip()
    if not city_input:
        return Response({"error": "Please provide a city name."},
                        status=status.HTTP_400_BAD_REQUEST)

    # 1) Geocode
    geo_resp = requests.get(GEOCODING_URL, params={"name": city_input})
    if geo_resp.status_code != 200 or not geo_resp.json().get("results"):
        return Response({"error": "City not found. Please check the spelling and try again."},
                        status=status.HTTP_404_NOT_FOUND)

    place = geo_resp.json()["results"][0]
    city = place["name"]            # normalized capitalization
    lat, lon = place["latitude"], place["longitude"]

    # 2) Forecast
    forecast_resp = requests.get(
        f"{OPEN_METEO_BASE_URL}/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode",
            "timezone": "auto",
            "forecast_days": 7,
        },
    )
    if forecast_resp.status_code != 200:
        return Response({"error": "Unable to fetch weather data. Please try again later."},
                        status=status.HTTP_502_BAD_GATEWAY)

    data = forecast_resp.json()

    # 3) Log only on success
    Search.objects.create(city=city)

    return Response({
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "current": data.get("current_weather", {}),
        "daily": data.get("daily", {}),
    })


@api_view(["GET"])
def weather_by_coords(request):
    lat = request.query_params.get("lat")
    lon = request.query_params.get("lon")
    if not lat or not lon:
        return Response({"error": "Latitude and longitude required."},
                        status=status.HTTP_400_BAD_REQUEST)

    # 1) Forecast
    forecast_resp = requests.get(
        f"{OPEN_METEO_BASE_URL}/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode",
            "timezone": "auto",
            "forecast_days": 7,
        },
    )
    if forecast_resp.status_code != 200:
        return Response({"error": "Unable to fetch weather data. Please try again later."},
                        status=status.HTTP_502_BAD_GATEWAY)

    data = forecast_resp.json()

    # 2) Reverse‑geocode the coords into a human‑friendly place name
    try:
        rev = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "weatherly-app"}
        )
        rev.raise_for_status()
        rev_json = rev.json()
        addr = rev_json.get("address", {})
        # pick the most specific available field
        city = (
            addr.get("city")
            or addr.get("town")
            or addr.get("village")
            or addr.get("municipality")
            or addr.get("county")
            or addr.get("state")
            or rev_json.get("display_name")
        )
    except Exception:
        city = None

    if not city:
        city = "Current Location"

    # 3) Log search
    Search.objects.create(city=city)

    return Response({
        "city": city,
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "current": data.get("current_weather", {}),
        "daily": data.get("daily", {}),
    })


@api_view(["GET"])
def recent_searches(request):
    qs = Search.objects.order_by("-searched_at")[:5]
    return Response([
        {"city": s.city, "searched_at": s.searched_at.isoformat()}
        for s in qs
    ])
