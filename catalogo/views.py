from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Juego
from favoritos.models import Favorito


def inicio_producto(request, template_name:str='catalogo/lista_productos.html'):
    try:
        lista_juegos = Juego.objects.all().order_by('id')
        page_number = request.GET.get('page')
        paginator = Paginator(lista_juegos,6)
        page_objeto = paginator.get_page(page_number)
        data = {'productos': page_objeto}
        return render(request, template_name, data)
    except:
        return render(request, template_name='errores/404.html')
    


def detalle_producto(request, id_producto: int, template_name: str = 'catalogo/detalle_producto.html'):
    juego = get_object_or_404(Juego, id=id_producto)

    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(
            usuario=request.user,
            juego=juego
        ).exists()

    data = {
        'producto': juego,
        'es_favorito': es_favorito
    }
    return render(request, template_name, data)
