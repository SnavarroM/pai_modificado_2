from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import home, RegisterView, CustomLoginView
from .views import UsuariosList, PerfilList, PerfilCreate, PerfilUpdate, PerfilDelete, \
    GestionPerfilUpdate, LogoutView, ExportarExcelFuncionarios, MainView
from . import views


app_name = 'user'
login_url = '/usuarios/login/'


urlpatterns = [  

    #Registro/Login
    #path('',home.as_view(),name='home'),
    path('registro/', RegisterView.as_view(), name='registro'),
    path('usuarios-list/', login_required(UsuariosList.as_view(), login_url=login_url), name="usuarios-list"),
    path('login/', CustomLoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('main/', MainView.as_view(), name="main"),


    #Perfiles
    path('perfiles-list/', login_required(PerfilList.as_view(), login_url=login_url), name="perfiles-list"),
    path('perfil-create/', login_required(PerfilCreate.as_view(), login_url=login_url), name="perfil-create"),
    path('perfil-update/<int:pk>/', login_required(PerfilUpdate.as_view(), login_url=login_url), name="perfil-update"),
    path('perfil-gestion/<int:pk>/', login_required(GestionPerfilUpdate.as_view(), login_url=login_url), name="perfil-gestion"),
    path('perfil-delete/<int:pk>/', login_required(PerfilDelete.as_view(), login_url=login_url), name="perfil-delete"),
    path('ajax/load-subdptos/', views.loadSubDepartamentos, name='ajax_load_subdptos'),
    path('ajax/load-unidades/', views.loadUnidades, name='ajax_load_unidades'),


    # Exportar Excel
    path('funcionarios-exportar/', login_required(ExportarExcelFuncionarios, login_url=login_url), name="funcionarios-exportar"), 
]
