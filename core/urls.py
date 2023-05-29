from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', include('insumos.urls', namespace="insumos")),
    path('departamentos/', include('departamentos.urls', namespace="departamentos")),
    path('usuarios/', include('user.urls', namespace="usuarios")),
    path('formularios/', include('formularioInsumos.urls', namespace="formularios")),
    path('cargos/', include('cargos.urls', namespace="cargos")),
    path('formulariosr/', include('formularioSR.urls', namespace="formulariosr")),
    path('proveedores/', include('proveedores.urls', namespace="proveedores")),
    path('compras/', include('compras.urls', namespace="compras")),
    path('presupuesto/', include('presupuesto.urls', namespace="presupuestos")),
    path('cierremensual/', include('cierreMensual.urls', namespace="cierremensual")),
    path('configuraciones/', include('configuraciones.urls', namespace="configuraciones")),
    path('logs/', include('logs.urls', namespace="logs")),
    path('inventario/', include('inventario.urls', namespace="inventario")),
    path('reportes/', include('reportes.urls', namespace="reportes")),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


handler404 = 'user.views.error_404'
handler403 = 'user.views.error_403'