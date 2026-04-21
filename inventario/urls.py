from django.urls import path

from inventario import views

app_name = "inventario"

urlpatterns = [
    path("", views.inventario_listado, name="listado"),
    path("<int:inventario_id>/", views.inventario_detalle, name="detalle"),
    path("<int:inventario_id>/entrada/", views.registrar_entrada_view, name="entrada"),
    path("<int:inventario_id>/salida/", views.registrar_salida_view, name="salida"),
    path("<int:inventario_id>/ajustar/", views.ajustar_stock_view, name="ajustar"),
    path("<int:inventario_id>/stock-minimo/", views.ajustar_stock_minimo_view, name="stock_minimo"),
    path("<int:inventario_id>/reservar/", views.reservar_stock_view, name="reservar"),
    path("<int:inventario_id>/liberar-reserva/", views.liberar_reserva_stock_view, name="liberar_reserva"),
]