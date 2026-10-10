import requests
import subprocess
import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery
from datetime import timedelta
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from app.models import FuelUpdateConfig, FuelPrice, FuelType

from .models import (
    Region,
    Province,
    Municipality,
    Station,
    FuelType,
    FuelPrice,
)

from .serializers import (
    RegionSerializer,
    ProvinceSerializer,
    MunicipalitySerializer,
    StationSerializer,
    FuelTypeSerializer,
    FuelPriceSerializer,
)

from django.db.models import (
    Avg, 
    Count
)

# ---- Inactivo ----
@api_view(["GET"])
def fuel(request):

    url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"

    result = subprocess.run(
        ["curl", "-s", url],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return Response(
            {"error":"Could not retrive fuel data"},
            status=502
        )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return Response(
            {"error":"Could not parse fuel data"},
            status=502
        )
    
    return Response(data)
# --------

@api_view(["GET"])
def regions(request):

    regions = Region.objects.all()

    serializer = RegionSerializer(
        regions,
        many=True
    )

    return Response(serializer.data)


@api_view(["GET"])
def provinces(request):

    provinces = Province.objects.all()

    serializer = ProvinceSerializer(
        provinces,
        many=True
    )

    return Response(serializer.data)


@api_view(["GET"])
def municipalities(request):

    municipalities = Municipality.objects.all()

    serializer = MunicipalitySerializer(
        municipalities,
        many=True
    )

    return Response(serializer.data)


@api_view(["GET"])
def stations(request):

    stations = Station.objects.all()

    province = request.query_params.get("province")
    municipality = request.query_params.get("municipality")
    fuel = request.query_params.get("fuel")

    if province:
        stations = stations.filter(
            municipality__province__api_id=province
        )

    if municipality:
        stations = stations.filter(
            municipality__api_id=municipality
        )

    if fuel:

        latest_price = FuelPrice.objects.filter(
            station=OuterRef("pk"),
            fuel_type__code=fuel
        ).order_by("-recorded_at")

        stations = stations.filter(
            prices__fuel_type__code=fuel
        ).annotate(
            price=Subquery(
                latest_price.values("price")[:1]
            ),
            price_recorded_at=Subquery(
                latest_price.values("recorded_at")[:1]
            )
        ).distinct()

    serializer = StationSerializer(
        stations,
        many=True
    )

    return Response(serializer.data)

@api_view(["GET"])
def fuel_types(request):

    fuel_types = FuelType.objects.all()

    serializer = FuelTypeSerializer(
        fuel_types,
        many=True
    )

    return Response(serializer.data)

@api_view(["GET"])
def station_prices(request, station_id):

    prices = FuelPrice.objects.filter(
        station_id=station_id
    ).select_related(
        "fuel_type"
    )

    fuel = request.query_params.get("fuel")
    days = request.query_params.get("days")

    if fuel:
        prices = prices.filter(
            fuel_type__code=fuel
        )

    if days:
        try:
            days = int(days)

            if days > 0:
                start_date = timezone.now() - timedelta(days=days)

                prices = prices.filter(
                    recorded_at__gte=start_date
                )

        except ValueError:
            pass

    serializer = FuelPriceSerializer(
        prices,
        many=True
    )

    return Response(serializer.data)

@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def fuel_update_config(request):
    config, _ = FuelUpdateConfig.objects.get_or_create(
        pk=1,
        defaults={"enabled": True},
    )

    if request.method == "GET":
        return Response({
            "enabled": config.enabled,
            "updated_at": config.updated_at,
        })

    enabled = request.data.get("enabled")

    if not isinstance(enabled, bool):
        return Response(
            {"error": "El campo 'enabled' debe ser true o false."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    config.enabled = enabled
    config.save(update_fields=["enabled", "updated_at"])

    return Response({
        "enabled": config.enabled,
        "updated_at": config.updated_at,
        "message": (
            "Actualización automática activada."
            if config.enabled
            else "Actualización automática desactivada."
        ),
    })


@api_view(["GET"])
def province_price_comparation(request):
    fuel_code = request.query_params.get("fuel_type")

    if not fuel_code:
        return Response(
            {"error": "Debes indicar el combustible mediante fuel_type."},
            status=400,
        )

    if not FuelType.objects.filter(code=fuel_code).exists():
        return Response(
            {"error": "El tipo de combustible no existe."},
            status=404,
        )

    results = (
        FuelPrice.objects
        .filter(fuel_type__code=fuel_code)
        .values(
            "station__municipality__province__api_id",
            "station__municipality__province__name",
        )
        .annotate(
            average_price=Avg("price"),
            station_count=Count("station", distinct=True),
        )
        .order_by("station__municipality__province__name")
    )

    provinces = []

    for item in results:
        average = item["average_price"]

        provinces.append({
            "province_api_id":
                item["station__municipality__province__api_id"],
            "province":
                item["station__municipality__province__name"],
            "average_price":
                format(average, ".3f") if average is not None else None,
            "station_count": item["station_count"],
        })

    return Response(provinces)
