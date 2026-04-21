from __future__ import annotations

from django.db import models
from django.db.models import Q

from ordenes.models import Orden
from pagos.enums import EstadoPago, ProveedorPago


class Pago(models.Model):
    orden = models.OneToOneField(
        Orden,
        on_delete=models.CASCADE,
        related_name="pago",
        verbose_name="Orden",
    )
    proveedor = models.CharField(
        max_length=30,
        choices=ProveedorPago.choices,
        default=ProveedorPago.MERCADO_PAGO,
        verbose_name="Proveedor",
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE,
        verbose_name="Estado",
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monto",
    )
    moneda = models.CharField(
        max_length=10,
        default="ARS",
        verbose_name="Moneda",
    )
    external_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name="ID externo",
    )
    preference_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="ID de preferencia",
    )
    init_point = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL de checkout",
    )
    raw_response = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Respuesta cruda",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        constraints = [
            models.CheckConstraint(
                condition=Q(monto__gte=0),
                name="pago_monto_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return f"Pago {self.id} - {self.orden.referencia}"


class WebhookPagoLog(models.Model):
    """
    Guarda trazabilidad de cada webhook recibido.
    Muy útil para debugging y auditoría.
    """

    proveedor = models.CharField(
        max_length=30,
        default=ProveedorPago.MERCADO_PAGO,
        verbose_name="Proveedor",
    )
    payload = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Payload",
    )
    query_params = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Query params",
    )
    headers = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Headers",
    )
    procesado = models.BooleanField(
        default=False,
        verbose_name="Procesado",
    )
    detalle = models.TextField(
        blank=True,
        null=True,
        verbose_name="Detalle",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log de webhook de pago"
        verbose_name_plural = "Logs de webhook de pagos"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Webhook {self.proveedor} - {self.created_at:%d/%m/%Y %H:%M:%S}"