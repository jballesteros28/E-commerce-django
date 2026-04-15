from django.contrib import admin
from .models import Juego


@admin.register(Juego)
class JuegoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "precio", "plataforma")
    search_fields = ("nombre", "plataforma")
    list_filter = ("plataforma",)