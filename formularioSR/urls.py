from django.urls import path
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from .views import ExportarExcelFormularioSR


app_name = 'formularioSR'
login_url = '/usuarios/login/'


urlpatterns = [
    
    # Formulario Solicitud Insumos
    path('', login_required(views.FormularioSRList.as_view(), login_url=login_url), name="index"),
    path('formulariosr-list/', login_required(views.FormularioSRList.as_view(), login_url=login_url), name="formulariosr-list"),
    path('formulariosr-detail/<int:pk>/', login_required(views.FormularioSRDetail.as_view(), login_url=login_url), name="formulariosr-detail"),
    path('formulariosr-solicitud/<int:pk>/', login_required(views.FormularioSRSolicitudUpdate.as_view(), login_url=login_url), name="formulariosr-solicitud"),
    path('formulariosr-reclamo/<int:pk>/', login_required(views.FormularioSRReclamoUpdate.as_view(), login_url=login_url), name="formulariosr-reclamo"),
    path('formulariosr-create/', login_required(views.FormularioSRCreate.as_view(), login_url=login_url), name="formulariosr-create"),

    path('formulariosr-cierre/<int:pk>/<int:edo>/', login_required(views.FormularioSRCierre.as_view(), login_url=login_url), name="formulariosr-cierre"),

    # Exportar Excel
    path('formulariosr-exportar/', login_required(ExportarExcelFormularioSR, login_url=login_url), name="formulariosr-exportar"),  
]