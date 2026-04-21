from django.contrib import admin
from django.utils.html import format_html

from inventario.models import InventarioProducto, MovimientoInventario


@admin.register(InventarioProducto)
class InventarioProductoAdmin(admin.ModelAdmin):
    """
    Administración del inventario consolidado.
    """

    list_display = (
        "producto",
        "stock_actual",
        "stock_reservado",
        "mostrar_stock_disponible",
        "stock_minimo",
        "mostrar_estado_stock",
        "activo_para_venta",
        "updated_at",
    )
    search_fields = ("producto__nombre",)
    list_filter = ("activo_para_venta",)
    autocomplete_fields = ("producto",)

    def mostrar_stock_disponible(self, obj: InventarioProducto) -> int:
        """
        Muestra el stock disponible calculado.
        """
        return obj.stock_disponible

    mostrar_stock_disponible.short_description = "Stock disponible"

    def mostrar_estado_stock(self, obj: InventarioProducto) -> str:
        """
        Muestra un indicador visual del estado del stock.
        """
        if obj.stock_disponible <= 0:
            return format_html('<span style="color: red; font-weight: 700;">Sin stock</span>')

        if obj.bajo_stock:
            return format_html(
                '<span style="color: orange; font-weight: 700;">Bajo stock</span>'
            )

        return format_html('<span style="color: green; font-weight: 700;">Disponible</span>')

    mostrar_estado_stock.short_description = "Estado"


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    """
    Historial de movimientos. Debe tratarse como trazabilidad,
    por eso no conviene editarlo libremente.
    """

    list_display = (
        "inventario",
        "tipo_movimiento",
        "origen",
        "cantidad",
        "stock_anterior",
        "stock_posterior",
        "creado_por",
        "created_at",
    )
    search_fields = (
        "inventario__producto__nombre",
        "motivo",
        "referencia_externa",
    )
    list_filter = (
        "tipo_movimiento",
        "origen",
        "created_at",
    )
    readonly_fields = (
        "inventario",
        "tipo_movimiento",
        "origen",
        "cantidad",
        "stock_anterior",
        "stock_posterior",
        "motivo",
        "referencia_externa",
        "creado_por",
        "created_at",
    )

    def has_add_permission(self, request) -> bool:
        """
        Impide agregar movimientos manuales desde admin.
        Deben crearse desde servicios.
        """
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """
        Impide editar movimientos.
        """
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """
        Impide eliminar movimientos.
        """
        return False