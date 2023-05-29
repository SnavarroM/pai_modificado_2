from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import DptoListView, DptoCreateView, DptoUpdateView, \
                  SubDptoListView, SubDptoCreateView, SubDptoUpdateView, \
                  UnidadListView, UnidadCreateView, UnidadUpdateView, \
                  ExportarExcelDptos, ExportarExcelSubDptos, ExportarExcelUnidades 

app_name = 'departamentos'
login_url = '/usuarios/login/'


urlpatterns = [
   
   #Departamentos
   path('', login_required(DptoListView.as_view(), login_url=login_url), name='dptos-list'),
   path('dptos-list/', login_required(DptoListView.as_view(), login_url=login_url), name='dptos-list'),
   path('dpto-create/', login_required(DptoCreateView.as_view(), login_url=login_url), name='dpto-create'),
   path('dpto-update/<int:pk>/', login_required(DptoUpdateView.as_view(), login_url=login_url), name='dpto-update'),


   #SubDepartamentos
   path('subdptos-list/', login_required(SubDptoListView.as_view(), login_url=login_url), name='subdptos-list'),
   path('subdpto-create/', login_required(SubDptoCreateView.as_view(), login_url=login_url), name='subdpto-create'),
   path('subdpto-update/<int:pk>/', login_required(SubDptoUpdateView.as_view(), login_url=login_url), name='subdpto-update'),


   #Unidadeds   
   path('unidades-list/', login_required(UnidadListView.as_view(), login_url=login_url), name='unidades-list'),
   path('unidad-create/', login_required(UnidadCreateView.as_view(), login_url=login_url), name='unidad-create'),
   path('unidad-update/<int:pk>/', login_required(UnidadUpdateView.as_view(), login_url=login_url), name='unidad-update'),


   # Exportar Excel
   path('departamentos-exportar/', login_required(ExportarExcelDptos, login_url=login_url), name="departamentos-exportar"),
   path('subdepartamentos-exportar/', login_required(ExportarExcelSubDptos, login_url=login_url), name="subdepartamentos-exportar"),
   path('unidades-exportar/', login_required(ExportarExcelUnidades, login_url=login_url), name="unidades-exportar"),
]
