from django.db import models
from django import template
from django.dispatch import receiver
from user.models import UserCargo, UserProfile, UserDepartamento
from django.contrib.auth.models import User


# Clase para el uso de filtros y llamadas a funciones
register = template.Library()



@register.filter(name="get_nombre_usuario")
def get_nombre_usuario(value):
    userProfile = UserProfile.objects.filter(user__username = value)
    return userProfile[0] if userProfile else ''



@register.filter(name="get_cargo")
def get_cargo(value):
    userCargo = UserCargo.objects.filter(id_usuario = value)
    return userCargo[0].id_cargo if userCargo else ''



@register.filter(name="get_perfil")
def get_perfil(value):
    userPerfil = UserProfile.objects.filter(user = value)
    return userPerfil[0].id_perfil if userPerfil else ''



@register.filter(name="get_perfil_id")
def get_perfil_id(value):
    userPerfil = UserProfile.objects.filter(user = value)
    return userPerfil[0].id_perfil.id if userPerfil else ''



@register.filter(name="get_email_usuario")
def get_email_usuario(value):
    user_datos = UserProfile.objects.filter(rut = value)
    return user_datos[0].user.email if user_datos else ''



@register.filter(name="get_usuario_departamento")
def get_usuario_departamento(value):

    user_dpto = UserDepartamento.objects.filter(id_usuario = value)
    print(user_dpto[0].id_departamento)
    return user_dpto[0].id_departamento if user_dpto else ''