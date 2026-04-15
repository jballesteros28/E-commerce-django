from django.urls import path
from . import views

urlpatterns= [
    path('registro_usuario', views.registrar_usuario, name='registro_usuario'),
    path('login_usuario', views.login_usuario, name='login_usuario'),
    path('logout_usuario', views.logout_usuario, name='logout_usuario'),
    path('perfil_usuario', views.perfil_usuario, name='perfil_usuario'),
    path('editar_usuario', views.editar_usuario, name='editar_usuario'),
    path('cambiar_password', views.cambiar_password, name='cambiar_password'),
]