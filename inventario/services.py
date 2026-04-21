from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from inventario.enums import OrigenMovimientoInventario, TipoMovimientoInventario
from inventario.models import InventarioProducto, MovimientoInventario

User = get_user_model()


@dataclass(frozen=True)
class ResultadoMovimientoInventario:
    """
    Resultado estructurado de una operación de inventario.
    """

    inventario: InventarioProducto
    movimiento: MovimientoInventario


def _validar_cantidad(cantidad: int) -> None:
    """
    Valida que la cantidad sea válida.
    """
    if cantidad <= 0:
        raise ValidationError({"cantidad": "La cantidad debe ser mayor a cero."})


def _obtener_inventario_bloqueado(inventario_id: int) -> InventarioProducto:
    """
    Obtiene el inventario con bloqueo de fila para evitar
    inconsistencias en operaciones concurrentes.
    """
    return InventarioProducto.objects.select_for_update().select_related("producto").get(
        id=inventario_id
    )


@transaction.atomic
def registrar_entrada(
    *,
    inventario_id: int,
    cantidad: int,
    motivo: str,
    creado_por: Optional[User] = None,
    origen: str = OrigenMovimientoInventario.ADMIN,
    referencia_externa: Optional[str] = None,
) -> ResultadoMovimientoInventario:
    """
    Registra una entrada de stock.
    """
    _validar_cantidad(cantidad)

    inventario = _obtener_inventario_bloqueado(inventario_id)

    stock_anterior = inventario.stock_actual
    stock_posterior = stock_anterior + cantidad

    inventario.stock_actual = stock_posterior
    inventario.full_clean()
    inventario.save(update_fields=["stock_actual", "updated_at"])

    movimiento = MovimientoInventario.objects.create(
        inventario=inventario,
        tipo_movimiento=TipoMovimientoInventario.ENTRADA,
        origen=origen,
        cantidad=cantidad,
        stock_anterior=stock_anterior,
        stock_posterior=stock_posterior,
        motivo=motivo,
        referencia_externa=referencia_externa,
        creado_por=creado_por,
    )
    movimiento.full_clean()

    return ResultadoMovimientoInventario(
        inventario=inventario,
        movimiento=movimiento,
    )


@transaction.atomic
def registrar_salida(
    *,
    inventario_id: int,
    cantidad: int,
    motivo: str,
    creado_por: Optional[User] = None,
    origen: str = OrigenMovimientoInventario.ADMIN,
    referencia_externa: Optional[str] = None,
) -> ResultadoMovimientoInventario:
    """
    Registra una salida de stock validando disponibilidad real.
    """
    _validar_cantidad(cantidad)

    inventario = _obtener_inventario_bloqueado(inventario_id)

    if not inventario.activo_para_venta:
        raise ValidationError(
            {"activo_para_venta": "El producto no está activo para operaciones de stock."}
        )

    if cantidad > inventario.stock_disponible:
        raise ValidationError(
            {
                "cantidad": (
                    "No hay stock disponible suficiente para registrar esta salida."
                )
            }
        )

    stock_anterior = inventario.stock_actual
    stock_posterior = stock_anterior - cantidad

    inventario.stock_actual = stock_posterior
    inventario.full_clean()
    inventario.save(update_fields=["stock_actual", "updated_at"])

    movimiento = MovimientoInventario.objects.create(
        inventario=inventario,
        tipo_movimiento=TipoMovimientoInventario.SALIDA,
        origen=origen,
        cantidad=cantidad,
        stock_anterior=stock_anterior,
        stock_posterior=stock_posterior,
        motivo=motivo,
        referencia_externa=referencia_externa,
        creado_por=creado_por,
    )
    movimiento.full_clean()

    return ResultadoMovimientoInventario(
        inventario=inventario,
        movimiento=movimiento,
    )


@transaction.atomic
def ajustar_stock(
    *,
    inventario_id: int,
    nuevo_stock: int,
    motivo: str,
    creado_por: Optional[User] = None,
    referencia_externa: Optional[str] = None,
) -> ResultadoMovimientoInventario:
    """
    Ajusta el stock al valor exacto indicado.

    Si el nuevo stock es mayor al actual, se registra como ajuste positivo.
    Si es menor, como ajuste negativo.
    """
    if nuevo_stock < 0:
        raise ValidationError({"nuevo_stock": "El nuevo stock no puede ser negativo."})

    inventario = _obtener_inventario_bloqueado(inventario_id)

    stock_anterior = inventario.stock_actual

    if nuevo_stock == stock_anterior:
        raise ValidationError(
            {"nuevo_stock": "El nuevo stock es igual al stock actual. No hay cambios."}
        )

    diferencia = abs(nuevo_stock - stock_anterior)

    if nuevo_stock > stock_anterior:
        tipo_movimiento = TipoMovimientoInventario.AJUSTE_POSITIVO
    else:
        if nuevo_stock < inventario.stock_reservado:
            raise ValidationError(
                {
                    "nuevo_stock": (
                        "El nuevo stock no puede quedar por debajo del stock reservado."
                    )
                }
            )
        tipo_movimiento = TipoMovimientoInventario.AJUSTE_NEGATIVO

    inventario.stock_actual = nuevo_stock
    inventario.full_clean()
    inventario.save(update_fields=["stock_actual", "updated_at"])

    movimiento = MovimientoInventario.objects.create(
        inventario=inventario,
        tipo_movimiento=tipo_movimiento,
        origen=OrigenMovimientoInventario.AJUSTE,
        cantidad=diferencia,
        stock_anterior=stock_anterior,
        stock_posterior=nuevo_stock,
        motivo=motivo,
        referencia_externa=referencia_externa,
        creado_por=creado_por,
    )
    movimiento.full_clean()

    return ResultadoMovimientoInventario(
        inventario=inventario,
        movimiento=movimiento,
    )