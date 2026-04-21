from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from inventario.models import InventarioProducto


Producto = apps.get_model("catalogo", "Juego")


@receiver(post_save, sender=Producto)
def crear_inventario_para_producto(sender, instance, created: bool, **kwargs) -> None:
    """
    Crea el inventario automáticamente al crear un producto.
    """
    if created:
        InventarioProducto.objects.get_or_create(producto=instance)