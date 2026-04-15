from django.urls import path
from . import views

urlpatterns= [
  path('', views.index, name='home'),
  path('cambiar-tema/', views.cambiar_tema, name='cambiar_tema'),
]