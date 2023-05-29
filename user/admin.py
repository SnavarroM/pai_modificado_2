from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, Perfil, UserDepartamento, UserCargo


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )


class PerfilAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in Perfil._meta.fields]


class UserDepartamentoAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in UserDepartamento._meta.fields]


class UserCargoAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in UserCargo._meta.fields]



admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(UserProfile)
admin.site.register(Perfil, PerfilAdmin)
admin.site.register(UserDepartamento, UserDepartamentoAdmin)
admin.site.register(UserCargo, UserCargoAdmin)