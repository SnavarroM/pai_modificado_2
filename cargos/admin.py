from django.contrib import admin
from .models import Cargo

class CargoAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in Cargo._meta.fields]
    
    
admin.site.register(Cargo, CargoAdmin)
