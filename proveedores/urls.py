from django.urls import path
from .views import ProveedorList, ProveedorCreate, ProveedorUpdate, ProveedorDelete, ExportarExcel
from django.contrib.auth.decorators import login_required


app_name = 'proveedores'
login_url = '/usuarios/login/'

urlpatterns = [    

    # Proveedores
    path('', ProveedorList.as_view(), name="index"),
    path('proveedores-list/', login_required(ProveedorList.as_view(), login_url=login_url), name="proveedores-list"),   
    path('proveedor-create/', login_required(ProveedorCreate.as_view(), login_url=login_url), name="proveedor-create"),
    path('proveedor-update/<int:pk>/', login_required(ProveedorUpdate.as_view(), login_url=login_url), name="proveedor-update"),
    path('proveedor-delete/<int:pk>/', login_required(ProveedorDelete.as_view(), login_url=login_url), name="proveedor-delete"),

    # Exportar Excel
    path('proveedores-exportar/', login_required(ExportarExcel, login_url=login_url), name="proveedores-exportar"),
]