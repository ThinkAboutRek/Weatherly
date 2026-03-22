import csv
import os

import requests
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Search

OPEN_METEO_BASE_URL = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1")
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def index(request):
    return render(request, "index.html")


# ---------------------------------------------------------------------------
# Weather API endpoints
# ---------------------------------------------------------------------------

@api_view(["GET"])
def weather_by_city(request):
    city_input = request.query_params.get("city", "").strip()
    if not city_input:
        return Response(
            {"error": "Please provide a city name."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    geo_resp = requests.get(GEOCODING_URL, params={"name": city_input})
    if geo_resp.status_code != 200 or not geo_resp.json().get("results"):
        return Response(
            {"error": "City not found. Please check the spelling and try again."},
            status=status.HTTP_404_NOT_FOUND,
        )

    place = geo_resp.json()["results"][0]
    city = place["name"]
    lat, lon = place["latitude"], place["longitude"]

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
        return Response(
            {"error": "Unable to fetch weather data. Please try again later."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    data = forecast_resp.json()
    user = request.user if request.user.is_authenticated else None
    Search.objects.create(city=city, user=user)

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
        return Response(
            {"error": "Latitude and longitude required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

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
        return Response(
            {"error": "Unable to fetch weather data. Please try again later."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    data = forecast_resp.json()

    try:
        rev = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "weatherly-app"},
        )
        rev.raise_for_status()
        addr = rev.json().get("address", {})
        city = (
            addr.get("city")
            or addr.get("town")
            or addr.get("village")
            or addr.get("municipality")
            or addr.get("county")
            or addr.get("state")
            or rev.json().get("display_name")
        )
    except Exception:
        city = None

    if not city:
        city = "Current Location"

    user = request.user if request.user.is_authenticated else None
    Search.objects.create(city=city, user=user)

    return Response({
        "city": city,
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "current": data.get("current_weather", {}),
        "daily": data.get("daily", {}),
    })


# ---------------------------------------------------------------------------
# Recent searches (SPA widget — session or anonymous)
# ---------------------------------------------------------------------------

@api_view(["GET"])
def recent_searches(request):
    if request.user.is_authenticated:
        qs = Search.objects.filter(user=request.user)[:5]
    else:
        qs = Search.objects.filter(user__isnull=True)[:5]
    return Response([
        {"city": s.city, "searched_at": s.searched_at.isoformat()}
        for s in qs
    ])


# ---------------------------------------------------------------------------
# Paginated JSON history (token-authenticated API)
# ---------------------------------------------------------------------------

@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def paginated_history(request):
    city_filter = request.query_params.get("city", "").strip()
    qs = Search.objects.filter(user=request.user)
    if city_filter:
        qs = qs.filter(city__icontains=city_filter)

    page_size = 10
    paginator = Paginator(qs, page_size)
    page_number = request.query_params.get("page", 1)
    page = paginator.get_page(page_number)

    return Response({
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "page": page.number,
        "results": [
            {"city": s.city, "searched_at": s.searched_at.isoformat()}
            for s in page.object_list
        ],
    })


# ---------------------------------------------------------------------------
# CSV export (session-authenticated HTML view)
# ---------------------------------------------------------------------------

@login_required
def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="search_history.csv"'

    writer = csv.writer(response)
    writer.writerow(["City", "Searched At"])

    qs = Search.objects.filter(user=request.user)
    city_filter = request.GET.get("city", "").strip()
    if city_filter:
        qs = qs.filter(city__icontains=city_filter)

    for s in qs:
        writer.writerow([s.city, s.searched_at.strftime("%Y-%m-%d %H:%M:%S")])

    return response


# ---------------------------------------------------------------------------
# Server-rendered search history page
# ---------------------------------------------------------------------------

@login_required
def search_history(request):
    city_filter = request.GET.get("city", "").strip()
    qs = Search.objects.filter(user=request.user)
    if city_filter:
        qs = qs.filter(city__icontains=city_filter)

    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page", 1)
    page = paginator.get_page(page_number)

    return render(request, "history.html", {
        "page": page,
        "city_filter": city_filter,
        "total": paginator.count,
    })
