from django.db import models
from django import template
from django.dispatch import receiver
from user.models import UserProfile

from departamentos.models import Departamento, Subdepartamento
from presupuesto.models import PresupuestoCategoria, PresupuestoDepartamento, PresupuestoSubDepartamento

# Clase para el uso de filtros y llamadas a funciones
register = template.Library()


@register.filter(name="get_nombre_jefe")
def get_nombre_jefe(value):
    if value is not None and ('-' in value):
        userProfile = UserProfile.objects.filter(rut = value)
        return userProfile[0] if userProfile else ''
    else:
        return ''




@receiver(models.signals.post_save, sender=Departamento)
def crear_presupuestos_dpto(sender, instance, created, **kwargs):
    dpto = instance
    ctas = PresupuestoCategoria.objects.all()

    for c in ctas:
        pptodpto = PresupuestoDepartamento(id_presupuesto_categoria = c, id_departamento = dpto, presupuesto = 0)
        pptodpto.save()



@receiver(models.signals.post_save, sender=Subdepartamento)
def crear_presupuestos_subdpto(sender, instance, created, **kwargs):
    subdpto = instance
    ctas = PresupuestoCategoria.objects.all()

    for c in ctas:
        pptosubdpto = PresupuestoSubDepartamento(id_presupuesto_categoria = instance, id_departamento = subdpto.departamento, id_subdepartamento = subdpto, presupuesto = 0)
        pptosubdpto.save()