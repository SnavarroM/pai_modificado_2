from django import template
from django.db import models
from django.dispatch import receiver

from departamentos.models import Departamento, Subdepartamento
from presupuesto.models import PresupuestoCategoria, PresupuestoDepartamento, PresupuestoSubDepartamento


# Clase para el uso de filtros y llamadas a funciones
register = template.Library()


@receiver(models.signals.post_save, sender=PresupuestoCategoria)
def crear_presupuestos_categoria(sender, instance, created, **kwargs):

    pptoExiste = PresupuestoDepartamento.objects.filter(id_presupuesto_categoria = instance)

    if not pptoExiste:
        dptos = Departamento.objects.all()
        subdptos = Subdepartamento.objects.all()

        lista_dptos = []
        for d in dptos:
                pptoDpto = PresupuestoDepartamento(id_presupuesto_categoria = instance, id_departamento = d, presupuesto = 0)
                lista_dptos.append(pptoDpto)

        PresupuestoDepartamento.objects.bulk_create(lista_dptos)

        lista_subdptos = []
        for s in subdptos:
                pptoSubDpto = PresupuestoSubDepartamento(id_presupuesto_categoria = instance, id_departamento = s.departamento, id_subdepartamento = s, presupuesto = 0)
                lista_subdptos.append(pptoSubDpto)

        PresupuestoSubDepartamento.objects.bulk_create(lista_subdptos)        


        #for d in dptos:
        #    pptodpto = PresupuestoDepartamento(id_presupuesto_categoria = instance, id_departamento = d, presupuesto = 0)
        #    pptodpto.save()

        #for s in subdptos:
        #    pptosubdpto = PresupuestoSubDepartamento(id_presupuesto_categoria = instance, id_departamento = s.departamento, id_subdepartamento = s, presupuesto = 0)
        #    pptosubdpto.save()