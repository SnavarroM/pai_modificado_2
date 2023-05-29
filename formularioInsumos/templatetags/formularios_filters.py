from django.conf import settings
from django.db.models import Sum, F
from django.db import models
from django import template
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import get_template

from formularioInsumos.models import FormularioHistorial, FormularioInsumo
from insumos.models import Insumo
from inventario.models import Inventario
from user.models import UserProfile

from formularioSR.templatetags import formulariosr_filters
from user.templatetags import users_filters



# Clase para el uso de filtros y llamadas a funciones
register = template.Library()


@register.filter(name="get_edo_solicitud_insumo")
def get_edo_solicitud_insumo(id_formulario):     
    edo_solicitud = FormularioHistorial.objects.filter(id_folio_formulario = id_formulario).order_by('-pk').first()
    return settings.ESTADO_APROBACION_SOLICITUD[edo_solicitud.estado_formulario - 1][1]



@register.filter(name="get_etiqueta_solicitud_insumo")
def get_etiqueta_solicitud_insumo(id_formulario):     
    edo_solicitud = FormularioHistorial.objects.filter(id_folio_formulario = id_formulario).order_by('-pk').first()
    return settings.ETIQUETAS_ESTADOS_FORMULARIOS[edo_solicitud.estado_formulario - 1][1]



@register.filter(name="get_edo_folio_insumo")
def get_edo_folio_insumo(folio):     
    edo_solicitud = FormularioHistorial.objects.filter(id_folio_formulario__folio = folio).order_by('-pk').first()
    return settings.ESTADO_APROBACION_SOLICITUD[edo_solicitud.estado_formulario - 1][1]



@register.filter(name="get_costo_formulario")
def get_costo_formulario(folio):
    solicitud = FormularioInsumo.objects.filter(id_folio = folio).aggregate(costo=Sum( F('cantidad') * F('precio') ))

    if (solicitud['costo'] is not None):    
        return solicitud['costo']
    else:
        return float(0)



@register.filter(name="get_precio_producto")
def get_precio_producto(id_insumo):
    insumo = Insumo.objects.filter(id = id_insumo) 
    return insumo[0].precio



@register.filter(name="set_inventario_solicitud")
def set_inventario_solicitud(id_solicitud, rut_solicitante):
    formInsumo = FormularioInsumo.objects.filter(id_folio = id_solicitud)

    lista_productos = []
    for item in formInsumo:
        lista_productos.append(
            dict(
                codigo_producto = item.id_insumo.codigo_insumo,
                cantidad = item.cantidad_entregada,
                id_folio_entrega = item.id_folio.id_formulario,
                rut_solicitante = rut_solicitante
            )
        )

    return Inventario.InsertarInventarioEntrega(lista_productos, 'S')



@register.filter(name="get_nombre_solicitante")
def get_nombre_solicitante(value):
    if value is not None and ('-' in value):
        userProfile = UserProfile.objects.filter(rut = value)
        return userProfile[0] if userProfile else ''
    else:
        return ''


@register.filter(name="set_formulario_historial")
def set_formulario_historial(self, edoSolicitud):
        SHistorial = FormularioHistorial()
        SHistorial.id_folio_formulario = self.object
        SHistorial.estado_formulario = edoSolicitud
        SHistorial.rut_gestor = self.request.user.userprofile.rut
        SHistorial.estado = True
        SHistorial.save()



@receiver(models.signals.post_save, sender=FormularioInsumo)
def enviar_notificacion_jefatura(sender, instance, created, **kwargs):

    if (instance.id_folio.rut_jefe_aprobador):

        folio = instance.id_folio.folio
        nombre_solicitante = get_nombre_solicitante(instance.id_folio.rut_solicitante)

        titulo = "Formulario de Adquisición de Bienes y/o Servicios"
        cuerpo = "<br>Se ha generado una nueva Solicitud de Adquisición de Bienes y Servicios del funcionario " + str(nombre_solicitante)
        cuerpo += ". Usted debe Aprobar o Rechazar dicha solicitud folio N° <strong>" + folio + "</strong> según su presupuesto.<br>"
        cuerpo += "<br>Favor dar gestión a la brevedad. <br>"
        link = "http://127.0.0.1:8000/usuarios/login/"


        mensaje = get_template("notificacionesCorreo/email_insumos_template.html").render({
                    'folio': folio, 'titulo': titulo, 'cuerpo': cuerpo, 'link': link
        })


        email = EmailMessage(
            titulo, 
            mensaje, 
            "Plataforma PAI " + "<" + settings.EMAIL_HOST_USER + ">",  # Remitente
            ["rsalazar@cenabast.cl"]   # Destinatario
            )
        email.content_subtype = "html" 
        email.send()




@receiver(models.signals.post_save, sender=FormularioInsumo)
def enviar_notificacion_encargado_bodega(sender, instance, created, **kwargs):

    if (instance.id_folio.rut_jefe_aprobador):

        folio = instance.id_folio.folio
        nombre_solicitante = get_nombre_solicitante(instance.id_folio.rut_solicitante)

        titulo = "Formulario de Adquisición de Bienes y/o Servicios"
        cuerpo = "<br>Se ha generado una nueva Solicitud de Adquisición de Bienes y Servicios del funcionario " + str(nombre_solicitante)
        cuerpo += " con folio N° <strong>" + folio + "</strong>.<br>"
        link = "http://127.0.0.1:8000/usuarios/login/"


        mensaje = get_template("notificacionesCorreo/email_insumos_template.html").render({
                    'folio': folio, 'titulo': titulo, 'cuerpo': cuerpo, 'link': link
        })


        email = EmailMessage(
            titulo, 
            mensaje, 
            "Plataforma PAI " + "<" + settings.EMAIL_HOST_USER + ">",  # Remitente
            ["rsalazar@cenabast.cl"]                                    # Destinatario
            )
        email.content_subtype = "html" 
        email.send()




