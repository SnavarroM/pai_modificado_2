from django.db import models
from django import template
from django.conf import settings


# Clase para el uso de filtros y llamadas a funciones del Modelo 
register = template.Library()


class Departamento(models.Model):
    id_dpto = models.IntegerField(verbose_name='Id Departamento',unique=True)
    nombre_dpto = models.CharField(max_length=100,verbose_name='Nombre departamento')
    rut_jefe = models.CharField(max_length=20, verbose_name="Rut Jefe", blank=True, null=True)
    rut_jefe_subrogante = models.CharField(max_length=20, verbose_name="Rut Jefe Subrogante", blank=True, null=True)
    estado = models.BooleanField(verbose_name='Estado',default=True)
    
    def __str__(self):
        return (self.nombre_dpto)


    class Meta: 
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['id_dpto']


    @register.filter(name="get_estado_dpto")
    def get_estado_dpto(self):     
        edo_dpto = Departamento.objects.filter(id = self.id)
        return settings.ESTADO[0][edo_dpto[0].estado]



class Subdepartamento(models.Model):
    id_sub_dpto = models.IntegerField(verbose_name='Id Sub Departamento',unique=True)
    departamento = models.ForeignKey(Departamento,verbose_name='pertenece al departamento',on_delete=models.PROTECT)
    nombre_sub_dpto = models.CharField(max_length=100,verbose_name='Nombre Sub-Departamento')
    rut_jefe = models.CharField(max_length=20, verbose_name="Rut Jefe", blank=True, null=True)
    rut_jefe_subrogante = models.CharField(max_length=20, verbose_name="Rut Jefe Subrogante", blank=True, null=True)
    estado = models.BooleanField(verbose_name='Estado', default=True)

    def __str__(self):
        return (self.nombre_sub_dpto)

    class Meta: 
        verbose_name = "Sub-Departamento"
        verbose_name_plural = "Sub-Departamentos"
        ordering = ['id_sub_dpto']


    @register.filter(name="get_estado_subdpto")
    def get_estado_subdpto(self):     
        edo_subdpto = Subdepartamento.objects.filter(id = self.id)
        return settings.ESTADO[0][edo_subdpto[0].estado]



class Unidad(models.Model):
    id_unidad = models.IntegerField(verbose_name='Id Unidad',unique=True)
    subdepartamento = models.ForeignKey(Subdepartamento,verbose_name='pertenece al Sub-departamento',on_delete=models.PROTECT, related_name="unidad_sub_dpto")
    nombre_unidad = models.CharField(max_length=100,verbose_name='Nombre Unidad')
    rut_jefe = models.CharField(max_length=20, verbose_name="Rut Jefe", blank=True, null=True)
    rut_jefe_subrogante = models.CharField(max_length=20, verbose_name="Rut Jefe Subrogante", blank=True, null=True)
    estado = models.BooleanField(verbose_name='Estado',default=True)

    def __str__(self):
        return (self.nombre_unidad)

    class Meta: 
        verbose_name = "Unidad"
        verbose_name_plural = "Secciones"
        ordering = ['id_unidad']


    @register.filter(name="get_estado_unidad")
    def get_estado_unidad(self):     
        edo_unidad = Unidad.objects.filter(id = self.id)
        return settings.ESTADO[0][edo_unidad[0].estado]