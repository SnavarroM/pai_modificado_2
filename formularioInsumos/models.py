from django.utils import  timezone
from django import template
from django.db import models
from django.conf import settings

from datetime import datetime
from departamentos.models import Departamento, Subdepartamento, Unidad
from insumos.models import Insumo
from user.models import UserProfile
from logs.models import Log


# Clase para el uso de filtros y llamadas a funciones del Modelo 
register = template.Library()



class Formulario(models.Model):
    id_formulario = models.AutoField(primary_key=True)
    folio = models.CharField(max_length=50, unique=True, verbose_name="Folio")
    id_departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, verbose_name="Departamento")
    id_sub_departamento = models.ForeignKey(Subdepartamento, on_delete=models.PROTECT, verbose_name="Sub Departamento", null=True)    
    id_unidad = models.ForeignKey(Unidad, on_delete=models.PROTECT, verbose_name="Unidad", null=True)
    fecha_creacion = models.DateField(verbose_name="Fecha Creación")
    rut_solicitante = models.CharField(max_length=50, verbose_name="Rut Solicitante")
    rut_jefe_aprobador = models.CharField(max_length=50, verbose_name="Rut Jefe Aprobador")
    rut_admin_interna = models.CharField(max_length=50, verbose_name="Rut Administración Interna")
    estado = models.BooleanField(default=True, verbose_name="Estado")   


    class Meta:
        ordering = ['-pk']


    def get_max_id(self):        
        maxId = Formulario.objects.all().order_by('-id_formulario').first()

        if (maxId is not None):
            return int(maxId.folio.split('/')[0][1:]) + 1
        else:
            return 1



    def save(self, **kwargs):
        
        if not self.id_formulario:   
            maxId = self.get_max_id()
            anio = str(datetime.now().strftime('%Y'))
            folio = "E{:06d}".format(maxId if maxId is not None else 1) + '/' + anio


            self.folio = folio
            self.hora_ingreso = datetime.now().strftime('%H:%M:%S')
            
            super(Formulario, self).save(**kwargs)
            objF = Formulario.objects.get(folio = folio)

            SHistorial = FormularioHistorial()
            SHistorial.id_folio_formulario = objF
            SHistorial.estado_formulario = settings.ESTADO_APROBACION_SOLICITUD[0][0]
            SHistorial.estado = True
            SHistorial.save()


    # @register.filter(name="get_edo_solicitud_insumo")
    # def get_edo_solicitud_insumo(self):     
    #     edo_solicitud = FormularioHistorial.objects.filter(id_folio_formulario = self.id_formulario).order_by('-pk').first()
    #     return settings.ESTADO_APROBACION_SOLICITUD[edo_solicitud.estado_formulario - 1][1]




class FormularioInsumo(models.Model):
    id_folio = models.ForeignKey(Formulario, on_delete=models.PROTECT, verbose_name="Folio")
    id_insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT, verbose_name="Insumo")

    cantidad = models.IntegerField(verbose_name="Cantidad")
    cantidad_aprobada_jefatura = models.IntegerField(verbose_name="Cantidad Aprobada por Jefatura", default=0)
    cantidad_entregada = models.IntegerField(verbose_name="Cantidad Entregada", default=0)
    precio = models.FloatField(verbose_name="Precio", default=0)
    estado = models.BooleanField(default=True, verbose_name="Estado")



class FormularioHistorial(models.Model):
    id_folio_formulario = models.ForeignKey(Formulario, on_delete=models.PROTECT, verbose_name="Folio")
    fecha_hora = models.DateTimeField(default=timezone.now)
    estado_formulario = models.IntegerField(verbose_name="Estado Solicitud")
    rut_gestor = models.CharField(max_length=50, verbose_name="Rut Gestor")
    estado = models.BooleanField(default=True, verbose_name="Estado")