@register.filter(name="enviar_notificacion_aprobacion_jefatura")
def enviar_notificacion_aprobacion_jefatura(instance, instanceForm):

    jefe_admint = formulariosr_filters.get_jefe_admin_interna()

    if (jefe_admint):

        folio = instanceForm.folio
        nombre_solicitante = get_nombre_solicitante(instanceForm.rut_solicitante)
        email_admint = users_filters.get_email_usuario(jefe_admint)

        titulo = "Formulario de Adquisición de Bienes y/o Servicios"
        cuerpo = "<br>He <strong>APROBADO</strong> el formulario de adquisición de bienes y servicios con "
        cuerpo += "folio N° <strong>" + folio + "</strong> del funcionario " + str(nombre_solicitante) + ".<br>"
        cuerpo += "Favor dar curso a la brevedad. <br>"
        
        
        link = "http://127.0.0.1:8000/usuarios/login/"


        mensaje = get_template("notificacionesCorreo/email_insumos_template.html").render({
                    'folio': folio, 'titulo': titulo, 'cuerpo': cuerpo, 'link': link
        })


        email = EmailMessage(
            titulo, 
            mensaje, 
            "Plataforma PAI " + "<" + settings.EMAIL_HOST_USER + ">",  # Remitente
            ["rsalazar@cenabast.cl", email_admint]   # Destinatario
            )
        email.content_subtype = "html" 
        email.send()




@register.filter(name="enviar_notificacion_rechazo")
def enviar_notificacion_rechazo(instance, instanceForm):

    rut_solicitante = instanceForm.rut_solicitante
    
    if (rut_solicitante):

        folio = instanceForm.folio
        nombre_solicitante = get_nombre_solicitante(rut_solicitante)
        email_solicitante = users_filters.get_email_usuario(rut_solicitante)


        titulo = "Formulario de Adquisición de Bienes y/o Servicios"
        cuerpo = "<br>Se ha <strong>RECHAZADO</strong> el formulario de adquisición de bienes y servicios con "
        cuerpo += "folio N° <strong>" + folio + ".<br>"        
        link = "http://127.0.0.1:8000/usuarios/login/"

        mensaje = get_template("notificacionesCorreo/email_insumos_template.html").render({
                    'folio': folio, 'titulo': titulo, 'cuerpo': cuerpo, 'link': link
        })


        email = EmailMessage(
            titulo, 
            mensaje, 
            "Plataforma PAI " + "<" + settings.EMAIL_HOST_USER + ">",   # Remitente
            ["rsalazar@cenabast.cl", email_solicitante]                 # Destinatario
            )
        email.content_subtype = "html" 
        email.send()




@register.filter(name="enviar_notificacion_aprobacion_adminterna")
def enviar_notificacion_aprobacion_adminterna(instance, instanceForm):

    rut_solicitante = instanceForm.rut_solicitante
    
    if (rut_solicitante):

        folio = instanceForm.folio
        nombre_solicitante = get_nombre_solicitante(rut_solicitante)
        email_solicitante = users_filters.get_email_usuario(rut_solicitante)
        tbl_insumos = get_tabla_resumen_solicitud(instanceForm)


        titulo = "Formulario de Adquisición de Bienes y/o Servicios"
        cuerpo = "Administración Interna ha <strong>APROBADO</strong> el formulario de adquisición de bienes y servicios con "
        cuerpo += "folio N° <strong>" + folio + ".<br> Quienes le darán curso a la brevedad.<br>"
        cuerpo += tbl_insumos        
        link = "http://127.0.0.1:8000/usuarios/login/"

        mensaje = get_template("notificacionesCorreo/email_insumos_template.html").render({
                    'folio': folio, 'titulo': titulo, 'cuerpo': cuerpo, 'link': link
        })


        email = EmailMessage(
            titulo, 
            mensaje, 
            "Plataforma PAI " + "<" + settings.EMAIL_HOST_USER + ">",   # Remitente
            ["rsalazar@cenabast.cl", email_solicitante]                 # Destinatario
            )
        email.content_subtype = "html" 
        email.send()




@register.filter(name="get_tabla_resumen_solicitud")
def get_tabla_resumen_solicitud(instance):

    tblInsumos = FormularioInsumo.objects.filter(id_folio = instance.id_formulario)
    
    str_table = "<table style='border:solid 1px; border-collapse: collapse; text-align:center'><thead style='font-weight:bold; background-color:#eee'>"
    str_table += "<tr><td style='border:solid 1px; padding:5px'>Insumo</td><td style='border:solid 1px; padding:5px'>Cant. Solicitada</td><td style='border:solid 1px; padding:5px'>Cant. Enviada</td><td style='border:solid 1px; padding:5px'>Diferencia</td></tr>"
    str_table += "<tbody>"

    for item in tblInsumos:
        str_table += "<tr>"
        str_table += "<td style='border:solid 1px; padding:5px'>" + item.id_insumo.denominacion + "</td>"
        str_table += "<td style='border:solid 1px; padding:5px'>" + str(item.cantidad) + "</td>"
        str_table += "<td style='border:solid 1px; padding:5px'>" + str(item.cantidad_entregada) + "</td>"
        str_table += "<td style='border:solid 1px; padding:5px'>" + str(item.cantidad - item.cantidad_entregada) + "</td>"
        str_table += "</tr>"

    str_table += "</tbody></table>"
    return str_table