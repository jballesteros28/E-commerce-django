from __future__ import annotations

from django import forms


class MovimientoInventarioForm(forms.Form):
    """
    Formulario base para entradas y salidas.
    """

    cantidad = forms.IntegerField(
        min_value=1,
        label="Cantidad",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese una cantidad",
            }
        ),
    )
    motivo = forms.CharField(
        max_length=255,
        label="Motivo",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: reposición, rotura, ajuste, etc.",
            }
        ),
    )
    referencia_externa = forms.CharField(
        max_length=100,
        required=False,
        label="Referencia externa",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: pedido #123",
            }
        ),
    )


class AjusteInventarioForm(forms.Form):
    """
    Formulario para ajustar el stock a un valor exacto.
    """

    nuevo_stock = forms.IntegerField(
        min_value=0,
        label="Nuevo stock",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese el nuevo stock total",
            }
        ),
    )
    motivo = forms.CharField(
        max_length=255,
        label="Motivo",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Motivo del ajuste",
            }
        ),
    )
    referencia_externa = forms.CharField(
        max_length=100,
        required=False,
        label="Referencia externa",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: auditoría marzo 2026",
            }
        ),
    )