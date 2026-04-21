from django.apps import AppConfig


class InventarioConfig(AppConfig):
    """
    Configuración principal de la app de inventario.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "inventario"

    def ready(self) -> None:
        """
        Importa señales cuando Django inicia la app.
        """
        import inventario.signals  # noqa: F401