from django.urls import path
from .views import weather_by_city, index

urlpatterns = [
    path("", index, name="home"),
    path("weather/", weather_by_city, name="weather-by-city"),
]
