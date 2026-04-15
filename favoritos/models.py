from django.db import models
from django.conf import settings
from catalogo.models import Juego

# Create your models here.
class Favorito(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favoritos'
    )
    juego = models.ForeignKey(
        Juego,
        on_delete=models.CASCADE,
        related_name='en_favoritos'
    )
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'juego'],
                name='unique_favorito_por_usuario'
            )
        ]
        
    def __str__(self) -> str:
        return f"{self.usuario.username} - {self.juego.nombre}"