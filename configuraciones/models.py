from django.db import models
from django.utils import timezone



class Configuraciones(models.Model):
    iva = models.FloatField(verbose_name="IVA")
    rut_encargado_bodega = models.CharField(max_length=50, verbose_name="Rut Encargado Bodega")
    rut_responsable = models.CharField(max_length=50, verbose_name="Rut Responsable")
    rut_secretaria_direccion = models.CharField(max_length=50, verbose_name="Rut Secretaria Dirección")
    ultima_actualizacion = models.DateField(default=timezone.now, verbose_name="Última Actualización")  
