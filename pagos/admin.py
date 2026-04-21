from django.contrib import admin

from pagos.models import Pago, WebhookPagoLog


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "orden",
        "proveedor",
        "estado",
        "monto",
        "moneda",
        "external_id",
        "created_at",
    )
    list_filter = ("proveedor", "estado", "created_at")
    search_fields = (
        "orden__referencia",
        "orden__usuario__username",
        "external_id",
        "preference_id",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(WebhookPagoLog)
class WebhookPagoLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "proveedor",
        "procesado",
        "detalle",
        "created_at",
    )
    list_filter = ("proveedor", "procesado", "created_at")
    readonly_fields = (
        "proveedor",
        "payload",
        "query_params",
        "headers",
        "procesado",
        "detalle",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False