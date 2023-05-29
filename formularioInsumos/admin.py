from django.contrib import admin
from .models import Formulario

class FormularioAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in Formulario._meta.fields]
        
    
admin.site.register(Formulario, FormularioAdmin)