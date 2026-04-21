from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import transaction

from carrito.models import Carrito
from inventario.models import InventarioProducto
from ordenes.models import Orden, OrdenItem


@dataclass(frozen=True)
class ResultadoCreacionOrden:
    """
    Resultado estructurado de la creación de una orden.
    """

    orden: Orden


def generar_referencia_orden() -> str:
    """
    Genera una referencia única y legible para la orden.
    """
    return f"ORD-{uuid4().hex[:10].upper()}"


@transaction.atomic
def crear_orden_desde_carrito(*, usuario) -> ResultadoCreacionOrden:
    """
    Crea una orden a partir del carrito actual del usuario.

    Flujo:
    - valida que exista carrito
    - valida que tenga items
    - valida stock real para cada producto
    - crea orden e items
    - calcula totales
    """
    carrito = (
        Carrito.objects.select_related("usuario")
        .prefetch_related("items__juego")
        .filter(usuario=usuario)
        .first()
    )

    if carrito is None:
        raise ValidationError("El usuario no tiene carrito.")

    items_carrito = list(carrito.items.select_related("juego"))

    if not items_carrito:
        raise ValidationError("No se puede crear una orden con el carrito vacío.")

    subtotal_orden = Decimal("0.00")

    # Validación de inventario antes de crear la orden
    inventarios_bloqueados: dict[int, InventarioProducto] = {}

    for item in items_carrito:
        inventario = (
            InventarioProducto.objects.select_for_update()
            .select_related("producto")
            .filter(producto=item.juego)
            .first()
        )

        if inventario is None:
            raise ValidationError(
                f"El producto '{item.juego.nombre}' no tiene inventario configurado."
            )

        if not inventario.activo_para_venta:
            raise ValidationError(
                f"El producto '{item.juego.nombre}' no está activo para la venta."
            )

        if item.cantidad > inventario.stock_disponible:
            raise ValidationError(
                f"No hay stock suficiente para '{item.juego.nombre}'. "
                f"Disponible: {inventario.stock_disponible}."
            )

        inventarios_bloqueados[item.juego.id] = inventario

    orden = Orden.objects.create(
        usuario=usuario,
        referencia=generar_referencia_orden(),
        subtotal=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    for item in items_carrito:
        precio_unitario = item.juego.precio
        subtotal_item = precio_unitario * item.cantidad

        orden_item = OrdenItem(
            orden=orden,
            juego=item.juego,
            nombre_producto=item.juego.nombre,
            precio_unitario=precio_unitario,
            cantidad=item.cantidad,
            subtotal=subtotal_item,
        )
        orden_item.full_clean()
        orden_item.save()

        subtotal_orden += subtotal_item

    orden.subtotal = subtotal_orden
    orden.total = subtotal_orden
    orden.full_clean()
    orden.save(update_fields=["subtotal", "total", "updated_at"])

    return ResultadoCreacionOrden(orden=orden)