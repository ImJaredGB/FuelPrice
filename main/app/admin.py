from django.contrib import admin
from .models import FuelUpdateConfig


@admin.register(FuelUpdateConfig)
class FuelUpdateConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "enabled", "updated_at")
    list_editable = ("enabled",)
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return (
            super().has_add_permission(request)
            and not FuelUpdateConfig.objects.exists()
        )

    def has_delete_permission(self, request, obj=None):
        return False