from django.db import models


class Region(models.Model):
    api_id = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Province(models.Model):
    api_id = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=100)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="provinces"
    )

    def __str__(self):
        return self.name


class Municipality(models.Model):
    api_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=150)
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="municipalities"
    )

    def __str__(self):
        return self.name


class Station(models.Model):
    api_id = models.CharField(max_length=20, unique=True)

    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)

    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.PROTECT,
        related_name="stations"
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    schedule = models.TextField(blank=True)
    margin = models.CharField(max_length=10, blank=True)
    sale_type = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.name


class FuelType(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FuelPrice(models.Model):
    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="prices"
    )

    fuel_type = models.ForeignKey(
        FuelType,
        on_delete=models.PROTECT,
        related_name="prices"
    )

    price = models.DecimalField(
        max_digits=6,
        decimal_places=3
    )

    recorded_at = models.DateTimeField()

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.station} - {self.fuel_type}: {self.price}"