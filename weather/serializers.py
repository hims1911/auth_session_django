from rest_framework import serializers

class WeatherDataSerializer(serializers.Serializer):
    station_name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    temperature = serializers.FloatField()
