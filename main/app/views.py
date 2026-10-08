import requests
import subprocess
import json

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery
from datetime import timedelta
from django.utils import timezone

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