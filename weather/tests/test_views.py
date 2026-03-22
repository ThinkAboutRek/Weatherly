import pytest
from django.urls import reverse
import requests_mock as req_mock_lib
from django.contrib.auth.models import User
from weather.models import Search


# ---------------------------------------------------------------------------
# weather_by_city
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_weather_by_city_success(client):
    with req_mock_lib.Mocker() as m:
        m.get("https://geocoding-api.open-meteo.com/v1/search", json={
            "results": [{"name": "London", "latitude": 51.5, "longitude": -0.1}]
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
        response = client.get(reverse("weather-by-city"), {"city": "London"})
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "London"
        assert "current" in data and "daily" in data


@pytest.mark.django_db
def test_weather_by_city_missing_param(client):
    response = client.get(reverse("weather-by-city"))
    assert response.status_code == 400
    body = response.json()
    assert "error" in body and "provide a city" in body["error"].lower()


@pytest.mark.django_db
def test_weather_by_city_not_found(client):
    with req_mock_lib.Mocker() as m:
        m.get("https://geocoding-api.open-meteo.com/v1/search", json={"results": []})
        resp = client.get(reverse("weather-by-city"), {"city": "NonExistentPlace"})
        assert resp.status_code == 404
        assert "not found" in resp.json()["error"].lower()


@pytest.mark.django_db
def test_weather_by_city_logs_search(client):
    with req_mock_lib.Mocker() as m:
        m.get("https://geocoding-api.open-meteo.com/v1/search", json={
            "results": [{"name": "Paris", "latitude": 48.8, "longitude": 2.3}]
        })
        m.get("https://api.open-meteo.com/v1/forecast", json={
            "current_weather": {"temperature": 20, "windspeed": 2},
            "daily": {"time": [], "temperature_2m_max": [], "temperature_2m_min": [], "weathercode": []}
        })
        client.get(reverse("weather-by-city"), {"city": "Paris"})
        assert Search.objects.filter(city="Paris").exists()


@pytest.mark.django_db
def test_weather_by_city_logs_user_when_authenticated(client):
    user = User.objects.create_user(username="tester", password="pass")
    client.login(username="tester", password="pass")
    with req_mock_lib.Mocker() as m:
        m.get("https://geocoding-api.open-meteo.com/v1/search", json={
            "results": [{"name": "Rome", "latitude": 41.9, "longitude": 12.5}]
        })
        m.get("https://api.open-meteo.com/v1/forecast", json={
            "current_weather": {"temperature": 25, "windspeed": 3},
            "daily": {"time": [], "temperature_2m_max": [], "temperature_2m_min": [], "weathercode": []}
        })
        client.get(reverse("weather-by-city"), {"city": "Rome"})
        assert Search.objects.filter(city="Rome", user=user).exists()


@pytest.mark.django_db
def test_weather_by_city_upstream_error(client):
    with req_mock_lib.Mocker() as m:
        m.get("https://geocoding-api.open-meteo.com/v1/search", json={
            "results": [{"name": "Berlin", "latitude": 52.5, "longitude": 13.4}]
        })
        m.get("https://api.open-meteo.com/v1/forecast", status_code=500, text="error")
        resp = client.get(reverse("weather-by-city"), {"city": "Berlin"})
        assert resp.status_code == 502


@pytest.mark.django_db
def test_case_insensitive_search_normalises_city(client):
    with req_mock_lib.Mocker() as m:
        m.get("https://geocoding-api.open-meteo.com/v1/search", json={
            "results": [{"name": "London", "latitude": 51.5, "longitude": -0.1}]
        })
        m.get("https://api.open-meteo.com/v1/forecast", json={
            "current_weather": {"temperature": 12, "windspeed": 3},
            "daily": {"time": ["2025-08-01"], "temperature_2m_max": [18], "temperature_2m_min": [10], "weathercode": [0]}
        })
        resp = client.get(reverse("weather-by-city"), {"city": "lOnDoN"})
        assert resp.status_code == 200
        # normalised name comes from geocoding API, not raw input
        assert resp.json()["city"] == "London"
        assert Search.objects.filter(city__iexact="london").exists()


# ---------------------------------------------------------------------------
# weather_by_coords
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_weather_by_coords_success(client):
    with req_mock_lib.Mocker() as m:
        m.get("https://api.open-meteo.com/v1/forecast", json={
            "latitude": 51.5,
            "longitude": -0.1,
            "current_weather": {"temperature": 14, "windspeed": 6},
            "daily": {
                "time": ["2025-08-01"],
                "temperature_2m_max": [17],
                "temperature_2m_min": [9],
                "weathercode": [1],
            }
        })
        m.get("https://nominatim.openstreetmap.org/reverse", json={
            "address": {"city": "London"},
            "display_name": "London, England"
        })
        resp = client.get(reverse("weather-by-coords"), {"lat": "51.5", "lon": "-0.1"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["city"] == "London"
        assert "current" in data and "daily" in data


@pytest.mark.django_db
def test_weather_by_coords_missing_params(client):
    resp = client.get(reverse("weather-by-coords"))
    assert resp.status_code == 400
    assert "error" in resp.json()


@pytest.mark.django_db
def test_weather_by_coords_logs_search(client):
    with req_mock_lib.Mocker() as m:
        m.get("https://api.open-meteo.com/v1/forecast", json={
            "latitude": 48.8,
            "longitude": 2.3,
            "current_weather": {"temperature": 18, "windspeed": 4},
            "daily": {"time": [], "temperature_2m_max": [], "temperature_2m_min": [], "weathercode": []}
        })
        m.get("https://nominatim.openstreetmap.org/reverse", json={
            "address": {"city": "Paris"},
            "display_name": "Paris, France"
        })
        client.get(reverse("weather-by-coords"), {"lat": "48.8", "lon": "2.3"})
        assert Search.objects.filter(city="Paris").exists()


@pytest.mark.django_db
def test_weather_by_coords_reverse_geocode_failure_uses_fallback(client):
    with req_mock_lib.Mocker() as m:
        m.get("https://api.open-meteo.com/v1/forecast", json={
            "latitude": 0.0,
            "longitude": 0.0,
            "current_weather": {"temperature": 30, "windspeed": 1},
            "daily": {"time": [], "temperature_2m_max": [], "temperature_2m_min": [], "weathercode": []}
        })
        m.get("https://nominatim.openstreetmap.org/reverse", status_code=500, text="error")
        resp = client.get(reverse("weather-by-coords"), {"lat": "0", "lon": "0"})
        assert resp.status_code == 200
        assert resp.json()["city"] == "Current Location"


@pytest.mark.django_db
def test_weather_by_coords_upstream_error(client):
    with req_mock_lib.Mocker() as m:
        m.get("https://api.open-meteo.com/v1/forecast", status_code=500, text="error")
        resp = client.get(reverse("weather-by-coords"), {"lat": "51.5", "lon": "-0.1"})
        assert resp.status_code == 502
