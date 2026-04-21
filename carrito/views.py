from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from catalogo.models import Juego
from .models import Carrito, ItemCarrito


@login_required
def agregar_al_carrito(request, id_juego: int):
    juego = get_object_or_404(
        Juego.objects.select_related("inventario"),
        id=id_juego,
    )

    inventario = getattr(juego, "inventario", None)

    if inventario is None:
        messages.error(request, "Este producto no tiene inventario configurado.")
        return redirect("detalle_producto", id_producto=id_juego)

    if not inventario.activo_para_venta:
        messages.error(request, "Este producto no está disponible para la venta.")
        return redirect("detalle_producto", id_producto=id_juego)

    if inventario.stock_disponible <= 0:
        messages.error(request, "Sin stock temporalmente para este producto.")
        return redirect("detalle_producto", id_producto=id_juego)

    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        juego=juego,
    )

    cantidad_actual = item.cantidad if not creado else 0

    if cantidad_actual + 1 > inventario.stock_disponible:
        messages.error(
            request,
            f"No puedes agregar más unidades de '{juego.nombre}'. "
            f"Stock disponible: {inventario.stock_disponible}.",
        )
        return redirect("detalle_producto", id_producto=id_juego)

    if not creado:
        item.cantidad += 1
        item.save()
        messages.info(
            request,
            f"Se ha aumentado la cantidad de {juego.nombre} en el carrito.",
        )
        return redirect("ver_carrito")

    messages.success(request, f"Producto '{juego.nombre}' añadido al carrito.")
    item.save()
    return redirect("detalle_producto", id_producto=id_juego)


@login_required
def ver_carrito(request, template_name: str = "carrito/ver_carrito.html"):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related("juego")
    total = carrito.total_precio()

    data = {
        "carrito": carrito,
        "items": items,
        "total": total,
    }
    return render(request, template_name, data)


@login_required
def eliminar_del_carrito(request, id_juego: int):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    item = carrito.items.filter(juego_id=id_juego).first()

    if not item:
        messages.error(request, "El producto no existe en el carrito.")
        return redirect("ver_carrito")

    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
        messages.info(request, f"Se ha restado una unidad de '{item.juego.nombre}'")
    else:
        nombre_juego = item.juego.nombre
        item.delete()
        messages.error(request, f"Producto '{nombre_juego}' eliminado del carrito")

    return redirect("ver_carrito")


@login_required
def limpiar_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    if carrito.items.exists():
        carrito.items.all().delete()
        messages.warning(request, "Se han eliminado todos los productos del carrito")
    else:
        messages.info(request, "El carrito ya estaba vacío")
    return redirect("ver_carrito")