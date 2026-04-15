from django.shortcuts import render
from catalogo.models import Juego
from django.core.paginator import Paginator
from django.db.models import Q


def buscar_juegos(request, template_name:str='buscador/resultados_busqueda.html'):
    try:
        query = request.GET.get('q','')

        resultados = Juego.objects.filter(
          Q(nombre__icontains=query) | Q(plataforma__icontains=query)
          ).order_by('id')
        
        paginator = Paginator(resultados, 6)
        page_number = request.GET.get('page')
        page_objeto = paginator.get_page(page_number)

        data = {
          'query': query,
          'resultados': page_objeto
        }
        
        return render(request, template_name, data)
    except:
        return render(request, template_name='errores/404.html')