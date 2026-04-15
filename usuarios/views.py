from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserRegisterForm, LoginUserForm, UserEditForm
from django.contrib import messages



def registrar_usuario(request, template_name:str='usuarios/registro_usuario.html'):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            usuario_nuevo = form.save(commit=True)
            login(request, usuario_nuevo)
            messages.success(request, "Registro completado correctamente.")
            return redirect('home')
    else:
        form = UserRegisterForm()
    data = {'form': form,
            'accion': 'Registrar usuario'}
    return render(request, template_name, data)

def login_usuario(request, template_name:str='usuarios/login_usuario.html'):
    if request.method == 'POST':
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            messages.success(request, "Inicio de sesión correcto.")
            return redirect('home')
        else:
            messages.error(request, 'Credenciales invalidas')
    else:
        form = LoginUserForm()
    data = {'form': form}
    return render(request, template_name, data)


def logout_usuario(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login_usuario')


@login_required
def perfil_usuario(request,template_name:str='usuarios/perfil_usuario.html'):
    return render(request, template_name)



@login_required
def editar_usuario(request,template_name:str='usuarios/editar_usuario.html'):
    usuario = request.user
    if request.method == 'POST':
        form = UserEditForm(request.POST or None, instance=usuario )
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, "Cambios completados correctamente.")
            return redirect('perfil_usuario')
    else:
        form = UserEditForm(instance=usuario)
    data = {'form': form,
            'accion': 'Modificar Usuario'}
    return render(request, template_name, data)


@login_required
def cambiar_password(request, template_name: str='usuarios/cambiar_password.html'):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            usuario = form.save()
            update_session_auth_hash(request,usuario)
            messages.success(request, "La contraseña se actualizo correctamente")
            return redirect('perfil_usuario')
    else:
        form = PasswordChangeForm(user=request.user)
        
    data = {'form': form,
            'accion': 'Cambiar contraseña'}
    return render(request, template_name, data)