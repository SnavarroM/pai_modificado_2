from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import FormularioInsumoCreate, FormularioInsumoList, FormularioInsumoJefatura, \
                FormularioInsumoAdminInterna, FormularioInsumoBodega
from . import views
from .views import ExportarExcelFormulario


app_name = 'formularioInsumos'
login_url = '/usuarios/login/'


urlpatterns = [

    # Formulario Solicitud Insumos
    path('', login_required(FormularioInsumoList.as_view(), login_url=login_url), name="index"),
    path('formularios-list/', login_required(FormularioInsumoList.as_view(), login_url=login_url), name="formularios-list"),
    #path('insumo/<int:pk>/', InsumoDetail.as_view(), name="insumo-detail"),
    path('formulario-create/', login_required(FormularioInsumoCreate.as_view(), login_url=login_url), name="formulario-create"),    
    path('formulario-jefatura/<int:pk>/', login_required(FormularioInsumoJefatura.as_view(), login_url=login_url), name="formulario-jefatura"),
    path('formulario-adminiterna/<int:pk>/', login_required(FormularioInsumoAdminInterna.as_view(), login_url=login_url), name="formulario-adminiterna"),
    path('formulario-bodega/<int:pk>/', login_required(FormularioInsumoBodega.as_view(), login_url=login_url), name="formulario-bodega"),
    path('ajax/insumos-sinstock/', login_required(views.InsumossinStock, login_url=login_url), name='ajax_insumos_sinstock'), 

    # Exportar Excel
    path('formularios-exportar/', login_required(ExportarExcelFormulario, login_url=login_url), name="formularios-exportar"), 
]