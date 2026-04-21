from __future__ import annotations

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from inventario.forms import (
    AjusteInventarioForm,
    AjusteStockMinimoForm,
    LiberarReservaStockForm,
    MovimientoInventarioForm,
    ReservaStockForm,
)
from inventario.models import InventarioProducto
from inventario.services import (
    ajustar_stock,
    ajustar_stock_minimo,
    liberar_stock_reservado,
    registrar_entrada,
    registrar_salida,
    reservar_stock,
)


@login_required
@permission_required("inventario.can_manage_inventory", raise_exception=True)
@staff_member_required
def inventario_listado(request, template_name: str = "inventario/listado.html"):
    inventarios_qs = (
        InventarioProducto.objects.select_related("producto")
        .all()
        .order_by("producto__nombre")
    )
    paginator = Paginator(inventarios_qs, 10)
    page_number = request.GET.get("page")
    inventarios = paginator.get_page(page_number)

    context = {
        "inventarios": inventarios,
        "titulo": "Inventario",
    }
    return render(request, template_name, context)


@login_required
@permission_required("inventario.can_manage_inventory", raise_exception=True)
@staff_member_required
def inventario_detalle(request, inventario_id: int, template_name: str = "inventario/detalle.html"):
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
def registrar_entrada_view(request, inventario_id: int, template_name: str = "inventario/registrar_entrada.html"):
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
def registrar_salida_view(request, inventario_id: int, template_name: str = "inventario/registrar_salida.html"):
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
def ajustar_stock_view(request, inventario_id: int, template_name: str = "inventario/ajustar_stock.html"):
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
        form = AjusteInventarioForm(initial={"nuevo_stock": inventario.stock_actual})

    context = {
        "inventario": inventario,
        "form": form,
        "titulo": f"Ajustar stock - {inventario.producto}",
    }
    return render(request, template_name, context)


@login_required
@permission_required("inventario.can_manage_inventory", raise_exception=True)
@staff_member_required
def ajustar_stock_minimo_view(request, inventario_id: int, template_name: str = "inventario/ajustar_stock_minimo.html"):
    inventario = get_object_or_404(InventarioProducto, id=inventario_id)

    if request.method == "POST":
        form = AjusteStockMinimoForm(request.POST)
        if form.is_valid():
            try:
                ajustar_stock_minimo(
                    inventario_id=inventario.id,
                    nuevo_stock_minimo=form.cleaned_data["nuevo_stock_minimo"],
                    motivo=form.cleaned_data["motivo"],
                    creado_por=request.user,
                )
                messages.success(request, "Stock mínimo ajustado correctamente.")
                return redirect("inventario:detalle", inventario_id=inventario.id)
            except ValidationError as exc:
                form.add_error(None, exc)
    else:
        form = AjusteStockMinimoForm(initial={"nuevo_stock_minimo": inventario.stock_minimo})

    context = {
        "inventario": inventario,
        "form": form,
        "titulo": f"Ajustar stock mínimo - {inventario.producto}",
    }
    return render(request, template_name, context)


@login_required
@permission_required("inventario.can_manage_inventory", raise_exception=True)
@staff_member_required
def reservar_stock_view(request, inventario_id: int, template_name: str = "inventario/reservar_stock.html"):
    inventario = get_object_or_404(InventarioProducto, id=inventario_id)

    if request.method == "POST":
        form = ReservaStockForm(request.POST)
        if form.is_valid():
            try:
                reservar_stock(
                    inventario_id=inventario.id,
                    cantidad=form.cleaned_data["cantidad"],
                    motivo=form.cleaned_data["motivo"],
                    referencia_externa=form.cleaned_data["referencia_externa"],
                    creado_por=request.user,
                )
                messages.success(request, "Stock reservado correctamente.")
                return redirect("inventario:detalle", inventario_id=inventario.id)
            except ValidationError as exc:
                form.add_error(None, exc)
    else:
        form = ReservaStockForm()

    context = {
        "inventario": inventario,
        "form": form,
        "titulo": f"Reservar stock - {inventario.producto}",
    }
    return render(request, template_name, context)


@login_required
@permission_required("inventario.can_manage_inventory", raise_exception=True)
@staff_member_required
def liberar_reserva_stock_view(request, inventario_id: int, template_name: str = "inventario/liberar_reserva.html"):
    inventario = get_object_or_404(InventarioProducto, id=inventario_id)

    if request.method == "POST":
        form = LiberarReservaStockForm(request.POST)
        if form.is_valid():
            try:
                liberar_stock_reservado(
                    inventario_id=inventario.id,
                    cantidad=form.cleaned_data["cantidad"],
                    motivo=form.cleaned_data["motivo"],
                    referencia_externa=form.cleaned_data["referencia_externa"],
                    creado_por=request.user,
                )
                messages.success(request, "Reserva liberada correctamente.")
                return redirect("inventario:detalle", inventario_id=inventario.id)
            except ValidationError as exc:
                form.add_error(None, exc)
    else:
        form = LiberarReservaStockForm()

    context = {
        "inventario": inventario,
        "form": form,
        "titulo": f"Liberar reserva - {inventario.producto}",
    }
    return render(request, template_name, context)