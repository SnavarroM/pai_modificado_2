from django.contrib import admin
from .models import PresupuestoDepartamento, PresupuestoSubDepartamento, PresupuestoCategoria



class PresupuestoCategoriaAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in PresupuestoCategoria._meta.fields]
    
    
admin.site.register(PresupuestoCategoria, PresupuestoCategoriaAdmin)



class PresupuestoDepartamentoAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in PresupuestoDepartamento._meta.fields]
    
    
admin.site.register(PresupuestoDepartamento, PresupuestoDepartamentoAdmin)



class PresupuestoSubDepartamentoAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in PresupuestoSubDepartamento._meta.fields]
    
    
admin.site.register(PresupuestoSubDepartamento, PresupuestoSubDepartamentoAdmin)
