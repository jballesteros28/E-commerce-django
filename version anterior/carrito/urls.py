from django.urls import path
from . import views

urlpatterns= [
    path('', views.ver_carrito, name='ver_carrito'),
    path('agregar_al_carrito/<int:id_juego>', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar_del_carrito/<int:id_juego>', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('limpiar_carrito', views.limpiar_carrito, name='limpiar_carrito')
]