from django.db import models


class TipoMovimientoInventario(models.TextChoices):
    """
    Tipos permitidos de movimientos de inventario.
    """

    ENTRADA = "ENTRADA", "Entrada"
    SALIDA = "SALIDA", "Salida"
    AJUSTE_POSITIVO = "AJUSTE_POSITIVO", "Ajuste positivo"
    AJUSTE_NEGATIVO = "AJUSTE_NEGATIVO", "Ajuste negativo"
    RESERVA = "RESERVA", "Reserva"
    LIBERACION = "LIBERACION", "Liberación"
    VENTA_CONFIRMADA = "VENTA_CONFIRMADA", "Venta confirmada"


class OrigenMovimientoInventario(models.TextChoices):
    """
    Origen del movimiento.
    """

    ADMIN = "ADMIN", "Administración"
    SISTEMA = "SISTEMA", "Sistema"
    PEDIDO = "PEDIDO", "Pedido"
    DEVOLUCION = "DEVOLUCION", "Devolución"
    AJUSTE = "AJUSTE", "Ajuste manual"