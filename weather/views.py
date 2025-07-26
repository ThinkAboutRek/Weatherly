import os
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Search

OPEN_METEO_BASE_URL = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1")
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

@api_view(["GET"])
def weather_by_city(request):
    city = request.query_params.get("city")
    if not city:
        return Response({"error": "City parameter is required."},
                        status=status.HTTP_400_BAD_REQUEST)

    Search.objects.create(city=city)

    # 1) Geocoding
    geocode_resp = requests.get(GEOCODING_URL, params={"name": city})
    if geocode_resp.status_code != 200 or not geocode_resp.json().get("results"):
        return Response({"error": "Unable to geocode the city."},
                        status=status.HTTP_502_BAD_GATEWAY)

    first = geocode_resp.json()["results"][0]
    lat, lon = first["latitude"], first["longitude"]

    # 2) Forecast
    forecast_resp = requests.get(
        f"{OPEN_METEO_BASE_URL}/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode",
            "timezone": "auto",
        },
    )
    if forecast_resp.status_code != 200:
        return Response({"error": "Unable to fetch weather data."},
                        status=status.HTTP_502_BAD_GATEWAY)

    data = forecast_resp.json()
    return Response({
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "current": data.get("current_weather", {}),
        "daily": data.get("daily", {}),
    })
