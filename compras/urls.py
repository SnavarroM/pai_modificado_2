from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import CompraList, CompraDetail, CompraCreate, CompraUpdate, ExportarExcelFacturas
from . import views

app_name = 'compras'
login_url = '/usuarios/login/'


urlpatterns = [    
    # Proveedores
    path('', login_required(CompraList.as_view(), login_url=login_url), name='index'),
    path('compras-list/', login_required(CompraList.as_view(), login_url=login_url), name='compras-list'),   
    path('compra-create/', login_required(CompraCreate.as_view(), login_url=login_url), name='compra-create'),
    path('compra-update/<int:pk>/', login_required(CompraUpdate.as_view(), login_url=login_url), name='compra-update'),
    path('compra-detail/<int:pk>/', login_required(CompraDetail.as_view(), login_url=login_url), name='compra-detail'),
    path('detalle-delete/<int:pk>/', login_required(views.deleteDetalleInsumo, login_url=login_url), name='detalle-delete'),
    path('ajax/load-precio-promedio/', login_required(views.loadPrecioPromedio, login_url=login_url), name='ajax_load_precio_promedio'),


    # Exportar Excel
    path('facturas-exportar/', login_required(ExportarExcelFacturas, login_url=login_url), name="facturas-exportar"),    
]