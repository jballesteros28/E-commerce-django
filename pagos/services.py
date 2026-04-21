from __future__ import annotations

import os

import mercadopago
from django.core.exceptions import ValidationError
from django.db import transaction

from carrito.models import Carrito
from inventario.enums import OrigenMovimientoInventario
from inventario.services import registrar_salida
from ordenes.enums import EstadoOrden
from ordenes.models import Orden
from pagos.enums import EstadoPago
from pagos.models import Pago


def get_mp_client():
    access_token = os.environ.get("MP_ACCESS_TOKEN")
    if not access_token:
        raise ValidationError("No está configurado MP_ACCESS_TOKEN.")
    return mercadopago.SDK(access_token)


@transaction.atomic
def iniciar_pago_para_orden(*, orden, usuario):
    """
    Crea una preferencia de pago para una orden válida,
    bloqueando repagos y reintentos inválidos.
    """
    if orden.usuario != usuario:
        raise ValidationError("No puedes pagar una orden que no te pertenece.")

    # Bloqueo de orden ya pagada
    if orden.estado == EstadoOrden.PAGADA:
        raise ValidationError("Esta orden ya fue pagada y no puede volver a pagarse.")

    # Bloqueo de orden cancelada
    if orden.estado == EstadoOrden.CANCELADA:
        raise ValidationError("Esta orden fue cancelada y no puede pagarse.")

    # Bloqueo de orden en proceso
    if orden.estado == EstadoOrden.EN_PROCESO:
        pago_existente = getattr(orden, "pago", None)

        if pago_existente and pago_existente.init_point:
            raise ValidationError(
                "Esta orden ya tiene un pago en proceso. "
                "Espera la confirmación o revisa su estado."
            )

        raise ValidationError("Esta orden ya tiene un pago en proceso.")

    # Solo permitimos pago en PENDIENTE o FALLIDA
    if orden.estado not in {EstadoOrden.PENDIENTE, EstadoOrden.FALLIDA}:
        raise ValidationError("Esta orden no está en un estado válido para pagar.")

    if not orden.items.exists():
        raise ValidationError("La orden no tiene productos.")

    if orden.total <= 0:
        raise ValidationError("La orden no tiene un total válido.")

    pago_existente = getattr(orden, "pago", None)

    # Si ya tiene pago aprobado, bloquear totalmente
    if pago_existente and pago_existente.estado == EstadoPago.APROBADO:
        raise ValidationError("Esta orden ya tiene un pago aprobado.")

    # Si el pago sigue pendiente y la orden está fallida por inconsistencia, también bloqueamos
    if pago_existente and pago_existente.estado == EstadoPago.PENDIENTE and orden.estado == EstadoOrden.EN_PROCESO:
        raise ValidationError(
            "Ya existe un intento de pago activo para esta orden."
        )

    client = get_mp_client()
    base_url = os.environ.get("MP_BASE_URL", "").rstrip("/")

    if not base_url:
        raise ValidationError("No está configurado MP_BASE_URL.")

    items = []
    for item in orden.items.all():
        inventario = getattr(item.juego, "inventario", None)
        if inventario is None:
            raise ValidationError(f"'{item.nombre_producto}' no tiene inventario.")

        if item.cantidad > inventario.stock_disponible:
            raise ValidationError(
                f"No hay stock suficiente para '{item.nombre_producto}'."
            )

        items.append(
            {
                "title": item.nombre_producto,
                "quantity": item.cantidad,
                "currency_id": "ARS",
                "unit_price": float(item.precio_unitario),
            }
        )

    preference_data = {
        "items": items,
        "external_reference": orden.referencia,
        "back_urls": {
            "success": f"{base_url}/pagos/resultado/exito/?ref={orden.referencia}",
            "failure": f"{base_url}/pagos/resultado/fallo/?ref={orden.referencia}",
            "pending": f"{base_url}/pagos/resultado/pendiente/?ref={orden.referencia}",
        },
        "auto_return": "approved",
        "notification_url": f"{base_url}/pagos/webhook/mercadopago/",
    }

    response = client.preference().create(preference_data)
    data = response.get("response", {})

    if "id" not in data or "init_point" not in data:
        raise ValidationError("No se pudo crear la preferencia de pago.")

    pago, _ = Pago.objects.get_or_create(
        orden=orden,
        defaults={
            "monto": orden.total,
        },
    )

    pago.estado = EstadoPago.PENDIENTE
    pago.monto = orden.total
    pago.preference_id = data.get("id")
    pago.init_point = data.get("init_point")
    pago.raw_response = data
    pago.save()

    orden.estado = EstadoOrden.EN_PROCESO
    orden.save(update_fields=["estado", "updated_at"])

    return pago


