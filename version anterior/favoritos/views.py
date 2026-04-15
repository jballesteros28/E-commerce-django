from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from catalogo.models import Juego
from .models import Favorito


@login_required
def agregar_a_favoritos(request, id_juego: int):
    if request.method == 'POST':
        juego = get_object_or_404(Juego, id=id_juego)

        favorito, creado = Favorito.objects.get_or_create(
            usuario=request.user,
            juego=juego
        )

        if creado:
            messages.success(request, "Producto agregado a favoritos.")
        else:
            messages.info(request, "Ese producto ya estaba en tus favoritos.")

    return redirect("detalle_producto", id_producto=id_juego)


@login_required
def eliminar_de_favoritos(request, id_juego: int):
    if request.method == 'POST':
        juego = get_object_or_404(Juego, id=id_juego)

        favorito = Favorito.objects.filter(
            usuario=request.user,
            juego=juego
        ).first()

        if favorito:
            favorito.delete()
            messages.success(request, "Producto eliminado de favoritos.")
        else:
            messages.warning(request, "Ese producto no estaba en favoritos.")

    return redirect("ver_favoritos")


@login_required
def ver_favoritos(request, template_name: str = "favoritos/ver_favoritos.html"):
    favoritos = Favorito.objects.filter(usuario=request.user).select_related("juego").order_by("-fecha_agregado")

    data = {
        "favoritos": favoritos
    }
    return render(request, template_name, data)