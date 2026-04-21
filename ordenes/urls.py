from django.urls import path

from ordenes import views

app_name = "ordenes"

urlpatterns = [
    path("crear/", views.crear_orden_view, name="crear"),
    path("mis-ordenes/", views.mis_ordenes_view, name="mis_ordenes"),
    path("<int:orden_id>/", views.detalle_orden_view, name="detalle"),
]