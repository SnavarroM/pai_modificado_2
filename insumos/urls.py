from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import CategoriaList, CategoriaCreate, CategoriaDetail, CategoriaUpdate, CategoriaDelete, \
                InsumoList, InsumoDetail, InsumoCreate, InsumoUpdate, InsumoDelete, UnidadMedidaCreate, \
                UnidadMedidaDelete, UnidadMedidaDetail, UnidadMedidaList, UnidadMedidaUpdate, ExportarExcel, \
                ExportarExcelUnidadMedida, ExportarExcelCategorias


app_name = 'insumos'
login_url = '/usuarios/login/'


urlpatterns = [
    # Insumos
    path('', login_required(InsumoList.as_view(), login_url=login_url), name="index"),
    path('insumos-list/', login_required(InsumoList.as_view(), login_url=login_url), name="insumos-list"),
    path('insumo/<int:pk>/', login_required(InsumoDetail.as_view(), login_url=login_url), name="insumo-detail"),
    path('insumo-create/', login_required(InsumoCreate.as_view(), login_url=login_url), name="insumo-create"),
    path('insumo-update/<int:pk>/', login_required(InsumoUpdate.as_view(), login_url=login_url), name="insumo-update"),
    path('insumo-delete/<int:pk>/', login_required(InsumoDelete.as_view(), login_url=login_url), name="insumo-delete"),


    # Categorías
    path('categorias-list/', login_required(CategoriaList.as_view(), login_url=login_url), name="categorias-list"),
    path('categoria/<int:pk>/', login_required(CategoriaDetail.as_view(), login_url=login_url), name="categoria-detail"),
    path('categoria-create/', login_required(CategoriaCreate.as_view(), login_url=login_url), name="categoria-create"),
    path('categoria-update/<int:pk>/', login_required(CategoriaUpdate.as_view(), login_url=login_url), name="categoria-update"),
    path('categoria-delete/<int:pk>/', login_required(CategoriaDelete.as_view(), login_url=login_url), name="categoria-delete"),


    # Unidad de Medidas
    path('unidadmedidas-list/', login_required(UnidadMedidaList.as_view(), login_url=login_url), name="unidadmedidas-list"),
    path('unidadmedida/<int:pk>/', login_required(UnidadMedidaDetail.as_view(), login_url=login_url), name="unidadmedida-detail"),
    path('unidadmedida-create/', login_required(UnidadMedidaCreate.as_view(), login_url=login_url), name="unidadmedida-create"),
    path('unidadmedida-update/<int:pk>/', login_required(UnidadMedidaUpdate.as_view(), login_url=login_url), name="unidadmedida-update"),
    path('unidadmedida-delete/<int:pk>/', login_required(UnidadMedidaDelete.as_view(), login_url=login_url), name="unidadmedida-delete"),


    # Exportar Excel
    path('insumos-exportar/', login_required(ExportarExcel, login_url=login_url), name="insumos-exportar"),
    path('unidadmedida-exportar/', login_required(ExportarExcelUnidadMedida, login_url=login_url), name="unidadmedida-exportar"),
    path('categorias-exportar/', login_required(ExportarExcelCategorias, login_url=login_url), name="categorias-exportar"),
]
