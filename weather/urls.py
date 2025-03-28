from django.urls import path
from .views import WeatherAPIView

urlpatterns = [
    path("weather/", WeatherAPIView.as_view(), name="weather-data"),
    path("weather/<str:station_id>/", WeatherAPIView.as_view(), name="weather-detail"),
]
