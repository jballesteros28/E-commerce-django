from django.urls import path

from pagos import views

app_name = "pagos"

urlpatterns = [
    path("iniciar/<int:orden_id>/", views.iniciar_pago_view, name="iniciar"),
    path("resultado/exito/", views.pago_exito_view, name="exito"),
    path("resultado/fallo/", views.pago_fallo_view, name="fallo"),
    path("resultado/pendiente/", views.pago_pendiente_view, name="pendiente"),
    path("webhook/mercadopago/", views.webhook_mercadopago_view, name="webhook_mp"),
]