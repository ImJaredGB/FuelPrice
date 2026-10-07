from rest_framework import serializers

from .models import (
    Region,
    Province,
    Municipality,
    Station,
    FuelType,
    FuelPrice,
)


class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = [
            "id",
            "api_id",
            "name",
        ]


class ProvinceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Province
        fields = [
            "id",
            "api_id",
            "name",
            "region",
        ]


class MunicipalitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Municipality
        fields = [
            "id",
            "api_id",
            "name",
            "province",
        ]


class StationSerializer(serializers.ModelSerializer):

    price = serializers.DecimalField(
        max_digits=6,
        decimal_places=3,
        read_only=True
    )

    price_recorded_at = serializers.DateTimeField(
        read_only=True
    )

    class Meta:
        model = Station
        fields = [
            "id",
            "api_id",
            "name",
            "address",
            "postal_code",
            "municipality",
            "latitude",
            "longitude",
            "schedule",
            "margin",
            "sale_type",
            "price",
            "price_recorded_at",
        ]

class FuelTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FuelType
        fields = [
            "id",
            "code",
            "name",
        ]

class FuelPriceSerializer(serializers.ModelSerializer):

    fuel_type = FuelTypeSerializer(
        read_only=True
    )

    class Meta:
        model = FuelPrice
        fields = [
            "id",
            "fuel_type",
            "price",
            "recorded_at",
        ]