from django.db import models


class EstadoPago(models.TextChoices):
    PENDIENTE = "PENDIENTE", "Pendiente"
    APROBADO = "APROBADO", "Aprobado"
    RECHAZADO = "RECHAZADO", "Rechazado"
    CANCELADO = "CANCELADO", "Cancelado"
    EXPIRADO = "EXPIRADO", "Expirado"
    ERROR = "ERROR", "Error"


class ProveedorPago(models.TextChoices):
    MERCADO_PAGO = "MERCADO_PAGO", "Mercado Pago"