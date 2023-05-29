from django.contrib import admin
from .models import Unidad, Subdepartamento, Departamento

class DepartamentoAdmin(admin.ModelAdmin):
    model = Departamento
    list_display = ['id_dpto','nombre_dpto','estado']
    ordering = ['id_dpto','nombre_dpto']
    search_fields = ['id_dpto','nombre_dpto']
    
admin.site.register(Departamento,DepartamentoAdmin)  

# --------------------------------------------------------------------------  

class SubdepartamentoAdmin(admin.ModelAdmin):
    model = Subdepartamento
    list_display = ['id_sub_dpto','departamento','nombre_sub_dpto','estado']
    ordering = ['id_sub_dpto','departamento','nombre_sub_dpto']
    search_fields = ['id_sub_dpto','nombre_sub_dpto']

admin.site.register(Subdepartamento,SubdepartamentoAdmin)
# -------------------------------------------------------------------------- 

class UnidadAdmin(admin.ModelAdmin):
    model = Unidad
    list_display = ['id_unidad','subdepartamento','nombre_unidad','estado']
    ordering = ['id_unidad','subdepartamento','nombre_unidad']
    search_fields = ['id_unidad','nombre_unidad']

admin.site.register(Unidad,UnidadAdmin)