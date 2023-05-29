from django import template
from insumos.models import Insumo


# Clase para el uso de filtros y llamadas a funciones
register = template.Library()


@register.filter(name="get_saldo_insumo")
def get_saldo_insumo(value):
    insumo = Insumo.objects.filter(id = value)
    
    if (insumo is not None):    
        return insumo[0].saldo
    else:
        return 0


@register.filter(name="get_unidad_medida")
def get_unidad_medida(value):
    insumo = Insumo.objects.filter(id = value)
    
    if (insumo is not None):    
        return insumo[0].unidad_medida
    else:
        return 0