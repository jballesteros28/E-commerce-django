from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from ordenes.models import Orden
from ordenes.services import crear_orden_desde_carrito


@login_required
def crear_orden_view(request):
    """
    Crea una orden a partir del carrito del usuario autenticado.
    """
    try:
        resultado = crear_orden_desde_carrito(usuario=request.user)
        messages.success(request, "La orden fue creada correctamente.")
        return redirect("ordenes:detalle", orden_id=resultado.orden.id)
    except ValidationError as exc:
        messages.error(request, str(exc))
        return redirect("ver_carrito")


@login_required
def mis_ordenes_view(request, template_name:str='ordenes/mis_ordenes.html'):
    """
    Lista de órdenes del usuario.
    """
    ordenes = (
        Orden.objects.filter(usuario=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )

    context = {
        "ordenes": ordenes,
        "titulo": "Mis órdenes",
    }
    return render(request, template_name, context)


@login_required
def detalle_orden_view(request, orden_id: int, template_name:str='ordenes/detalle_orden.html'):
    """
    Detalle de una orden del usuario.
    """
    orden = get_object_or_404(
        Orden.objects.prefetch_related("items"),
        id=orden_id,
        usuario=request.user,
    )

    context = {
        "orden": orden,
        "titulo": f"Detalle de orden {orden.referencia}",
    }
    return render(request, template_name, context)