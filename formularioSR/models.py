from datetime import date, datetime
from time import time, timezone
from urllib import request
from django import template
from django.db import models
from django.conf import settings

from django.contrib.auth.models import User
from departamentos.models import Departamento, Subdepartamento, Unidad
import formularioSR
from user.models import UserDepartamento, UserProfile
from cargos.models import Cargo

from django.db.models.functions import Concat
from django.db.models import Q, Value


# Clase para el uso de filtros y llamadas a funciones del Modelo 
register = template.Library()


class FormularioSR(models.Model):
    id_formulario = models.AutoField(primary_key=True)
    folioSR = models.CharField(max_length=50, verbose_name="Folio SR")
    tipo_formulario = models.CharField(max_length=50, choices=settings.TIPO_FORMULARIO, verbose_name="Tipo Formulario")
    rut_solicitante = models.CharField(max_length=50, verbose_name="Rut Solicitante")
    anexo = models.IntegerField(verbose_name="Anexo", default=0, null=True)
    email = models.EmailField(max_length=50, verbose_name="Email")
    fecha_ingreso = models.DateField(default=date.today, verbose_name="Fecha Ingreso")    
    hora_ingreso = models.TimeField(default=time, verbose_name="Hora Ingreso")
    fecha_respuesta = models.DateField(default=date.today, verbose_name="Fecha Respuesta")
    comentarios = models.TextField(verbose_name="Comentario")    
    id_departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, verbose_name="Departamento")
    id_sub_departamento = models.ForeignKey(Subdepartamento, on_delete=models.PROTECT, verbose_name="Sub Departamento", blank=True, null=True)    
    id_unidad = models.ForeignKey(Unidad, on_delete=models.PROTECT, verbose_name="Unidad", blank=True, null=True)
    id_cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, verbose_name="Cargo")
    estado = models.BooleanField(default=True, verbose_name="Estado")   

    class Meta:
        ordering = ['-pk']


    def get_max_id(self):        
        maxId = FormularioSR.objects.all().order_by('-id_formulario').first()

        if (maxId is not None):
            return int(maxId.folioSR.split('/')[0][1:]) + 1
        else:
            return 1


    def save(self, **kwargs):
        
        if not self.id_formulario:   
            maxId = self.get_max_id()
            anio = str(datetime.now().strftime('%Y'))
            folio = "E{:06d}".format(maxId if maxId is not None else 1) + '/' + anio
            
            self.folioSR = folio
            self.hora_ingreso = datetime.now().strftime('%H:%M:%S')
            
            super(FormularioSR, self).save(**kwargs)
            objFSR = FormularioSR.objects.get(folioSR = folio)
            
            SRHistorial = FormularioSRHistorial()
            SRHistorial.id_formulario = objFSR
            SRHistorial.folio_formularioSR = self.folioSR
            SRHistorial.fecha_ingreso = datetime.now().strftime('%Y-%m-%d')
            SRHistorial.hora_ingreso = datetime.now().strftime('%H:%M:%S')
            SRHistorial.estado_solicitud = settings.ESTADO_FORMULARIOSR[0][0]           #ESTADO_FORMULARIO
            SRHistorial.estado = True
            SRHistorial.save()

            if (self.tipo_formulario == 'SOLICITUD'):
                SRDerivacion = FormularioSRDerivacion()
                SRDerivacion.folio_formularioSR = self.folioSR
                SRDerivacion.id_formulario = objFSR
                SRDerivacion.fecha_derivado = datetime.now().strftime('%Y-%m-%d')
                SRDerivacion.hora_derivado = datetime.now().strftime('%H:%M:%S')
                SRDerivacion.save()



    def get_funcionarios_adminterna(name="get_funcionarios_adminterna"):
        #filtro_subdpto = Subdepartamento.objects.filter(id_sub_dpto=2100).values('id')
        filtro_subdpto = Subdepartamento.objects.filter(nombre_sub_dpto__icontains = "ADMINISTRACIÓN INTERNA").values_list('id')
        filtro_unidad = Unidad.objects.filter(subdepartamento=filtro_subdpto[0]).values('id').exclude(id_unidad=2104)
        #print ('filtro_subdpto: ', filtro_subdpto)
        #filtro_unidad = Unidad.objects.filter(subdepartamento=Subdepartamento.objects.get(id_sub_dpto=2100).id).values('id').exclude(id_unidad=2104)
        #print ('filtro_unidad: ', filtro_unidad)
        filtro_usudpto = UserDepartamento.objects.filter(
                                        Q(id_sub_departamento_id__in=filtro_subdpto) |
                                        Q(id_unidad_id__in=filtro_unidad)
                                    ).values('id_usuario_id')
        #print ('filtro_usudpto: ', filtro_usudpto)
        funcionarios = User.objects.filter(id__in=filtro_usudpto)
        #print ('funcionarios: ', funcionarios)
        return funcionarios 




class FormularioSRHistorial(models.Model):
    id_historial = models.AutoField(primary_key=True)
    folio_formularioSR = models.CharField(max_length=50, default='', verbose_name="Folio SR")
    id_formulario = models.ForeignKey(FormularioSR, on_delete=models.PROTECT, verbose_name='Id formularioSR', related_name="srhistorial")
    fecha_ingreso = models.DateField(verbose_name="Fecha Ingreso")    
    hora_ingreso = models.TimeField(verbose_name="Hora Ingreso")
    comentarios = models.TextField(null=True, verbose_name="Respuesta", default='')
    indicaciones = models.TextField(null=True, verbose_name="Indicación", default='')
    estado_solicitud = models.IntegerField(verbose_name="Estado Solicitud", choices=settings.ESTADO_FORMULARIOSR)   
    estado = models.BooleanField(default=True, verbose_name="Estado")  



class FormularioSRDerivacion(models.Model):
    id_derivacion = models.AutoField(primary_key=True)
    folio_formularioSR = models.CharField(max_length=50, default='', verbose_name="Folio SR")
    id_formulario = models.ForeignKey(FormularioSR, on_delete=models.PROTECT, verbose_name='Id formularioSR', related_name="srderivacion")
    rut_derivado = models.CharField(max_length=50, verbose_name="Rut Derivado", blank=True)
    fecha_derivado = models.DateField(verbose_name="Fecha Derivado") 
    hora_derivado = models.TimeField(verbose_name="Hora Derivado")   