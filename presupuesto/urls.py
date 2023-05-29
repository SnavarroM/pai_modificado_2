from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import  PresupuestoCategoriaList, PresupuestoCategoriaCreate, PresupuestoCategoriaUpdate, \
                    AsignacionPresupuesto, AsignacionPresupuestoUpdate, \
                    ExportarExcelCtasPresupuestarias, ExportarExcelAsignacionPresupuesto
from . import views


app_name = 'presupuesto'
login_url = '/usuarios/login/'


urlpatterns = [
    
    # Cuenta Presupuestaria
    path('', login_required(PresupuestoCategoriaList.as_view(), login_url=login_url), name="index"),
    path('cuentas-list/', login_required(PresupuestoCategoriaList.as_view(), login_url=login_url), name="cuentas-list"),
    path('cuenta-create/', login_required(PresupuestoCategoriaCreate.as_view(), login_url=login_url), name="cuenta-create"),
    path('cuenta-update/<int:pk>/', login_required(PresupuestoCategoriaUpdate.as_view(), login_url=login_url), name="cuenta-update"),


    # Asignación de Presupuesto
    #path('presupuesto-create/', AsignacionPresupuesto.as_view(), name="presupuesto-create"),
    path('presupuesto-update/<int:pk>/', login_required(AsignacionPresupuestoUpdate.as_view(), login_url=login_url), name='presupuesto-update'),
    path('ajax/load-montopresupuestario/', views.loadMontoPresupuestario, name='ajax_load_montopresupuestario'),


    # Exportar Excel
    path('cuentas-exportar/', login_required(ExportarExcelCtasPresupuestarias, login_url=login_url), name="cuentas-exportar"), 
    path('presupuesto-exportar/<int:pk>/', login_required(ExportarExcelAsignacionPresupuesto, login_url=login_url), name="presupuesto-exportar"), 
]