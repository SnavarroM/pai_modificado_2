from datetime import date
from django import template
from django.db import models

from insumos.models import Categoria, UnidadMedida



class CierreMensual(models.Model):
    id_cierre_mensual = models.AutoField(primary_key=True)
    fecha_cierre = models.DateField(default=date.today, verbose_name="Fecha Cierre")
    estado = models.BooleanField(default=True, verbose_name="Estado")


    class Meta:
        ordering = ['-pk']




class CierreMensualInsumo(models.Model):
    id_cierre_mensual_insumo = models.AutoField(primary_key=True)
    id_cierre_mensual = models.ForeignKey(CierreMensual, on_delete=models.PROTECT, verbose_name="Id Cierre Mensual", related_name="cierremensual_insumo")
    id_insumo = models.IntegerField(verbose_name="Id Insumo") 
    codigo_insumo = models.IntegerField(verbose_name="Código Insumo")
    denominacion = models.CharField(max_length=255, default='', verbose_name="Denominación")
    id_unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, verbose_name="Id Cierre Mensual")
    saldo = models.IntegerField(verbose_name="Saldo")
    precio = models.FloatField(verbose_name="Precio")
    id_categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, verbose_name="Id Categoría")
    estado = models.BooleanField(default=True, verbose_name="Estado")


    class Meta:
        ordering = ['-pk']