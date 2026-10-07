from django.urls import path
from .views import (
    fuel,
    regions,
    provinces,
    municipalities,
    stations,
    fuel_types,
    station_prices,
)

urlpatterns = [
    path('fuel/', fuel, name='fuel'),
    path("regions/", regions, name="regions"),
    path("provinces/", provinces, name="provinces"),
    path("municipalities/", municipalities, name="municipalities"),
    path("stations/", stations, name="stations"),
    path("fuel-types/", fuel_types, name="fuel-types"),
    path(
        "stations/<int:station_id>/prices/",
        station_prices,
        name="station-prices",
    ),
]