from django.urls import path
from .views import weather_by_city

urlpatterns = [
    path("weather/", weather_by_city, name="weather-by-city"),
]
