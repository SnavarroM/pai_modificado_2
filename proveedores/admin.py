from django.contrib import admin
from .models import Proveedor


class ProveedorAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in Proveedor._meta.fields]


admin.site.register(Proveedor, ProveedorAdmin)