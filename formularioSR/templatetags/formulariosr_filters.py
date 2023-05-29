import datetime
from datetime import datetime
from django.conf import settings
from django.db import models
from django import template
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import get_template

from departamentos.models import Subdepartamento
from formularioSR.models import FormularioSR, FormularioSRHistorial
from formularioInsumos.templatetags import formularios_filters

from user.models import UserProfile
from user.templatetags import users_filters


# Clase para el uso de filtros y llamadas a funciones
register = template.Library()



@register.filter(name="get_tiempo_respuesta")
def get_tiempo_respuesta(folio):
    historial = FormularioSRHistorial.objects.filter(folio_formularioSR = folio).exclude(estado_solicitud = 1).order_by('-pk').first()
    if (historial):
        fecha_ultima_resp = datetime.combine(historial.fecha_ingreso, historial.hora_ingreso)
        return fecha_ultima_resp        
    else:
        return ""



@register.filter(name="get_estado_solicitud")
def get_estado_solicitud(id_formulario):      
    edo_solicitud = FormularioSRHistorial.objects.filter(id_formulario = id_formulario).order_by('-pk').first()

    if (edo_solicitud):
        return settings.ESTADO_FORMULARIOSR[edo_solicitud.estado_solicitud - 1][1]
    else:
        return ""



@register.filter(name="get_etiqueta_solicitud")
def get_etiqueta_solicitud(id_formulario):      
    edo_solicitud = FormularioSRHistorial.objects.filter(id_formulario = id_formulario).order_by('-pk').first()

    if (edo_solicitud):
        return settings.ETIQUETAS_ESTADOS_FORMULARIOS[edo_solicitud.estado_solicitud - 1][1]
    else:
        return ""



@register.filter(name="get_fecha_hora_ingreso")
def get_fecha_hora_ingreso(folio):
    SRIngreso = FormularioSR.objects.filter(folioSR = folio).values_list('fecha_ingreso', 'hora_ingreso').first()
    if (SRIngreso):  
        fecha_hora = datetime.combine(SRIngreso[0], SRIngreso[1])
        return fecha_hora.strftime('%d-%m-%Y %H:%M:%S')
    else:
        return ""


@register.filter(name="get_difer_fechas")
def get_difer_fechas(fecha_ingreso, fecha_respuesta):

    if (isinstance(fecha_ingreso, str)):
        ingreso = datetime.strptime(fecha_ingreso, "%d-%m-%Y %H:%M:%S")
        fecha_ingreso = datetime.strptime(str(ingreso), "%Y-%m-%d %H:%M:%S")

    if (isinstance(fecha_respuesta, str)):
        if (fecha_respuesta.startswith("E")):
            folio = fecha_respuesta
            respuesta = get_tiempo_respuesta(folio)   

            if (respuesta == ""):
                return "0 días"
            else:
                fecha_respuesta = respuesta
    return str(abs(fecha_respuesta - fecha_ingreso).days) + ' días'


@register.filter(name="get_jefe_admin_interna")
def get_jefe_admin_interna():
    admin_interna = Subdepartamento.objects.filter(nombre_sub_dpto__icontains = "ADMINISTRACIÓN INTERNA")
    if (admin_interna):
        if admin_interna[0].rut_jefe is not None:
            jefe_admint = admin_interna[0].rut_jefe

    return jefe_admint




@receiver(models.signals.post_save, sender=FormularioSR)
def enviar_notificacion_ingreso(sender, instance, created, **kwargs):

    jefe_admint = get_jefe_admin_interna()
    
    if (jefe_admint):

        folio = instance.folioSR
        email_admint = users_filters.get_email_usuario(jefe_admint)
        tipo_formulario = instance.tipo_formulario
        
        titulo = "Formulario de Solicitudes y Reclamos"
        cuerpo = "Se ha generado un nuevo formulario " + tipo_formulario + " con folio N° <strong> " + folio + " </strong>"
        cuerpo += "<br>Usted debe dar gestión ingresando al sistema.<br>"
        link = "http://127.0.0.1:8000/usuarios/login/"


        mensaje = get_template("notificacionesCorreo/email_insumos_template.html").render({
                    'folio': folio, 'titulo': titulo, 'cuerpo': cuerpo, 'link': link
        })


        email = EmailMessage(
            titulo, 
            mensaje, 
            "Plataforma PAI " + "<" + settings.EMAIL_HOST_USER + ">",  # Remitente
            ["rsalazar@cenabast.cl"]                                   # Destinatario
            )
        email.content_subtype = "html" 
        email.send()




