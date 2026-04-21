from __future__ import annotations
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from ordenes.models import Orden
from pagos.models import Pago, WebhookPagoLog
from pagos.services import (
    iniciar_pago_para_orden,
    mapear_estado_mp_a_local,
    obtener_pago_mp,
    procesar_pago_aprobado,
    procesar_pago_no_aprobado,
)


@login_required
def iniciar_pago_view(request: HttpRequest, orden_id: int):
    """
    Inicia el flujo de pago para una orden del usuario autenticado.
    """
    orden = get_object_or_404(
        Orden.objects.prefetch_related("items__juego"),
        id=orden_id,
        usuario=request.user,
    )

    try:
        pago = iniciar_pago_para_orden(orden=orden, usuario=request.user)
        return redirect(pago.init_point)
    except ValidationError as exc:
        messages.error(request, exc.message)
        return redirect("ordenes:detalle", orden_id=orden.id)


def pago_exito_view(request: HttpRequest, template_name: str = "pagos/exito.html"):
    return render(request, template_name)


def pago_fallo_view(request: HttpRequest, template_name: str = "pagos/fallo.html"):
    return render(request, template_name)


def pago_pendiente_view(request: HttpRequest, template_name: str = "pagos/pendiente.html"):
    return render(request, template_name)


@csrf_exempt
def webhook_mercadopago_view(request: HttpRequest):
    """
    Recibe la notificación de Mercado Pago y procesa el pago real.

    Flujo:
    - obtener payment_id desde query params
    - consultar el pago real en MP
    - buscar la orden por external_reference
    - crear/actualizar el pago local
    - si está aprobado: marcar orden pagada, descontar stock y vaciar carrito
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido"}, status=405)

    log = WebhookPagoLog.objects.create(
        payload={},
        query_params=dict(request.GET),
        headers={k: v for k, v in request.headers.items()},
        procesado=False,
    )

    # Mercado Pago suele enviar data.id o id en la query
    payment_id = request.GET.get("data.id") or request.GET.get("id")

    if not payment_id:
        log.detalle = "Webhook ignorado: missing payment id"
        log.procesado = True
        log.save(update_fields=["detalle", "procesado"])
        return JsonResponse(
            {"status": "ignored", "reason": "missing payment id"},
            status=200,
        )

    try:
        data_mp = obtener_pago_mp(payment_id)
        log.payload = data_mp
        log.save(update_fields=["payload"])

        external_reference = data_mp.get("external_reference")

        if not external_reference:
            log.detalle = "Webhook ignorado: missing external_reference"
            log.procesado = True
            log.save(update_fields=["detalle", "procesado"])
            return JsonResponse(
                {"status": "ignored", "reason": "missing external_reference"},
                status=200,
            )

        orden = Orden.objects.filter(referencia=external_reference).first()
        if orden is None:
            log.detalle = f"Webhook ignorado: order not found ({external_reference})"
            log.procesado = True
            log.save(update_fields=["detalle", "procesado"])
            return JsonResponse(
                {"status": "ignored", "reason": "order not found"},
                status=200,
            )

        pago, _ = Pago.objects.get_or_create(
            orden=orden,
            defaults={
                "monto": orden.total,
                "moneda": "ARS",
            },
        )

        estado_local = mapear_estado_mp_a_local(data_mp.get("status"))

        if estado_local == "APROBADO":
            procesar_pago_aprobado(pago=pago, data_mp=data_mp)
            log.detalle = f"Pago aprobado procesado para orden {orden.referencia}"
        else:
            procesar_pago_no_aprobado(pago=pago, data_mp=data_mp)
            log.detalle = (
                f"Pago no aprobado procesado para orden {orden.referencia} "
                f"(estado local: {estado_local})"
            )

        log.procesado = True
        log.save(update_fields=["detalle", "procesado"])

        return JsonResponse({"status": "ok"}, status=200)

    except Exception as exc:
        log.detalle = f"Error procesando webhook: {str(exc)}"
        log.procesado = False
        log.save(update_fields=["detalle", "procesado"])

        return JsonResponse(
            {"status": "error", "detail": str(exc)},
            status=500,
        )