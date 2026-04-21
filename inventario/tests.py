from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from inventario.enums import TipoMovimientoInventario
from inventario.models import InventarioProducto
from inventario.services import ajustar_stock, registrar_entrada, registrar_salida

User = get_user_model()
Producto = apps.get_model("catalogo", "Juego")


class InventarioServicesTestCase(TestCase):
    """
    Tests base del módulo de inventario.
    """

    def setUp(self) -> None:
        self.usuario = User.objects.create_user(
            username="admin_test",
            password="test12345",
        )

        self.producto = Producto.objects.create(
            nombre="Producto test",
            precio=1000,
            plataforma="PC",
            imagen="default.jpg",
        )

        self.inventario = InventarioProducto.objects.get(producto=self.producto)

    def test_registrar_entrada_aumenta_stock(self) -> None:
        resultado = registrar_entrada(
            inventario_id=self.inventario.id,
            cantidad=10,
            motivo="Ingreso inicial",
            creado_por=self.usuario,
        )

        self.inventario.refresh_from_db()

        self.assertEqual(self.inventario.stock_actual, 10)
        self.assertEqual(resultado.movimiento.tipo_movimiento, TipoMovimientoInventario.ENTRADA)

    def test_registrar_salida_disminuye_stock(self) -> None:
        registrar_entrada(
            inventario_id=self.inventario.id,
            cantidad=10,
            motivo="Ingreso inicial",
            creado_por=self.usuario,
        )

        resultado = registrar_salida(
            inventario_id=self.inventario.id,
            cantidad=4,
            motivo="Salida por prueba",
            creado_por=self.usuario,
        )

        self.inventario.refresh_from_db()

        self.assertEqual(self.inventario.stock_actual, 6)
        self.assertEqual(resultado.movimiento.tipo_movimiento, TipoMovimientoInventario.SALIDA)

    def test_registrar_salida_sin_stock_disponible_lanza_error(self) -> None:
        with self.assertRaises(ValidationError):
            registrar_salida(
                inventario_id=self.inventario.id,
                cantidad=1,
                motivo="Intento inválido",
                creado_por=self.usuario,
            )

    def test_ajuste_stock_actualiza_valor(self) -> None:
        registrar_entrada(
            inventario_id=self.inventario.id,
            cantidad=10,
            motivo="Ingreso inicial",
            creado_por=self.usuario,
        )

        ajustar_stock(
            inventario_id=self.inventario.id,
            nuevo_stock=7,
            motivo="Ajuste por auditoría",
            creado_por=self.usuario,
        )

        self.inventario.refresh_from_db()

        self.assertEqual(self.inventario.stock_actual, 7)

    def test_stock_disponible_se_calcula_correctamente(self) -> None:
        self.inventario.stock_actual = 12
        self.inventario.stock_reservado = 5
        self.inventario.save()

        self.assertEqual(self.inventario.stock_disponible, 7)