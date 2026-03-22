from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views, auth_views

urlpatterns = [
    # HTML pages
    path("", views.index, name="home"),
    path("register/", auth_views.register_view, name="register"),
    path("login/", auth_views.login_view, name="login"),
    path("logout/", auth_views.logout_view, name="logout"),
    path("history/", views.search_history, name="history"),
    path("history/export/", views.export_csv, name="export-csv"),

    # JSON API
    path("api/weather/", views.weather_by_city, name="weather-by-city"),
    path("api/weather-coords/", views.weather_by_coords, name="weather-by-coords"),
    path("api/searches/", views.recent_searches, name="recent-searches"),
    path("api/searches/history/", views.paginated_history, name="paginated-history"),
    path("api/token/", obtain_auth_token, name="api-token"),
]
