from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import fetch_air_temperature_data
from .serializers import WeatherDataSerializer


class WeatherAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Handles:
    - GET /api/weather/ => List all station weather data
    - GET /api/weather/<station_id>/ => Get single station data
    """

    @extend_schema(
        parameters=[
            OpenApiParameter(name='station_id', description='Station ID (e.g., S117)', required=False, type=str),
        ],
        responses={200: WeatherDataSerializer(many=True)},
        description="Returns air temperature readings for all weather stations or a single station if station_id is "
                    "provided in the URL."
    )
    def get(self, request, station_id=None):
        data = fetch_air_temperature_data()
        if not data:
            return Response({"error": "Unable to fetch weather data"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        stations = {s["id"]: s for s in data["metadata"]["stations"]}
        readings = {r["station_id"]: r["value"] for r in data["items"][0]["readings"]}

        # If station_id is provided, return a single reading
        if station_id:
            if station_id not in stations:
                return Response({"error": "Station not found"}, status=status.HTTP_404_NOT_FOUND)

            station = stations[station_id]
            result = {
                "station_name": station.get("name"),
                "latitude": station.get("location", {}).get("latitude"),
                "longitude": station.get("location", {}).get("longitude"),
                "temperature": readings.get(station_id)
            }
            serializer = WeatherDataSerializer(result)
            return Response(serializer.data)

        # Otherwise return all readings
        results = []
        for sid, temp in readings.items():
            station = stations.get(sid, {})
            results.append({
                "station_name": station.get("name"),
                "latitude": station.get("location", {}).get("latitude"),
                "longitude": station.get("location", {}).get("longitude"),
                "temperature": temp
            })
        serializer = WeatherDataSerializer(results, many=True)
        return Response({"weather_data": serializer.data}, status=status.HTTP_200_OK)
