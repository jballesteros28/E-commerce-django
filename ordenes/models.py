from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from ordenes.enums import EstadoOrden
from catalogo.models import Juego


class Orden(models.Model):
    """
    Cabecera de una compra.

    Guarda la información general de la orden y su estado.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ordenes",
        verbose_name="Usuario",
    )
    referencia = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Referencia",
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoOrden.choices,
        default=EstadoOrden.PENDIENTE,
        verbose_name="Estado",
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Subtotal",
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Total",
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Creada el",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizada el",
    )

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(subtotal__gte=0),
                name="orden_subtotal_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(total__gte=0),
                name="orden_total_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.referencia} - {self.usuario.username}"

    def clean(self) -> None:
        errores: dict[str, str] = {}

        if self.subtotal < 0:
            errores["subtotal"] = "El subtotal no puede ser negativo."

        if self.total < 0:
            errores["total"] = "El total no puede ser negativo."

        if errores:
            raise ValidationError(errores)


class OrdenItem(models.Model):
    """
    Detalle de productos comprados.

    Guarda snapshot del producto para no depender del estado futuro del catálogo.
    """

    orden = models.ForeignKey(
        Orden,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Orden",
    )
    juego = models.ForeignKey(
        Juego,
        on_delete=models.PROTECT,
        related_name="ordenes_item",
        verbose_name="Juego",
    )
    nombre_producto = models.CharField(
        max_length=100,
        verbose_name="Nombre del producto",
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio unitario",
    )
    cantidad = models.PositiveIntegerField(
        verbose_name="Cantidad",
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Subtotal",
    )

    class Meta:
        verbose_name = "Item de orden"
        verbose_name_plural = "Items de orden"
        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad__gt=0),
                name="orden_item_cantidad_gt_0",
            ),
            models.CheckConstraint(
                condition=Q(precio_unitario__gte=0),
                name="orden_item_precio_unitario_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(subtotal__gte=0),
                name="orden_item_subtotal_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nombre_producto} x {self.cantidad}"

    def clean(self) -> None:
        errores: dict[str, str] = {}

        if self.cantidad <= 0:
            errores["cantidad"] = "La cantidad debe ser mayor a cero."

        if self.precio_unitario < 0:
            errores["precio_unitario"] = "El precio unitario no puede ser negativo."

        if self.subtotal < 0:
            errores["subtotal"] = "El subtotal no puede ser negativo."

        if errores:
            raise ValidationError(errores)