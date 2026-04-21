from django.contrib import admin

from ordenes.models import Orden, OrdenItem


class OrdenItemInline(admin.TabularInline):
    model = OrdenItem
    extra = 0
    readonly_fields = (
        "juego",
        "nombre_producto",
        "precio_unitario",
        "cantidad",
        "subtotal",
    )
    can_delete = False


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = (
        "referencia",
        "usuario",
        "estado",
        "subtotal",
        "total",
        "created_at",
    )
    list_filter = ("estado", "created_at")
    search_fields = ("referencia", "usuario__username", "usuario__email")
    readonly_fields = ("referencia", "created_at", "updated_at")
    inlines = [OrdenItemInline]


@admin.register(OrdenItem)
class OrdenItemAdmin(admin.ModelAdmin):
    list_display = (
        "orden",
        "nombre_producto",
        "cantidad",
        "precio_unitario",
        "subtotal",
    )
    search_fields = ("orden__referencia", "nombre_producto")