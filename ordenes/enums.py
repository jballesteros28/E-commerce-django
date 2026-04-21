from django.db import models


class EstadoOrden(models.TextChoices):
    """
    Estados posibles de una orden.
    """

    PENDIENTE = "PENDIENTE", "Pendiente"
    EN_PROCESO = "EN_PROCESO", "En proceso"
    PAGADA = "PAGADA", "Pagada"
    CANCELADA = "CANCELADA", "Cancelada"
    FALLIDA = "FALLIDA", "Fallida"