from django.urls import path
from .views import index, weather_by_city, weather_by_coords, recent_searches

urlpatterns = [
    path("", index, name="home"),
    path("weather/", weather_by_city, name="weather-by-city"),
    path("weather-coords/", weather_by_coords, name="weather-by-coords"),
    path("searches/", recent_searches, name="recent-searches"),
]
