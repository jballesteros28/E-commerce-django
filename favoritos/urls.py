from django.urls import path
from . import views

urlpatterns = [
    path("", views.ver_favoritos, name="ver_favoritos"),
    path("agregar_a_favoritos/<int:id_juego>", views.agregar_a_favoritos, name="agregar_a_favoritos"),
    path("eliminar_de_favoritos/<int:id_juego>", views.eliminar_de_favoritos, name="eliminar_de_favoritos"),
]