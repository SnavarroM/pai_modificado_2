from django.contrib import admin
from .models import Categoria, UnidadMedida, Insumo

class CategoriaAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in Categoria._meta.fields]
    
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in UnidadMedida._meta.fields]
    
# class EstadoAdmin(admin.ModelAdmin):
#     list_display = [field.attname for field in Estado._meta.fields]
    
class InsumoAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in Insumo._meta.fields]
    
    
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(UnidadMedida, UnidadMedidaAdmin)
#admin.site.register(Estado, EstadoAdmin)
admin.site.register(Insumo, InsumoAdmin)