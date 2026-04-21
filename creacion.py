from __future__ import annotations

import os
from decimal import Decimal

import django
from django.apps import apps
from django.db import transaction


# Configurar entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tienda_ecommerce.settings")
django.setup()


Juego = apps.get_model("catalogo", "Juego")


def get_model_safe(app_label: str, model_name: str):
    """
    Devuelve el modelo si existe. Si no existe, retorna None.
    """
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None


@transaction.atomic
def limpiar_tablas_relacionadas() -> None:
    """
    Limpia tablas relacionadas al catálogo para dejar la semilla consistente.

    Orden importante:
    1. tablas hijas / dependientes
    2. catálogo
    """
    modelos_a_limpiar = [
        # Pagos
        ("pagos", "WebhookPagoLog"),
        ("pagos", "Pago"),

        # Órdenes
        ("ordenes", "OrdenItem"),
        ("ordenes", "Orden"),

        # Carrito
        ("carrito", "ItemCarrito"),
        ("carrito", "Carrito"),

        # Favoritos (si existe)
        ("favoritos", "Favorito"),

        # Inventario
        ("inventario", "MovimientoInventario"),
        ("inventario", "InventarioProducto"),

        # Catálogo
        ("catalogo", "Juego"),
    ]

    for app_label, model_name in modelos_a_limpiar:
        model = get_model_safe(app_label, model_name)
        if model is not None:
            deleted_count, _ = model.objects.all().delete()
            print(f"[OK] {app_label}.{model_name}: {deleted_count} registros eliminados.")


@transaction.atomic
def cargar_juegos() -> None:
    """
    Carga la semilla completa de juegos.
    """
    lista_juegos = [
        {
            "nombre": "FIFA 24",
            "descripcion": "Simulador de fútbol con licencias oficiales, modos competitivos y experiencia realista para jugar solo o en línea.",
            "precio": Decimal("59.99"),
            "plataforma": "PS5",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Call of Duty MW3",
            "descripcion": "Shooter de acción intensa con campaña cinematográfica, multijugador competitivo y combates rápidos de alta adrenalina.",
            "precio": Decimal("69.99"),
            "plataforma": "PC",
            "imagen": "default.jpg",
        },
        {
            "nombre": "EA Sports FC 25",
            "descripcion": "Nueva entrega del simulador de fútbol con plantillas actualizadas, Ultimate Team y modos online competitivos.",
            "precio": Decimal("64.99"),
            "plataforma": "Xbox Series X",
            "imagen": "default.jpg",
        },
        {
            "nombre": "God of War Ragnarok",
            "descripcion": "Aventura épica de acción con combates intensos, narrativa cinematográfica y mitología nórdica de primer nivel.",
            "precio": Decimal("49.99"),
            "plataforma": "PS5",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Spider-Man 2",
            "descripcion": "Acción de mundo abierto con desplazamiento ágil, combate dinámico y una historia centrada en Peter Parker y Miles Morales.",
            "precio": Decimal("69.99"),
            "plataforma": "PS5",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Red Dead Redemption 2",
            "descripcion": "Aventura western de mundo abierto con historia profunda, exploración inmersiva y una ambientación cinematográfica.",
            "precio": Decimal("39.99"),
            "plataforma": "PC",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Minecraft",
            "descripcion": "Juego sandbox creativo y de supervivencia donde puedes construir, explorar, recolectar recursos y jugar en comunidad.",
            "precio": Decimal("29.99"),
            "plataforma": "Multiplataforma",
            "imagen": "default.jpg",
        },
        {
            "nombre": "GTA V",
            "descripcion": "Mundo abierto de crimen y acción con misiones, exploración urbana, conducción y un potente modo online.",
            "precio": Decimal("34.99"),
            "plataforma": "PS4",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Cyberpunk 2077",
            "descripcion": "RPG futurista de mundo abierto con narrativa madura, exploración urbana y múltiples estilos de combate.",
            "precio": Decimal("44.99"),
            "plataforma": "PC",
            "imagen": "default.jpg",
        },
        {
            "nombre": "The Witcher 3",
            "descripcion": "RPG de fantasía con historia profunda, decisiones que impactan la narrativa y un enorme mundo abierto por explorar.",
            "precio": Decimal("24.99"),
            "plataforma": "PC",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Resident Evil 4",
            "descripcion": "Survival horror con acción, tensión constante, enemigos memorables y una campaña intensa y atmosférica.",
            "precio": Decimal("54.99"),
            "plataforma": "PS5",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Hogwarts Legacy",
            "descripcion": "Aventura RPG ambientada en el universo mágico de Harry Potter, con exploración, hechizos y combate.",
            "precio": Decimal("59.99"),
            "plataforma": "Xbox",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Assassin's Creed Mirage",
            "descripcion": "Juego de acción y sigilo con ambientación histórica, parkour y mecánicas clásicas de infiltración.",
            "precio": Decimal("49.99"),
            "plataforma": "PS5",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Elden Ring",
            "descripcion": "RPG de acción desafiante con mundo abierto, exploración libre, jefes exigentes y combate profundo.",
            "precio": Decimal("59.99"),
            "plataforma": "PC",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Forza Horizon 5",
            "descripcion": "Juego de carreras de mundo abierto con gran variedad de autos, paisajes espectaculares y conducción arcade-realista.",
            "precio": Decimal("49.99"),
            "plataforma": "Xbox",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Mortal Kombat 1",
            "descripcion": "Juego de lucha con combates brutales, personajes icónicos, modos competitivos y mucha acción arcade.",
            "precio": Decimal("64.99"),
            "plataforma": "PS5",
            "imagen": "default.jpg",
        },
        {
            "nombre": "NBA 2K25",
            "descripcion": "Simulador de baloncesto con equipos actualizados, modos online y experiencia competitiva enfocada en realismo.",
            "precio": Decimal("59.99"),
            "plataforma": "PS5",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Valorant",
            "descripcion": "Shooter táctico competitivo por equipos con agentes, habilidades únicas y fuerte enfoque en precisión y estrategia.",
            "precio": Decimal("0.00"),
            "plataforma": "PC",
            "imagen": "default.jpg",
        },
        {
            "nombre": "League of Legends",
            "descripcion": "MOBA competitivo con gran variedad de campeones, estrategia en equipo y fuerte escena de esports.",
            "precio": Decimal("0.00"),
            "plataforma": "PC",
            "imagen": "default.jpg",
        },
        {
            "nombre": "Fortnite",
            "descripcion": "Battle royale de ritmo rápido con construcción, eventos en vivo, juego multiplataforma y actualizaciones constantes.",
            "precio": Decimal("0.00"),
            "plataforma": "Multiplataforma",
            "imagen": "default.jpg",
        },
    ]

    juegos_creados = []
    for juego in lista_juegos:
        juegos_creados.append(Juego.objects.create(**juego))

    print(f"[OK] Se cargaron {len(juegos_creados)} juegos correctamente.")


def ejecutar_semilla() -> None:
    """
    Ejecuta la limpieza y recarga completa de la semilla.
    """
    print("=== INICIO DE SEMILLA ===")
    limpiar_tablas_relacionadas()
    cargar_juegos()
    print("=== FIN DE SEMILLA ===")


if __name__ == "__main__":
    ejecutar_semilla()