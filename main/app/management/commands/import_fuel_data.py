import json
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal, InvalidOperation

from app.models import (
    FuelPrice,
    FuelType,
    Municipality,
    Province,
    Region,
    Station,
)


URL = (
    "https://sedeaplicaciones.minetur.gob.es/"
    "ServiciosRESTCarburantes/PreciosCarburantes/"
    "EstacionesTerrestres/FiltroCCAA/09"
)


FUEL_TYPES = {
    "Precio Gasoleo A": ("diesel_a", "Diesel A"),
    "Precio Gasoleo Premium": ("diesel_premium", "Diesel Premium"),
    "Precio Gasoleo B": ("diesel_b", "Diesel B"),
    "Precio Gasolina 95 E5": ("gasoline_95_e5", "Gasolina 95 E5"),
    "Precio Gasolina 95 E10": ("gasoline_95_e10", "Gasolina 95 E10"),
    "Precio Gasolina 98 E5": ("gasoline_98_e5", "Gasolina 98 E5"),
    "Precio Gasolina 98 E10": ("gasoline_98_e10", "Gasolina 98 E10"),
    "Precio Gasolina 95 E25": ("gasoline_95_e25", "Gasolina 95 E25"),
    "Precio Gasolina 95 E85": ("gasoline_95_e85", "Gasolina 95 E85"),
    "Precio Gasolina 95 E5 Premium": (
        "gasoline_95_e5_premium",
        "Gasolina 95 E5 Premium",
    ),
    "Precio Biodiesel": ("biodiesel", "Biodiesel"),
    "Precio Bioetanol": ("bioethanol", "Bioetanol"),
    "Precio Gasolina Renovable": (
        "renewable_gasoline",
        "Gasolina Renovable",
    ),
    "Precio Diésel Renovable": (
        "renewable_diesel",
        "Diésel Renovable",
    ),
}


