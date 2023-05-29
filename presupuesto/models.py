from django.db import models
from datetime import date
from django.dispatch import receiver

from insumos.models import Categoria
from departamentos.models import Departamento, Subdepartamento



class PresupuestoCategoria(models.Model):
    id_categoria = models.OneToOneField(Categoria, on_delete=models.PROTECT, verbose_name="Categoría", related_name="presupuesto_categoria")
    marco_presupuestario = models.FloatField(verbose_name="Marco Presupuestario")

    class Meta:
            ordering = ['-id']



class PresupuestoDepartamento(models.Model):
    id_presupuesto_categoria = models.ForeignKey(PresupuestoCategoria, on_delete=models.PROTECT, verbose_name="Categoría", default=None, related_name="presupuesto_dpto_categoria")
    id_departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, verbose_name="Departamento", related_name="presupuesto_dpto")
    presupuesto = models.FloatField(verbose_name="Presupuesto")
    fecha = models.DateField(default=date.today, verbose_name="Fecha")
    estado = models.BooleanField(default=True, verbose_name="Estado")  



class PresupuestoSubDepartamento(models.Model):
    id_presupuesto_categoria = models.ForeignKey(PresupuestoCategoria, on_delete=models.PROTECT, verbose_name="Categoría", default=None, related_name="presupuesto_subdpto_categoria")
    id_departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, verbose_name="Departamento", related_name="presupuesto_subdpto_dpto")
    id_subdepartamento = models.ForeignKey(Subdepartamento, on_delete=models.PROTECT, verbose_name="SubDepartamento", related_name="presupuesto_subdpto")    
    presupuesto = models.FloatField(verbose_name="Presupuesto")
    fecha = models.DateField(default=date.today, verbose_name="Fecha")
    estado = models.BooleanField(default=True, verbose_name="Estado")  

