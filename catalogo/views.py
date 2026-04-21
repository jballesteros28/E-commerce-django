from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from favoritos.models import Favorito
from .models import Juego


def inicio_producto(request, template_name: str = "catalogo/lista_productos.html"):
    try:
        lista_juegos = (
            Juego.objects.select_related("inventario")
            .all()
            .order_by("id")
        )

        page_number = request.GET.get("page")
        paginator = Paginator(lista_juegos, 6)
        page_objeto = paginator.get_page(page_number)

        data = {"productos": page_objeto}
        return render(request, template_name, data)
    except Exception:
        return render(request, template_name="404.html")


def detalle_producto(
    request,
    id_producto: int,
    template_name: str = "catalogo/detalle_producto.html",
):
    juego = get_object_or_404(
        Juego.objects.select_related("inventario"),
        id=id_producto,
    )

    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(
            usuario=request.user,
            juego=juego,
        ).exists()

    data = {
        "producto": juego,
        "es_favorito": es_favorito,
    }
    return render(request, template_name, data)
