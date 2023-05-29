import socket
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone




class Log(models.Model):
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    cantidad = models.IntegerField(verbose_name="Cantidad") 
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuario")
    ip_usuario = models.GenericIPAddressField(verbose_name="IP Usuario")
    fecha_log = models.DateTimeField(default=timezone.now, verbose_name="Fecha")


    def __str__(self):
        return self.descripcion



    def get_ip_address():
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address



    def InsertarLog(usuario, descripcion, cantidad):
        ipusuario = Log.get_ip_address()

        log = Log(descripcion=descripcion, cantidad=cantidad, usuario=usuario, ip_usuario=ipusuario)
        log.save()
        return log
