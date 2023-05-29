import email
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import template
from django.conf import settings

from departamentos.models import Departamento, Subdepartamento, Unidad
from cargos.models import Cargo


# Clase para el uso de filtros y llamadas a funciones del Modelo 
register = template.Library()



class Perfil(models.Model):
    nombre_perfil = models.CharField(max_length=50, verbose_name="Nombre Perfil")
    estado = models.BooleanField(default=True, verbose_name="Estado")


    class Meta:
        ordering = ['id']


    def __str__(self):
        return self.nombre_perfil


    def get_default_Perfil(self):
        return self.objects.get(id=2).id


    @register.filter(name="get_estado_perfil")
    def get_estado_perfil(self):     
        edo_perfil = Perfil.objects.filter(id = self.id)
        return settings.ESTADO[0][edo_perfil[0].estado]



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile", verbose_name="Usuario")
    rut = models.CharField(max_length=20, verbose_name="Rut", unique=True)   
    anexo = models.IntegerField(default=0, blank=True, null=True, verbose_name="Anexo")
    estado = models.BooleanField(default=True, verbose_name="Estado")
    id_perfil = models.ForeignKey(Perfil, on_delete=models.PROTECT, verbose_name="Perfil", default=Perfil.get_default_Perfil(Perfil))


    class Meta:
        ordering = ['id']


    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)


    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.userprofile.save()


    @register.filter(name="get_estado_user")
    def get_estado_user(self):     
        edo_user = UserProfile.objects.filter(id = self.id)
        return settings.ESTADO[0][edo_user[0].estado]


    @register.filter(name="get_cargo_user")
    def get_cargo_user(self):     
        cargo = UserCargo.objects.filter(id_usuario = self.user).values_list('id_cargo__nombre_cargo')
        return cargo[0][0] if cargo else ''


    # def login_user(request):

    #     if request.method == "POST":
    #         username = request.POST.get('username')
    #         password = request.POST.get('password')
    #         user = authenticate(username=username, password=password)
    
    #         if user is not None:
    #             if user.is_active:
    #                 login(request, user)
    
    #                 return HttpResponseRedirect('/user/login.html')
    #             else:
    #                 return HttpResponse("Inactive user.")
    #         else:
    #             return HttpResponseRedirect(settings.LOGIN_URL)
    
    #     return render(request, "index.html")



class UserDepartamento(models.Model):
    id_departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, verbose_name="Departamento", related_name="usuario_dpto", blank=True, null=True)
    id_sub_departamento = models.ForeignKey(Subdepartamento, on_delete=models.PROTECT, verbose_name="Sub Departamento", related_name="usuario_subdpto", blank=True, null=True)
    id_unidad = models.ForeignKey(Unidad, on_delete=models.PROTECT, verbose_name="Unidad", related_name="usuario_unidad", blank=True, null=True)
    id_usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="usuario_id_dpto", related_name="usuario_id_dpto")



class UserCargo(models.Model):
    id_cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, verbose_name="Cargo", related_name="cargo", default=1)
    id_usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuario", related_name="usuario_cargo")
    fecha_activacion = models.DateField(verbose_name="Fecha Activación", null=True, blank=True)
    fecha_desactivacion = models.DateField(verbose_name="Fecha Desactivación", null=True, blank=True)
    estado = models.BooleanField(default=True, verbose_name="Estado")