class Command(BaseCommand):
    help = "Importa los precios actuales de combustible de Cataluña."

    def handle(self, *args, **options):

        self.stdout.write("Descargando datos de combustible...")

        # ---------------------------------------------------------
        # 1. DESCARGAR DATOS
        # ---------------------------------------------------------

        try:
            result = subprocess.run(
                ["curl", "-s", URL],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as error:
            self.stderr.write(
                self.style.ERROR(
                    f"Error al descargar los datos: {error}"
                )
            )
            return

        # ---------------------------------------------------------
        # 2. PARSEAR JSON
        # ---------------------------------------------------------

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.stderr.write(
                self.style.ERROR(
                    "La respuesta de la API no contiene un JSON válido."
                )
            )
            return

        stations_data = data.get("ListaEESSPrecio")

        if not isinstance(stations_data, list) or not stations_data:
            self.stderr.write(
                self.style.ERROR(
                    "La API no devolvió ninguna estación. "
                    "No se modificará la base de datos."
                )
            )
            return

        # ---------------------------------------------------------
        # 3. FECHA DE LOS DATOS
        # ---------------------------------------------------------

        try:
            recorded_at = datetime.strptime(
                data["Fecha"],
                "%d/%m/%Y %H:%M:%S",
            )

            recorded_at = recorded_at.replace(
                tzinfo=ZoneInfo("Europe/Madrid")
            )

        except (KeyError, ValueError):
            self.stderr.write(
                self.style.ERROR(
                    "No se pudo obtener una fecha válida de la API. "
                    "No se modificará la base de datos."
                )
            )
            return

        self.stdout.write(
            f"Datos publicados por la API: "
            f"{recorded_at.strftime('%d/%m/%Y %H:%M:%S')}"
        )

        self.stdout.write(
            f"Estaciones recibidas: {len(stations_data)}"
        )

        # ---------------------------------------------------------
        # 4. ACTUALIZAR BASE DE DATOS
        #
        # Todo lo que ocurra aquí está dentro de una transacción.
        #
        # Si algo falla:
        #
        #     ROLLBACK
        #
        # y los precios anteriores permanecen.
        # ---------------------------------------------------------

        try:
            with transaction.atomic():

                # -------------------------------------------------
                # REGION
                # -------------------------------------------------

                region, _ = Region.objects.get_or_create(
                    api_id="09",
                    defaults={
                        "name": "Cataluña",
                    },
                )

                # -------------------------------------------------
                # CACHE DE OBJETOS
                #
                # Evitamos hacer búsquedas repetidas innecesarias.
                # -------------------------------------------------

                provinces_cache = {}
                municipalities_cache = {}
                fuel_types_cache = {}

                # -------------------------------------------------
                # BORRAR PRECIOS ANTERIORES
                #
                # IMPORTANTE:
                # Esto ocurre dentro de transaction.atomic().
                #
                # Si algo falla después, PostgreSQL hará rollback.
                # -------------------------------------------------

                old_prices = FuelPrice.objects.count()

                FuelPrice.objects.all().delete()

                self.stdout.write(
                    f"Precios anteriores eliminados: {old_prices}"
                )

                # Lista donde prepararemos todos los nuevos precios
                new_prices = []

                # Contadores
                provinces_created = 0
                municipalities_created = 0
                stations_created = 0

                # -------------------------------------------------
                # PROCESAR ESTACIONES
                # -------------------------------------------------

                for station_data in stations_data:

                    # ---------------------------------------------
                    # PROVINCIA
                    # ---------------------------------------------

                    province_api_id = station_data.get(
                        "IDProvincia"
                    )

                    province_name = station_data.get(
                        "Provincia"
                    )

                    province_key = province_api_id

                    if province_key not in provinces_cache:

                        province, created = Province.objects.get_or_create(
                            api_id=province_api_id,
                            defaults={
                                "name": province_name,
                                "region": region,
                            },
                        )

                        provinces_cache[province_key] = province

                        if created:
                            provinces_created += 1

                    else:
                        province = provinces_cache[province_key]

                    # ---------------------------------------------
                    # MUNICIPIO
                    # ---------------------------------------------

                    municipality_api_id = station_data.get(
                        "IDMunicipio"
                    )

                    municipality_name = station_data.get(
                        "Municipio"
                    )

                    municipality_key = municipality_api_id

                    if municipality_key not in municipalities_cache:

                        municipality, created = (
                            Municipality.objects.get_or_create(
                                api_id=municipality_api_id,
                                defaults={
                                    "name": municipality_name,
                                    "province": province,
                                },
                            )
                        )

                        municipalities_cache[
                            municipality_key
                        ] = municipality

                        if created:
                            municipalities_created += 1

                    else:
                        municipality = municipalities_cache[
                            municipality_key
                        ]

                    # ---------------------------------------------
                    # ESTACIÓN
                    # ---------------------------------------------

                    station_api_id = station_data.get(
                        "IDEESS"
                    )

                    latitude = station_data.get("Latitud")
                    longitude = station_data.get("Longitud (WGS84)")

                    if latitude:
                        latitude = latitude.strip().replace(",", ".")

                    if longitude:
                        longitude = longitude.strip().replace(",", ".")

                    station_defaults = {
                        "name": station_data.get("Rótulo"),
                        "address": station_data.get("Dirección"),
                        "postal_code": station_data.get("C.P."),
                        "municipality": municipality,
                        "latitude": latitude,
                        "longitude": longitude,
                        "schedule": station_data.get("Horario") or "",
                        "margin": station_data.get("Margen") or "",
                        "sale_type": station_data.get("Tipo Venta") or "",
                    }

                    station, created = Station.objects.update_or_create(
                        api_id=station_api_id,
                        defaults=station_defaults,
                    )

                    if created:
                        stations_created += 1

                    # ---------------------------------------------
                    # PRECIOS
                    # ---------------------------------------------

                    for api_field, fuel_info in FUEL_TYPES.items():

                        raw_price = station_data.get(api_field)

                        if not raw_price:
                            continue

                        raw_price = raw_price.strip()

                        if not raw_price:
                            continue

                        # La API utiliza coma decimal.
                        raw_price = raw_price.replace(",", ".")

                        try:
                            price = Decimal(raw_price)
                        except InvalidOperation:
                            continue

                        fuel_code, fuel_name = fuel_info

                        if fuel_code not in fuel_types_cache:

                            fuel_type, _ = FuelType.objects.get_or_create(
                                code=fuel_code,
                                defaults={
                                    "name": fuel_name,
                                },
                            )

                            fuel_types_cache[
                                fuel_code
                            ] = fuel_type

                        else:
                            fuel_type = fuel_types_cache[
                                fuel_code
                            ]

                        new_prices.append(
                            FuelPrice(
                                station=station,
                                fuel_type=fuel_type,
                                price=price,
                                recorded_at=recorded_at,
                            )
                        )

                # -------------------------------------------------
                # INSERTAR TODOS LOS PRECIOS NUEVOS
                # -------------------------------------------------

                FuelPrice.objects.bulk_create(
                    new_prices,
                    batch_size=1000,
                )

        except Exception as error:

            self.stderr.write(
                self.style.ERROR(
                    "Error durante la actualización."
                )
            )

            self.stderr.write(
                self.style.ERROR(
                    f"Detalle: {error}"
                )
            )

            self.stderr.write(
                self.style.ERROR(
                    "Los datos anteriores se han conservado "
                    "gracias al rollback de la transacción."
                )
            )

            return

        # ---------------------------------------------------------
        # 5. RESULTADO
        # ---------------------------------------------------------

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Actualización completada correctamente."
            )
        )

        self.stdout.write(
            f"Provincias nuevas: {provinces_created}"
        )

        self.stdout.write(
            f"Municipios nuevos: {municipalities_created}"
        )

        self.stdout.write(
            f"Estaciones nuevas: {stations_created}"
        )

        self.stdout.write(
            f"Precios actuales: {len(new_prices)}"
        )

        self.stdout.write(
            f"Fecha de los precios: "
            f"{recorded_at.strftime('%d/%m/%Y %H:%M:%S')}"
        )