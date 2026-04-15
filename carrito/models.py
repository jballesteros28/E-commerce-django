from django.db import models
from django.conf import settings
from catalogo.models import Juego

# Create your models here.
class Carrito(models.Model):
    usuario= models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete= models.CASCADE,
        related_name='carrito'
    )
    creado= models.DateTimeField(auto_now_add=True)
    actualizado= models.DateTimeField(auto_now=True)
    
    
    def __str__(self) -> str:
        return f"carrito de {self.usuario.username}"
    
    def total_items(self):
        return sum(item.cantidad for item in self.items.all())
    
    def total_precio(self):
        return sum(item.subtotal() for item in self.items.all())
    
class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="items")
    juego = models.ForeignKey(Juego, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together= ("carrito","juego")
        
    def __str__(self) -> str:
        return f"{self.juego.nombre} x {self.cantidad}"
    
    def subtotal(self):
        return self.juego.precio * self.cantidad