from django.contrib import admin
from .models import Carrito, ItemCarrito


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "usuario",
        "creado",
        "actualizado",
    )

    search_fields = (
        "usuario__username",
        "usuario__email",
    )

    ordering = ("-actualizado",)


@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "carrito",
        "juego",
        "cantidad",
        "subtotal_admin",
    )

    search_fields = (
        "carrito__usuario__username",
        "juego__nombre",
    )

    list_filter = (
        "juego__plataforma",
    )

    def subtotal_admin(self, obj):
        return obj.subtotal()

    subtotal_admin.short_description = "Subtotal"