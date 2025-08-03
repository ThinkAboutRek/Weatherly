import pytest
from django.urls import reverse
import requests_mock

@pytest.mark.django_db
def test_weather_by_city_success(client):
    city = "London"

    # Mock external API calls
    with requests_mock.Mocker() as m:
        m.get("https://geocoding-api.open-meteo.com/v1/search", json={
            "results": [{
                "name": "London",
                "latitude": 51.5,
                "longitude": -0.1
            }]
        })
        m.get("https://api.open-meteo.com/v1/forecast", json={
            "current_weather": {"temperature": 10, "windspeed": 5},
            "daily": {
                "time": ["2025-08-01"],
                "temperature_2m_max": [15],
                "temperature_2m_min": [7],
                "weathercode": [0],
            }
        })

        url = reverse("weather-by-city")
        response = client.get(url, {"city": city})
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == city
        assert "current" in data and "daily" in data

@pytest.mark.django_db
def test_weather_by_city_missing_param(client):
    url = reverse("weather-by-city")
    response = client.get(url)  # no city query
    assert response.status_code == 400
    body = response.json()
    assert "error" in body and "provide a city" in body["error"].lower()
