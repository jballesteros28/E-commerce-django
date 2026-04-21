from django.urls import path

from inventario import views

app_name = "inventario"

urlpatterns = [
    path("", views.inventario_listado, name="listado"),
    path("<int:inventario_id>/", views.inventario_detalle, name="detalle"),
    path("<int:inventario_id>/entrada/", views.registrar_entrada_view, name="entrada"),
    path("<int:inventario_id>/salida/", views.registrar_salida_view, name="salida"),
    path("<int:inventario_id>/ajustar/", views.ajustar_stock_view, name="ajustar"),
]