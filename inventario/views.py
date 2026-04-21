from __future__ import annotations

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required, login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from inventario.forms import AjusteInventarioForm, MovimientoInventarioForm
from inventario.models import InventarioProducto
from inventario.services import ajustar_stock, registrar_entrada, registrar_salida


@login_required
@permission_required("inventario.can_manage_inventory", raise_exception=True)
@staff_member_required
def inventario_listado(request, template_name: str="inventario/listado.html"):
    """
    Lista general del inventario.
    """
    inventarios_qs = (
        InventarioProducto.objects.select_related("producto")
        .all()
        .order_by("producto__nombre")
    )
    paginator = Paginator(inventarios_qs,10)
    page_number = request.GET.get('page')
    inventarios = paginator.get_page(page_number)

    context = {
        "inventarios": inventarios,
        "titulo": "Inventario",
    }
    return render(request, template_name, context)


@login_required
@permission_required("inventario.can_manage_inventory", raise_exception=True)
@staff_member_required
def inventario_detalle(request, inventario_id: int, template_name: str="inventario/detalle.html"):
    """
    Muestra el detalle del inventario y su historial.
    """
    inventario = get_object_or_404(
        InventarioProducto.objects.select_related("producto"),
        id=inventario_id,
    )
    movimientos = inventario.movimientos.all()

    context = {
        "inventario": inventario,
        "movimientos": movimientos,
        "titulo": f"Detalle de inventario - {inventario.producto}",
    }
    return render(request, template_name, context)


@login_required
@permission_required("inventario.can_manage_inventory", raise_exception=True)
@staff_member_required
def registrar_entrada_view(request, inventario_id: int, template_name: str="inventario/registrar_entrada.html"):
    """
    Vista para registrar entradas de stock.
    """
    inventario = get_object_or_404(InventarioProducto, id=inventario_id)

    if request.method == "POST":
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            try:
                registrar_entrada(
                    inventario_id=inventario.id,
                    cantidad=form.cleaned_data["cantidad"],
                    motivo=form.cleaned_data["motivo"],
                    referencia_externa=form.cleaned_data["referencia_externa"],
                    creado_por=request.user,
                )
                messages.success(request, "Entrada de stock registrada correctamente.")
                return redirect("inventario:detalle", inventario_id=inventario.id)
            except ValidationError as exc:
                form.add_error(None, exc)

    else:
        form = MovimientoInventarioForm()

    context = {
        "inventario": inventario,
        "form": form,
        "titulo": f"Registrar entrada - {inventario.producto}",
    }
    return render(request, template_name, context)


@login_required
@permission_required("inventario.can_manage_inventory", raise_exception=True)
@staff_member_required
def registrar_salida_view(request, inventario_id: int, template_name: str="inventario/registrar_salida.html"):
    """
    Vista para registrar salidas de stock.
    """
    inventario = get_object_or_404(InventarioProducto, id=inventario_id)

    if request.method == "POST":
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            try:
                registrar_salida(
                    inventario_id=inventario.id,
                    cantidad=form.cleaned_data["cantidad"],
                    motivo=form.cleaned_data["motivo"],
                    referencia_externa=form.cleaned_data["referencia_externa"],
                    creado_por=request.user,
                )
                messages.success(request, "Salida de stock registrada correctamente.")
                return redirect("inventario:detalle", inventario_id=inventario.id)
            except ValidationError as exc:
                form.add_error(None, exc)

    else:
        form = MovimientoInventarioForm()

    context = {
        "inventario": inventario,
        "form": form,
        "titulo": f"Registrar salida - {inventario.producto}",
    }
    return render(request, template_name, context)

@login_required
@permission_required("inventario.can_manage_inventory", raise_exception=True)
@staff_member_required
def ajustar_stock_view(request, inventario_id: int, template_name: str="inventario/ajustar_stock.html"):
    """
    Vista para ajustar el stock a un valor exacto.
    """
    inventario = get_object_or_404(InventarioProducto, id=inventario_id)

    if request.method == "POST":
        form = AjusteInventarioForm(request.POST)
        if form.is_valid():
            try:
                ajustar_stock(
                    inventario_id=inventario.id,
                    nuevo_stock=form.cleaned_data["nuevo_stock"],
                    motivo=form.cleaned_data["motivo"],
                    referencia_externa=form.cleaned_data["referencia_externa"],
                    creado_por=request.user,
                )
                messages.success(request, "Stock ajustado correctamente.")
                return redirect("inventario:detalle", inventario_id=inventario.id)
            except ValidationError as exc:
                form.add_error(None, exc)

    else:
        form = AjusteInventarioForm(
            initial={"nuevo_stock": inventario.stock_actual}
        )

    context = {
        "inventario": inventario,
        "form": form,
        "titulo": f"Ajustar stock - {inventario.producto}",
    }
    return render(request, template_name, context)