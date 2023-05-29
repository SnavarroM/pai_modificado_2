from django.contrib import admin
from .models import FormularioSR, FormularioSRHistorial, FormularioSRDerivacion


class FormularioSRAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in FormularioSR._meta.fields]


class FormularioSRHistorialAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in FormularioSRHistorial._meta.fields]


class FormularioSRDerivacionAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in FormularioSRDerivacion._meta.fields]


admin.site.register(FormularioSR, FormularioSRAdmin)
admin.site.register(FormularioSRHistorial, FormularioSRHistorialAdmin)
admin.site.register(FormularioSRDerivacion, FormularioSRDerivacionAdmin)