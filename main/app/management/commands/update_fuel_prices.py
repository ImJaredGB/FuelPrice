
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from app.models import FuelUpdateConfig


class Command(BaseCommand):
    help = "Actualiza los precios si la actualización automática está activada."

    def handle(self, *args, **options):
        config, _ = FuelUpdateConfig.objects.get_or_create(
            pk=1,
            defaults={"enabled": True},
        )

        if not config.enabled:
            self.stdout.write(
                self.style.WARNING(
                    "Actualización automática desactivada. "
                    "No se importarán nuevos precios."
                )
            )
            return

        self.stdout.write("Actualización automática activada.")
        self.stdout.write("Iniciando importación de precios...")

        try:
            call_command("import_fuel_data")
        except Exception as error:
            raise CommandError(
                f"No se pudo actualizar el precio del combustible: {error}"
            ) from error
