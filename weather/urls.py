from django.urls import path
from .views import index, weather_by_city, recent_searches

urlpatterns = [
    path("", index, name="home"),
    path("weather/", weather_by_city, name="weather-by-city"),
    path("searches/", recent_searches, name="recent-searches"),
]
