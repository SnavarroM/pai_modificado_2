from django.db import models
from django.utils import timezone

from logs.models import Log
from user.models import User


class Inventario(models.Model):
    codigo_producto = models.IntegerField(verbose_name="Código Producto")
    cantidad = models.IntegerField(verbose_name="Cantidad")
    tipo_transaccion = models.CharField(max_length=5, verbose_name="Tipo Transacción")
    id_compra = models.IntegerField(verbose_name="Id Compra")
    id_folio_entrega = models.CharField(max_length=20, verbose_name="Id Folio Entrega")
    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha")

    class Meta:
        ordering = ['id']


    def InsertarInventarioCompra(lista_productos, tipo_transaccion):
        for prod in lista_productos:
            inventario = Inventario(
                codigo_producto = prod.id_insumo.codigo_insumo,
                cantidad = prod.cantidad,
                tipo_transaccion = tipo_transaccion,
                id_compra = prod.id_compra.id,
                id_folio_entrega = 0
            )
            inventario.save()

            user_instance = User.objects.get(userprofile__rut=prod.id_compra.rut_responsable)
            Log.InsertarLog(user_instance, 'Se ingresó al Inventario una Compra Id ' + str(prod.id_compra.id) + ' del producto ' + str(prod.id_insumo.codigo_insumo), prod.cantidad)

        return inventario


    def InsertarInventarioEntrega(lista_productos, tipo_transaccion):        
        for prod in lista_productos:
            inventario = Inventario(
                codigo_producto = prod["codigo_producto"],
                cantidad = prod["cantidad"],
                tipo_transaccion = tipo_transaccion,
                id_compra = 0,
                id_folio_entrega = prod["id_folio_entrega"]
            )
            inventario.save()
            print(prod["rut_solicitante"])
            
            user_instance = User.objects.get(userprofile__rut=prod["rut_solicitante"])
            Log.InsertarLog(user_instance, 'Se entregó con folio ' + str(prod["id_folio_entrega"]) + ' el producto ' + str(prod["codigo_producto"]), prod["cantidad"])

        return inventario