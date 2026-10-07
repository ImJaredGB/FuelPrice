import json
import subprocess

from datetime import datetime
from zoneinfo import ZoneInfo

from django.core.management.base import BaseCommand

from app.models import (
    Region,
    Province,
    Municipality,
    Station,
    FuelType,
    FuelPrice,
)


FUEL_TYPES = {
    "Precio Gasoleo A": {
        "code": "diesel_a",
        "name": "Diesel A",
    },
    "Precio Gasoleo Premium": {
        "code": "diesel_premium",
        "name": "Diesel Premium",
    },
    "Precio Gasoleo B": {
        "code": "diesel_b",
        "name": "Diesel B",
    },
    "Precio Gasolina 95 E5": {
        "code": "gasoline_95_e5",
        "name": "Gasoline 95 E5",
    },
    "Precio Gasolina 95 E10": {
        "code": "gasoline_95_e10",
        "name": "Gasoline 95 E10",
    },
    "Precio Gasolina 98 E5": {
        "code": "gasoline_98_e5",
        "name": "Gasoline 98 E5",
    },
    "Precio Gasolina 98 E10": {
        "code": "gasoline_98_e10",
        "name": "Gasoline 98 E10",
    },
    "Precio Gasolina 95 E25": {
        "code": "gasoline_95_e25",
        "name": "Gasoline 95 E25",
    },
    "Precio Gasolina 95 E85": {
        "code": "gasoline_95_e85",
        "name": "Gasoline 95 E85",
    },
    "Precio Gasolina 95 E5 Premium": {
        "code": "gasoline_95_e5_premium",
        "name": "Gasoline 95 E5 Premium",
    },
    "Precio Biodiesel": {
        "code": "biodiesel",
        "name": "Biodiesel",
    },
    "Precio Bioetanol": {
        "code": "bioethanol",
        "name": "Bioethanol",
    },
    "Precio Gasolina Renovable": {
        "code": "renewable_gasoline",
        "name": "Renewable Gasoline",
    },
    "Precio Diésel Renovable": {
        "code": "renewable_diesel",
        "name": "Renewable Diesel",
    },
}


class Command(BaseCommand):

    help = "Import fuel station and price data from the Ministry API"

    def handle(self, *args, **options):

        url = (
            "https://sedeaplicaciones.minetur.gob.es/"
            "ServiciosRESTCarburantes/"
            "PreciosCarburantes/"
            "EstacionesTerrestres/"
            "FiltroCCAA/09"
        )

        self.stdout.write("Downloading fuel data...")

        result = subprocess.run(
            ["curl", "-s", url],
            capture_output=True,
            text=True,
            check=True,
        )

        data = json.loads(result.stdout)

        stations = data["ListaEESSPrecio"]

        self.stdout.write(
            f"Downloaded {len(stations)} stations."
        )

        # API timestamp
        recorded_at = datetime.strptime(
            data["Fecha"],
            "%d/%m/%Y %H:%M:%S"
        )

        recorded_at = recorded_at.replace(
            tzinfo=ZoneInfo("Europe/Madrid")
        )

        # Region
        region, _ = Region.objects.get_or_create(
            api_id="09",
            defaults={
                "name": "Cataluña",
            },
        )

        # Counters
        provinces_created = 0
        municipalities_created = 0
        stations_created = 0
        stations_updated = 0
        prices_created = 0

        # Import stations
        for station_data in stations:

            # Province
            province, created = Province.objects.get_or_create(
                api_id=station_data["IDProvincia"],
                defaults={
                    "name": station_data["Provincia"],
                    "region": region,
                },
            )

            if created:
                provinces_created += 1

            # Municipality
            municipality, created = Municipality.objects.get_or_create(
                api_id=station_data["IDMunicipio"],
                defaults={
                    "name": station_data["Municipio"],
                    "province": province,
                },
            )

            if created:
                municipalities_created += 1

            # Coordinates
            latitude = station_data["Latitud"].replace(",", ".")
            longitude = station_data["Longitud (WGS84)"].replace(",", ".")

            # Station
            station, created = Station.objects.update_or_create(
                api_id=station_data["IDEESS"],
                defaults={
                    "name": station_data["Rótulo"],
                    "address": station_data["Dirección"],
                    "postal_code": station_data["C.P."],
                    "municipality": municipality,
                    "latitude": latitude,
                    "longitude": longitude,
                    "schedule": station_data["Horario"],
                    "margin": station_data["Margen"],
                    "sale_type": station_data["Tipo Venta"],
                },
            )

            if created:
                stations_created += 1
            else:
                stations_updated += 1

            # Fuel prices
            for api_field, fuel_data in FUEL_TYPES.items():

                raw_price = station_data.get(
                    api_field,
                    ""
                ).strip()

                if not raw_price:
                    continue

                price = raw_price.replace(",", ".")

                fuel_type, _ = FuelType.objects.get_or_create(
                    code=fuel_data["code"],
                    defaults={
                        "name": fuel_data["name"],
                    },
                )

                _, created = FuelPrice.objects.get_or_create(
                    station=station,
                    fuel_type=fuel_type,
                    recorded_at=recorded_at,
                    defaults={
                        "price": price,
                    },
                )

                if created:
                    prices_created += 1

        # Result
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Import completed successfully."
            )
        )

        self.stdout.write(
            f"Provinces created: {provinces_created}"
        )

        self.stdout.write(
            f"Municipalities created: {municipalities_created}"
        )

        self.stdout.write(
            f"Stations created: {stations_created}"
        )

        self.stdout.write(
            f"Stations updated: {stations_updated}"
        )

        self.stdout.write(
            f"Prices created: {prices_created}"
        )