from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from carrito.models import Carrito, ItemCarrito
from catalogo.models import Juego
from inventario.models import InventarioProducto
from ordenes.models import Orden
from ordenes.services import crear_orden_desde_carrito

User = get_user_model()


class OrdenesServicesTestCase(TestCase):
    def setUp(self) -> None:
        self.usuario = User.objects.create_user(
            username="usuario_test",
            password="test12345",
        )

        self.carrito = Carrito.objects.create(usuario=self.usuario)

        self.juego = Juego.objects.create(
            nombre="God of War",
            precio=10000,
            plataforma="PS5",
            imagen="gow.jpg",
        )

        self.inventario = InventarioProducto.objects.create(
            producto=self.juego,
            stock_actual=10,
            stock_reservado=0,
            stock_minimo=2,
            activo_para_venta=True,
        )

    def test_crear_orden_desde_carrito_funciona(self) -> None:
        ItemCarrito.objects.create(
            carrito=self.carrito,
            juego=self.juego,
            cantidad=2,
        )

        resultado = crear_orden_desde_carrito(usuario=self.usuario)

        self.assertEqual(Orden.objects.count(), 1)
        self.assertEqual(resultado.orden.items.count(), 1)
        self.assertEqual(resultado.orden.total, self.juego.precio * 2)

    def test_no_crea_orden_con_carrito_vacio(self) -> None:
        with self.assertRaises(ValidationError):
            crear_orden_desde_carrito(usuario=self.usuario)

    def test_no_crea_orden_si_no_hay_stock_suficiente(self) -> None:
        ItemCarrito.objects.create(
            carrito=self.carrito,
            juego=self.juego,
            cantidad=20,
        )

        with self.assertRaises(ValidationError):
            crear_orden_desde_carrito(usuario=self.usuario)