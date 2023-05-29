from django import template
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator

# Clase para el uso de filtros y llamadas a funciones del Modelo 
register = template.Library()


class Proveedor(models.Model):
    rut_proveedor = models.CharField(max_length=50, verbose_name="RUT Proveedor", validators=[RegexValidator('^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]{1}$', message="Ingresar un rut válido (Ej: 12345678-9)")])
    nombre_proveedor = models.CharField(max_length=50, verbose_name="Nombre Proveedor")
    estado = models.BooleanField(default=True, verbose_name="Estado")  

    def __str__(self):
        return self.nombre_proveedor


    @register.filter(name="get_estado_proveedor")
    def get_estado_proveedor(self):     
        edo_proveedor = Proveedor.objects.filter(id = self.id)
        return settings.ESTADO[0][edo_proveedor[0].estado]