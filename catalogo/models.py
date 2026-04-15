from django.db import models

# Create your models here.
class Juego(models.Model):
  nombre = models.CharField(max_length=100)
  precio = models.DecimalField(max_digits=6,decimal_places=2)
  plataforma = models.CharField(max_length=200)
  imagen = models.CharField(max_length=200, default="default.jpg")
  
  def __str__(self) -> str:
    return f'{self.nombre }'