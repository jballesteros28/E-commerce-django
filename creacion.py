import os
import django
from decimal import Decimal

# Configurar entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tienda_ecommerce.settings")
django.setup()

from catalogo.models import Juego  # cambia 'juegos' por el nombre real de tu app


def cargar_juegos():
    lista_juegos = [
        {"nombre": "FIFA 24", "precio": Decimal("59.99"), "plataforma": "PS5"},
        {"nombre": "Call of Duty MW3", "precio": Decimal("69.99"), "plataforma": "PC"},
        {"nombre": "EA Sports FC 25", "precio": Decimal("64.99"), "plataforma": "Xbox Series X"},
        {"nombre": "God of War Ragnarok", "precio": Decimal("49.99"), "plataforma": "PS5"},
        {"nombre": "Spider-Man 2", "precio": Decimal("69.99"), "plataforma": "PS5"},
        {"nombre": "Red Dead Redemption 2", "precio": Decimal("39.99"), "plataforma": "PC"},
        {"nombre": "Minecraft", "precio": Decimal("29.99"), "plataforma": "Multiplataforma"},
        {"nombre": "GTA V", "precio": Decimal("34.99"), "plataforma": "PS4"},
        {"nombre": "Cyberpunk 2077", "precio": Decimal("44.99"), "plataforma": "PC"},
        {"nombre": "The Witcher 3", "precio": Decimal("24.99"), "plataforma": "PC"},
        {"nombre": "Resident Evil 4", "precio": Decimal("54.99"), "plataforma": "PS5"},
        {"nombre": "Hogwarts Legacy", "precio": Decimal("59.99"), "plataforma": "Xbox"},
        {"nombre": "Assassin's Creed Mirage", "precio": Decimal("49.99"), "plataforma": "PS5"},
        {"nombre": "Elden Ring", "precio": Decimal("59.99"), "plataforma": "PC"},
        {"nombre": "Forza Horizon 5", "precio": Decimal("49.99"), "plataforma": "Xbox"},
        {"nombre": "Mortal Kombat 1", "precio": Decimal("64.99"), "plataforma": "PS5"},
        {"nombre": "NBA 2K25", "precio": Decimal("59.99"), "plataforma": "PS5"},
        {"nombre": "Valorant", "precio": Decimal("0.00"), "plataforma": "PC"},
        {"nombre": "League of Legends", "precio": Decimal("0.00"), "plataforma": "PC"},
        {"nombre": "Fortnite", "precio": Decimal("0.00"), "plataforma": "Multiplataforma"},
    ]

    for juego in lista_juegos:
        Juego.objects.create(**juego)

    print("Se cargaron 20 juegos correctamente.")


if __name__ == "__main__":
    cargar_juegos()