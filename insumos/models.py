from email.policy import default
from django.db import models
from django import template
from django.conf import settings
from logs.models import Log
from user.models import User


# Clase para el uso de filtros y llamadas a funciones del Modelo 
register = template.Library()



class UnidadMedida(models.Model):
    nombre_unidad_medida = models.CharField(max_length=50, verbose_name="Unidad Medida")    
    estado = models.BooleanField(default=True, verbose_name="Estado")

    def __str__(self):
        return self.nombre_unidad_medida

    @register.filter(name="get_estado_unidmedida")
    def get_estado_unidmedida(self):     
        edo_unidmedida = UnidadMedida.objects.filter(id = self.id)
        return settings.ESTADO[0][edo_unidmedida[0].estado]



class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=255, verbose_name="Nombre")
    estado = models.BooleanField(default=True, verbose_name="Estado")

    def __str__(self):
        return self.nombre_categoria


    @register.filter(name="get_estado_categoria")
    def get_estado_categoria(self):     
        edo_categoria = Categoria.objects.filter(id = self.id)
        return settings.ESTADO[0][edo_categoria[0].estado]



class Insumo(models.Model):
    codigo_insumo = models.CharField(max_length=50, verbose_name="Código Insumo")
    denominacion = models.CharField(max_length=255, verbose_name="Denominación")
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, verbose_name="Unidad Medida", related_name="insumo_unidadmedida")
    saldo = models.IntegerField(verbose_name="Saldo")
    precio = models.FloatField(verbose_name="Precio", default=0)
    stock_critico = models.IntegerField(verbose_name="Stock Crítico", default=1)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, verbose_name="Categoría", related_name="insumo_categoria")
    estado = models.BooleanField(default=True, verbose_name="Estado")


    class Meta:
        
        ordering = ['id']


    def __str__(self):
        return self.denominacion


    @register.filter(name="get_estado_insumo")
    def get_estado_insumo(self):     
        edo_insumo = Insumo.objects.filter(id = self.id)
        return settings.ESTADO[0][edo_insumo[0].estado]


    def update_precio_insumo(codigo_insumo, precio, usuario):
        insumo = Insumo.objects.get(codigo_insumo=codigo_insumo)
        insumo.precio = precio
        insumo.save()

        user_instance = User.objects.get(userprofile__rut=usuario)
        Log.InsertarLog(user_instance, 'Se actualizó el precio a ' + str(precio) + ' del producto ' + str(codigo_insumo), 0)

        return insumo


    def aumentar_cantidad_insumo(codigo_insumo, cantidad, usuario):
        insumo = Insumo.objects.get(codigo_insumo=codigo_insumo)
        insumo.saldo = insumo.saldo + cantidad
        insumo.save()

        user_instance = User.objects.get(userprofile__rut=usuario)
        Log.InsertarLog(user_instance, 'Se sumaron ' + str(cantidad) + ' al saldo del producto ' + str(codigo_insumo), 0)

        return insumo


    def disminuir_cantidad_insumo(codigo_insumo, cantidad, usuario):
        insumo = Insumo.objects.get(codigo_insumo=codigo_insumo)
        insumo.saldo = insumo.saldo - cantidad
        insumo.save()

        user_instance = User.objects.get(userprofile__rut=usuario)
        Log.InsertarLog(user_instance, 'Se restaron ' + str(cantidad) + ' al saldo del producto ' + str(codigo_insumo), 0)

        return insumo