@register.filter(name="enviar_notificacion_derivacion")
def enviar_notificacion_derivacion(instance, instanceDerivacion, instanceHistorial):

    # print("inst: ", instance)
    # print("instDeriv: ", instanceDerivacion)
    # print("instHist: ", instanceHistorial)

    ejecutivo_derivado = instanceDerivacion['srderivacion-0-rut_derivado']

    if (ejecutivo_derivado):
        
        folio = instance.folioSR
        indicaciones = instanceDerivacion['srhistorial-0-indicaciones']
        nombre_solicitante = formularios_filters.get_nombre_solicitante(ejecutivo_derivado)
        email_derivado = users_filters.get_email_usuario(ejecutivo_derivado)

        # print ("nombre: ", nombre_solicitante)
        # print ("folio: ", folio)
        # print ("indicaciones: ", indicaciones)
        # print ("email_deriv: ", email_derivado)

        titulo = "Formulario de Solicitudes y Reclamos"
        cuerpo = "<br>Dar gestión a la <strong>SOLICITUD</strong> folio N° <strong>" + folio + " </strong> del funcionario "
        cuerpo += str(nombre_solicitante) + ".<br>" + str(indicaciones) + "<br> Revisar ingresando al sistema."
        cuerpo += "Favor dar curso a la brevedad. <br>"
        
        
        link = "http://127.0.0.1:8000/usuarios/login/"


        mensaje = get_template("notificacionesCorreo/email_insumos_template.html").render({
                    'folio': folio, 'titulo': titulo, 'cuerpo': cuerpo, 'link': link
        })


        email = EmailMessage(
            titulo, 
            mensaje, 
            "Plataforma PAI " + "<" + settings.EMAIL_HOST_USER + ">",  # Remitente
            ["rsalazar@cenabast.cl", email_derivado]                   # Destinatario
            )
        email.content_subtype = "html" 
        email.send()




@register.filter(name="enviar_notificacion_respuesta_solicitante")
def enviar_notificacion_respuesta_solicitante(instance):

        # print("inst: ", instance)
        # print("form: ", instance.cleaned_data['id_formulario'])
        # print("folio: ", instance.cleaned_data['id_formulario'].folioSR)
        
        folio = instance.cleaned_data['id_formulario'].folioSR
        comentarios = instance.data['srhistorial-0-comentarios']
        rut_solicitante = instance.data['rut_solicitante'][0]
        nombre_solicitante = formularios_filters.get_nombre_solicitante(rut_solicitante)
        email_solicitante = users_filters.get_email_usuario(rut_solicitante)

        # print ("nombre: ", nombre_solicitante)
        # print ("folio: ", folio)
        # print ("comentarios: ", comentarios)
        # print ("email_deriv: ", email_solicitante)

        titulo = "Formulario de Solicitudes y Reclamos"
        cuerpo = "<br>Respuesta: " + str(comentarios) + "<br><br>"
        cuerpo += "Usted puede dar seguimiento ingresando al sistema."        
        link = "http://127.0.0.1:8000/usuarios/login/"


        mensaje = get_template("notificacionesCorreo/email_insumos_template.html").render({
                    'folio': folio, 'titulo': titulo, 'cuerpo': cuerpo, 'link': link
        })


        email = EmailMessage(
            titulo, 
            mensaje, 
            "Plataforma PAI " + "<" + settings.EMAIL_HOST_USER + ">",     # Remitente
            ["rsalazar@cenabast.cl", email_solicitante]                   # Destinatario
            )
        email.content_subtype = "html" 
        email.send()