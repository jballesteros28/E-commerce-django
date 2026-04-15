from django.contrib import admin
from .models import Favorito


@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "juego", "fecha_agregado")
    search_fields = ("usuario__username", "juego__nombre")
    list_filter = ("fecha_agregado",)