def obtener_pago_mp(payment_id: str | int) -> dict:
    """
    Consulta el pago real en Mercado Pago usando el payment_id.
    """
    client = get_mp_client()
    response = client.payment().get(payment_id)
    data = response.get("response", {})

    if not data or "id" not in data:
        raise ValidationError("No se pudo obtener el pago desde Mercado Pago.")

    return data


def mapear_estado_mp_a_local(estado_mp: str) -> str:
    """
    Convierte el estado externo de Mercado Pago a estado local.
    """
    estado_mp = (estado_mp or "").lower()

    if estado_mp == "approved":
        return EstadoPago.APROBADO

    if estado_mp in {"pending", "in_process", "authorized"}:
        return EstadoPago.PENDIENTE

    if estado_mp == "rejected":
        return EstadoPago.RECHAZADO

    if estado_mp == "cancelled":
        return EstadoPago.CANCELADO

    if estado_mp in {"refunded", "charged_back"}:
        return EstadoPago.CANCELADO

    return EstadoPago.ERROR


def vaciar_carrito_usuario(usuario) -> None:
    """
    Vacía el carrito del usuario después de un pago aprobado.
    """
    carrito = Carrito.objects.filter(usuario=usuario).first()
    if carrito:
        carrito.items.all().delete()


@transaction.atomic
def procesar_pago_aprobado(*, pago: Pago, data_mp: dict) -> None:
    """
    Procesa un pago aprobado de forma idempotente:
    - valida referencia externa
    - valida monto
    - valida stock
    - descuenta stock
    - marca pago y orden como aprobados
    - vacía carrito
    """
    orden = (
        Orden.objects.select_for_update()
        .prefetch_related("items__juego__inventario")
        .get(id=pago.orden_id)
    )

    # Idempotencia: si ya está procesado, salimos
    if orden.estado == EstadoOrden.PAGADA and pago.estado == EstadoPago.APROBADO:
        return

    monto_mp = data_mp.get("transaction_amount")
    external_reference = data_mp.get("external_reference")
    payment_id = data_mp.get("id")

    if external_reference != orden.referencia:
        raise ValidationError("La referencia externa del pago no coincide con la orden.")

    if monto_mp is None:
        raise ValidationError("Mercado Pago no devolvió transaction_amount.")

    if float(orden.total) != float(monto_mp):
        raise ValidationError("El monto pagado no coincide con el total de la orden.")

    # Validar stock antes de descontar
    for item in orden.items.all():
        inventario = getattr(item.juego, "inventario", None)

        if inventario is None:
            raise ValidationError(
                f"El producto '{item.nombre_producto}' no tiene inventario."
            )

        if item.cantidad > inventario.stock_disponible:
            raise ValidationError(
                f"No hay stock suficiente para descontar '{item.nombre_producto}'."
            )

    # Descontar stock
    for item in orden.items.all():
        registrar_salida(
            inventario_id=item.juego.inventario.id,
            cantidad=item.cantidad,
            motivo=f"Venta confirmada - Orden {orden.referencia}",
            creado_por=None,
            origen=OrigenMovimientoInventario.PEDIDO,
            referencia_externa=orden.referencia,
        )

    pago.estado = EstadoPago.APROBADO
    pago.external_id = str(payment_id)
    pago.raw_response = data_mp
    pago.save(update_fields=["estado", "external_id", "raw_response", "updated_at"])

    orden.estado = EstadoOrden.PAGADA
    orden.save(update_fields=["estado", "updated_at"])

    vaciar_carrito_usuario(orden.usuario)


@transaction.atomic
def procesar_pago_no_aprobado(*, pago: Pago, data_mp: dict) -> None:
    """
    Actualiza estados locales para pagos no aprobados.
    """
    estado_local = mapear_estado_mp_a_local(data_mp.get("status"))

    pago.estado = estado_local
    pago.external_id = str(data_mp.get("id")) if data_mp.get("id") else pago.external_id
    pago.raw_response = data_mp
    pago.save(update_fields=["estado", "external_id", "raw_response", "updated_at"])

    orden = Orden.objects.select_for_update().get(id=pago.orden_id)

    if estado_local == EstadoPago.RECHAZADO:
        orden.estado = EstadoOrden.FALLIDA
    elif estado_local == EstadoPago.CANCELADO:
        orden.estado = EstadoOrden.CANCELADA
    else:
        orden.estado = EstadoOrden.EN_PROCESO

    orden.save(update_fields=["estado", "updated_at"])