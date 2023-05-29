
from django.db import models
from django import template
from django.conf import settings

# Clase para el uso de filtros y llamadas a funciones del Modelo 
register = template.Library()


class Cargo(models.Model):
    nombre_cargo = models.CharField(max_length=50, verbose_name="Descripción Cargo")
    estado = models.BooleanField(default=True, verbose_name="Estado")  
    
    def __str__(self):
        return self.nombre_cargo



    @register.filter(name="get_estado_cargo")
    def get_estado_cargo(self):     
        edo_cargo = Cargo.objects.filter(id = self.id)
        return settings.ESTADO[0][edo_cargo[0].estado]