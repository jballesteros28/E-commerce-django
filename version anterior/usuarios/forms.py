from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import Usuario


class UserRegisterForm(UserCreationForm):
    class Meta:
        model= Usuario
        fields= ['username','email','password1','password2']
        
        
class LoginUserForm(AuthenticationForm):
    pass


class UserEditForm(forms.ModelForm):
    """
    Formulario para editar datos básicos del usuario.
    No incluye contraseña porque eso debe ir en otro flujo separado.
    """
    class Meta:
        model = Usuario
        fields = ["username", "email"]