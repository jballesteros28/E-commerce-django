from __future__ import annotations

from django import forms


class MovimientoInventarioForm(forms.Form):
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


class AjusteStockMinimoForm(forms.Form):
    nuevo_stock_minimo = forms.IntegerField(
        min_value=0,
        label="Nuevo stock mínimo",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese el nuevo stock mínimo",
            }
        ),
    )
    motivo = forms.CharField(
        max_length=255,
        label="Motivo",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Motivo del ajuste de stock mínimo",
            }
        ),
    )


class ReservaStockForm(forms.Form):
    cantidad = forms.IntegerField(
        min_value=1,
        label="Cantidad a reservar",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese la cantidad a reservar",
            }
        ),
    )
    motivo = forms.CharField(
        max_length=255,
        label="Motivo",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: pedido pendiente, bloqueo interno, etc.",
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
                "placeholder": "Ejemplo: orden #123",
            }
        ),
    )


class LiberarReservaStockForm(forms.Form):
    cantidad = forms.IntegerField(
        min_value=1,
        label="Cantidad a liberar",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese la cantidad a liberar",
            }
        ),
    )
    motivo = forms.CharField(
        max_length=255,
        label="Motivo",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Motivo de la liberación",
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
                "placeholder": "Ejemplo: cancelación de orden #123",
            }
        ),
    )