from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalogo.models import Juego
from .models import Carrito, ItemCarrito

@login_required
def agregar_al_carrito(request, id_juego: int):
    juego = get_object_or_404(Juego, id=id_juego)
    carrito, _ = Carrito.objects.get_or_create(usuario= request.user)
    item, creado = ItemCarrito.objects.get_or_create(carrito=carrito,juego=juego)
    if not creado:
        item.cantidad += 1
        messages.info(request, f"Se ha aumentado la cantidad de {juego.nombre} en el carrito")
        item.save()
        return redirect('ver_carrito')
    else:
        messages.success(request, f"Producto '{juego.nombre}' añadido al carrito")
    item.save()
    return redirect('detalle_producto', id_producto=id_juego)


@login_required
def ver_carrito(request, template_name:str='carrito/ver_carrito.html'):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related('juego')
    total = carrito.total_precio()
    data = {'carrito': carrito,
            'items': items,
            'total': total}
    return render(request, template_name, data)

@login_required
def eliminar_del_carrito(request, id_juego: int):
    carrito , _ = Carrito.objects.get_or_create(usuario=request.user)
    item = carrito.items.filter(juego_id=id_juego).first()
    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
        messages.info(request, f"Se ha restado una unidad de '{item.juego.nombre}'")
    else:
        item.delete()
        messages.error(request, f"Producto '{item.juego.nombre}' eliminado del carrito")
    return redirect('ver_carrito')


@login_required
def limpiar_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    if carrito.items.exists():
        carrito.items.all().delete()
        messages.warning(request, "Se han eliminado todos los productos del carrito")
    else:
        messages.info(request, "El carrito ya estaba vacio")
    return redirect('ver_carrito')