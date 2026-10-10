from django.urls import path
from .views import (
    fuel,
    regions,
    provinces,
    municipalities,
    stations,
    fuel_types,
    station_prices,
    fuel_update_config,
    province_price_comparation,
)

urlpatterns = [
    path('fuel/', fuel, name='fuel'),
    path("regions/", regions, name="regions"),
    path("provinces/", provinces, name="provinces"),
    path("municipalities/", municipalities, name="municipalities"),
    path("stations/", stations, name="stations"),
    path("fuel-types/", fuel_types, name="fuel-types"),
    path("stations/<int:station_id>/prices/",station_prices,name="station-prices"),
    path("fuel/update-config/",fuel_update_config,name="fuel_update_config"),
    path("fuel/province-comparation/",province_price_comparation,name="province_price_comparation")
]