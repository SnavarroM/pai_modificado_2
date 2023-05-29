from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import CargoList, CargoDetail, CargoCreate, CargoUpdate, CargoDelete, \
    ExportarExcel


app_name = 'cargos'
login_url = '/usuarios/login/'


urlpatterns = [    
    
    # Cargo
    path('', login_required(CargoList.as_view(), login_url=login_url), name="index"),
    path('cargos-list/', login_required(CargoList.as_view(), login_url=login_url), name="cargos-list"),
    path('cargo/<int:pk>/', login_required(CargoDetail.as_view(), login_url=login_url), name="cargo-detail"),
    path('cargo-create/', login_required(CargoCreate.as_view(), login_url=login_url), name="cargo-create"),
    path('cargo-update/<int:pk>/', login_required(CargoUpdate.as_view(), login_url=login_url), name="cargo-update"),
    path('cargo-delete/<int:pk>/', login_required(CargoDelete.as_view(), login_url=login_url), name="cargo-delete"),
    
    # Exportar Excel
    path('cargos-exportar/', login_required(ExportarExcel, login_url=login_url), name="cargos-exportar"),
]