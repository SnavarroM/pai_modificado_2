from django.urls import path
from django.contrib.auth.decorators import login_required


from .views import CierreMensualReport, CierreMensualExportarExcel, SolicitudesReport, \
                SolicitudesExportarExcel, InventarioReport, InventarioExportarExcel, GenerarComprobantePDF


app_name = 'reportes'
login_url = '/usuarios/login/'

urlpatterns = [

    ##  Cierre Mensual  ##    
    path('cierremensual-report/', login_required(CierreMensualReport.as_view(), login_url=login_url), name="cierremensual-report"),
    path('cierremensual-exportar/<int:id>', login_required(CierreMensualExportarExcel, login_url=login_url), name="cierremensual-exportar"),


    ##  Solicitudes  ##
    path('solicitudes-report/', login_required(SolicitudesReport.as_view(), login_url=login_url), name="solicitudes-report"),
    path('solicitudes-exportar/', login_required(SolicitudesExportarExcel, login_url=login_url), name="solicitudes-exportar"),


    ##  Inventario  ##
    path('inventario/', login_required(InventarioReport.as_view(), login_url=login_url), name="inventario-report"),
    path('inventario-exportar/', login_required(InventarioExportarExcel, login_url=login_url), name="inventario-exportar"),

    ##  Comprobante de Solicitud PDF    ##
    path('form-insumo/<int:id>/', login_required(GenerarComprobantePDF, login_url=login_url), name='form-insumo'),
]
