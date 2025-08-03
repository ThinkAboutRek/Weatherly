import pytest
from django.urls import reverse
import requests_mock
from weather.models import Search

@pytest.mark.django_db
def test_weather_by_city_not_found(client):
    # Geocoding returns no results
    with requests_mock.Mocker() as m:
        m.get("https://geocoding-api.open-meteo.com/v1/search", json={"results": []})
        url = reverse("weather-by-city")
        resp = client.get(url, {"city": "NonExistentPlace"})
        assert resp.status_code == 404
        assert "error" in resp.json()
        assert "not found" in resp.json()["error"].lower()

@pytest.mark.django_db
def test_recent_searches_endpoint(client):
    # create six searches so only five most recent are returned
    for i in range(6):
        Search.objects.create(city=f"City{i}")
    url = reverse("recent-searches")
    resp = client.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    # newest first: City5 should appear before City4
    assert data[0]["city"] == "City5"

@pytest.mark.django_db
def test_case_insensitive_search_and_logging(client):
    city_input = "lOnDoN"
    with requests_mock.Mocker() as m:
        m.get("https://geocoding-api.open-meteo.com/v1/search", json={
            "results": [{
                "name": "London",
                "latitude": 51.5,
                "longitude": -0.1
            }]
        })
        m.get("https://api.open-meteo.com/v1/forecast", json={
            "current_weather": {"temperature": 12, "windspeed": 3},
            "daily": {
                "time": ["2025-08-01"],
                "temperature_2m_max": [18],
                "temperature_2m_min": [10],
                "weathercode": [0]
            }
        })
        url = reverse("weather-by-city")
        resp = client.get(url, {"city": city_input})
        assert resp.status_code == 200
        data = resp.json()
        # Response city uses normalized name from geocode
        assert data["city"] == "London"
        # Check that a Search entry was created with the original input (or desired behavior)
        searches = Search.objects.filter(city__iexact=city_input)
        assert searches.exists()
