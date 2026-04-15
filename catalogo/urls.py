from django.urls import path
from . import views

urlpatterns= [
    path('', views.inicio_producto, name='inicio_producto'),
    path('detalle_producto/<int:id_producto>', views.detalle_producto, name='detalle_producto')
]