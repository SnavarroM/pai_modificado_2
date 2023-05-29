from types import NoneType
from datetime import date
from urllib import request

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from .models import CierreMensual, CierreMensualInsumo
from insumos.models import Insumo
from logs.models import Log




def ExisteCierreMensual(fechaActual):
    cierre = CierreMensual.objects.filter(fecha_cierre__year=fechaActual.strftime('%Y')).filter(fecha_cierre__month=fechaActual.strftime('%m'))
    return cierre if cierre else None



def EliminarCierreInsumoDetalle(Cierre):
    cierre = CierreMensualInsumo.objects.filter(id_cierre_mensual=Cierre.id_cierre_mensual).delete()
    return cierre



def InsertarCierre(request, fechaActual):
    cierre = CierreMensual(fecha_cierre=fechaActual)
    cierre.save()
    
    Log.InsertarLog(request.user, 'Se realizó el Cierre Mensual ' + str(cierre.id_cierre_mensual) + ' correspondiente a ' + str(fechaActual), 0)
    return cierre



def ActualizarCierre(request, Cierre, fechaActual):
    cierre = CierreMensual.objects.get(id_cierre_mensual=Cierre.id_cierre_mensual)
    cierre.fecha_cierre = fechaActual
    cierre.save()    
    
    Log.InsertarLog(request.user, 'Se actualizó el Cierre Mensual Id ' + str(Cierre.id_cierre_mensual) + ' correspondiente a ' + str(fechaActual), 0)
    return cierre



def InsertarCierreInsumoDetalle(Cierre):
    insumos = Insumo.objects.all()

    for ins in insumos:
        detcierre = CierreMensualInsumo(
            id_cierre_mensual = Cierre, 
            id_insumo  = ins.id,
            codigo_insumo = ins.codigo_insumo,
            denominacion = ins.denominacion,
            id_unidad_medida = ins.unidad_medida,
            saldo = ins.saldo,
            precio = ins.precio,
            id_categoria = ins.categoria,
            estado = ins.estado
        )
        detcierre.save()


@permission_required("cierreMensual.add_cierre", "cierreMensual.change_cierre")
def CierreInsumo(request):
    
    fechaActual = date.today()
    Cierre = ExisteCierreMensual(fechaActual) 
    
    if (Cierre is not None):
        ActualizarCierre(request, Cierre[0], fechaActual)
        EliminarCierreInsumoDetalle(Cierre[0])
        InsertarCierreInsumoDetalle(Cierre[0])
        messages.success(request, 'Cierre Mensual fue actualizado con éxito.')
    else:
        Cierre = InsertarCierre(request, fechaActual)       
        InsertarCierreInsumoDetalle( Cierre)
        messages.success(request, 'Cierre Mensual fue creado con éxito.')

    
    return HttpResponseRedirect(reverse_lazy('insumos:insumos-list'))