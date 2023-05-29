from django.contrib import admin
from .models import Compra, CompraInsumo


class CompraAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in Compra._meta.fields]


class CompraInsumoAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in CompraInsumo._meta.fields]


admin.site.register(Compra, CompraAdmin)
admin.site.register(CompraInsumo, CompraInsumoAdmin)