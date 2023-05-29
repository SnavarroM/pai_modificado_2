from django.urls import path
from .views import CierreInsumo
from django.contrib.auth.decorators import login_required

app_name = 'cierreMensual'
login_url = '/usuarios/login/'


urlpatterns = [    
    path('', login_required(CierreInsumo, login_url=login_url), name="index"),
    path('cierre/', login_required(CierreInsumo, login_url=login_url), name="cierre"),
]