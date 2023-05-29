from datetime import date
from sys import maxsize
from django import template
from django.db import models
from django.conf import settings

from insumos.models import Insumo
from proveedores.models import Proveedor

register = template.Library()


class Compra(models.Model):
    fecha_compra = models.DateField(verbose_name="Fecha Compra")
    guia = models.CharField(max_length=50, verbose_name="Guía", unique=True) 
    orden_de_compra = models.CharField(max_length=50, verbose_name="Orden de Compra", unique=True)
    total_compra = models.IntegerField(verbose_name="Total Compra")
    descuento = models.IntegerField(verbose_name="Descuento")
    fecha_ingreso_compra = models.DateField(default=date.today, verbose_name="Fecha Ingreso Compra")
    rut_responsable = models.CharField(max_length=50, verbose_name="RUT Responsable")
    estado = models.BooleanField(default=True, verbose_name="Estado") 

    # Campos Relación
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, verbose_name="Proveedor")

    class Meta:
        ordering = ['-id']


    @property
    def total_neto(self):
        detallecompra = CompraInsumo.objects.filter(id_compra = self.id) 
        totalneto = 0
        for detcom in detallecompra:
            totalneto += detcom.cantidad * detcom.precio_unitario        
        return totalneto


    @property
    def total_iva(self):
        totalneto = self.total_neto
        valoriva = float(settings.IVA) / 100
        totaliva = totalneto * valoriva
        return totaliva



class CompraInsumo(models.Model):
    # Campos Relación
    id_compra = models.ForeignKey(Compra, on_delete=models.PROTECT, verbose_name="Compra")
    id_insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT, verbose_name="Insumo")
    
    cantidad = models.IntegerField(verbose_name="Cantidad")
    precio_unitario = models.FloatField(verbose_name="Precio Unitario")
    precio_promedio = models.FloatField(verbose_name="Precio Promedio")
    precio_con_iva = models.FloatField(verbose_name="Precio con IVA")
    estado = models.BooleanField(default=True, verbose_name="Estado") 


    def __str__(self):
        return self.id_compra.guia


    @property
    def total_insumo(self):
        return self.cantidad * self.precio_unitario