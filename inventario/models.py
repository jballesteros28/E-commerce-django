from __future__ import annotations



from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from catalogo.models import Juego

from inventario.enums import OrigenMovimientoInventario, TipoMovimientoInventario


class InventarioProducto(models.Model):
    """
    Mantiene el stock consolidado de un producto.

    Este modelo separa la lógica de inventario del catálogo.
    Así el producto sigue enfocado en datos comerciales y
    el inventario en existencia y disponibilidad.
    """

    producto = models.OneToOneField(
        Juego,
        on_delete=models.CASCADE,
        related_name="inventario",
        verbose_name="Producto",
    )
    stock_actual = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock actual",
        help_text="Cantidad física actual disponible en inventario.",
    )
    stock_reservado = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock reservado",
        help_text="Cantidad reservada temporalmente para procesos de compra.",
    )
    stock_minimo = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock mínimo",
        help_text="Umbral mínimo recomendado para reposición.",
    )
    activo_para_venta = models.BooleanField(
        default=True,
        verbose_name="Activo para venta",
        help_text="Indica si este producto puede venderse actualmente.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado el",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizado el",
    )

    class Meta:
        verbose_name = "Inventario de producto"
        verbose_name_plural = "Inventarios de productos"
        permissions = [
            ("can_manage_inventory", "Puede gestionar inventario"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(stock_actual__gte=0),
                name="inventario_stock_actual_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(stock_reservado__gte=0),
                name="inventario_stock_reservado_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(stock_minimo__gte=0),
                name="inventario_stock_minimo_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(stock_actual__gte=F("stock_reservado")),
                name="inventario_stock_actual_mayor_igual_reservado",
            ),
        ]

    def __str__(self) -> str:
        """
        Representación legible del inventario.
        """
        return f"Inventario - {self.producto}"

    @property
    def stock_disponible(self) -> int:
        """
        Stock realmente disponible para vender.
        """
        return self.stock_actual - self.stock_reservado

    @property
    def tiene_stock(self) -> bool:
        """
        Indica si hay stock disponible para venta.
        """
        return self.stock_disponible > 0

    @property
    def bajo_stock(self) -> bool:
        """
        Indica si el stock disponible está en o por debajo del mínimo.
        """
        return self.stock_disponible <= self.stock_minimo

    def clean(self) -> None:
        """
        Validaciones de negocio del inventario.
        """
        errores: dict[str, str] = {}

        if self.stock_reservado > self.stock_actual:
            errores["stock_reservado"] = (
                "El stock reservado no puede ser mayor al stock actual."
            )

        if self.stock_actual < 0:
            errores["stock_actual"] = "El stock actual no puede ser negativo."

        if self.stock_minimo < 0:
            errores["stock_minimo"] = "El stock mínimo no puede ser negativo."

        if errores:
            raise ValidationError(errores)


class MovimientoInventario(models.Model):
    """
    Registra cada cambio de stock con trazabilidad completa.

    La cantidad siempre se guarda positiva.
    El efecto sobre stock lo define el tipo de movimiento.
    """

    inventario = models.ForeignKey(
        InventarioProducto,
        on_delete=models.CASCADE,
        related_name="movimientos",
        verbose_name="Inventario",
    )
    tipo_movimiento = models.CharField(
        max_length=30,
        choices=TipoMovimientoInventario.choices,
        verbose_name="Tipo de movimiento",
    )
    origen = models.CharField(
        max_length=20,
        choices=OrigenMovimientoInventario.choices,
        verbose_name="Origen",
        default=OrigenMovimientoInventario.SISTEMA,
    )
    cantidad = models.PositiveIntegerField(
        verbose_name="Cantidad",
        help_text="La cantidad siempre debe ser mayor a cero.",
    )
    stock_anterior = models.PositiveIntegerField(
        verbose_name="Stock anterior",
    )
    stock_posterior = models.PositiveIntegerField(
        verbose_name="Stock posterior",
    )
    motivo = models.CharField(
        max_length=255,
        verbose_name="Motivo",
        help_text="Describe por qué se registró este movimiento.",
    )
    referencia_externa = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Referencia externa",
        help_text="Ejemplo: ID de pedido, devolución o proceso externo.",
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_inventario_creados",
        verbose_name="Creado por",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de creación",
    )

    class Meta:
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad__gt=0),
                name="movimiento_inventario_cantidad_gt_0",
            ),
            models.CheckConstraint(
                condition=Q(stock_anterior__gte=0),
                name="movimiento_inventario_stock_anterior_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(stock_posterior__gte=0),
                name="movimiento_inventario_stock_posterior_gte_0",
            ),
        ]

    def __str__(self) -> str:
        """
        Representación legible del movimiento.
        """
        return (
            f"{self.get_tipo_movimiento_display()} - "
            f"{self.inventario.producto} - {self.cantidad}"
        )

    def clean(self) -> None:
        """
        Validaciones de negocio del movimiento.
        """
        errores: dict[str, str] = {}

        if self.cantidad <= 0:
            errores["cantidad"] = "La cantidad debe ser mayor a cero."

        if self.stock_posterior < 0:
            errores["stock_posterior"] = "El stock posterior no puede ser negativo."

        if not self.motivo.strip():
            errores["motivo"] = "El motivo es obligatorio."

        if errores:
            raise ValidationError(errores)