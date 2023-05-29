from import_export import resources
from .models import Insumo

class InsumoResource(resources.ModelResource):
    class Meta:
        model = Insumo