import xlwt
import datetime

from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from user.models import UserDepartamento, UserProfile, UserCargo, Perfil
from departamentos.models import Departamento, Subdepartamento, Unidad
from cargos.models import Cargo
from logs.models import Log

from .forms import RegisterForm, UserDepartamentoForm, UsuarioForm
from .forms import UsuarioForm, PerfilForm, UserProfileForm, UserDepartamentoForm, UserCargoForm, LoginForm

from extra_views import UpdateWithInlinesView, InlineFormSetFactory




# Registro / Login
class home(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            context = {}
            return render(request, 'user/home.html', context)
        else:
            return HttpResponseRedirect(reverse_lazy('user:login'))



class MainView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'user/main.html', context)




class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'registration/registro.html'


    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})


    def post(self, request):
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():

                user = form.save()
                user.refresh_from_db()                                      #load the profile instance created by the signal
                user.userprofile.rut = form.cleaned_data.get('rut')
                user.userprofile.anexo = form.cleaned_data.get('anexo')
                user.save()
                
                group = Group.objects.get(name=user.userprofile.id_perfil)
                user.groups.add(group)

                objUsuario = UserProfile.objects.get(user = user.id)
                
                UDpto = UserDepartamento()
                UDpto.id_usuario_id = objUsuario.user_id                
                #UDpto.id_departamento_id = 1
                #UDpto.id_sub_departamento_id = 1
                #UDpto.id_unidad_id = 1
                UDpto.save()

                UCargo = UserCargo()
                UCargo.id_usuario_id = objUsuario.user_id            
                UCargo.id_cargo_id = Cargo.objects.get(id=3).id
                UCargo.save()
                
                Log.InsertarLog(user, 'Se registró un nuevo Usuario Id ' + str(user.id) + " - " + user.username, 0)    
                                
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=user.username, password=raw_password)
                login(request, user)
                    
                return HttpResponseRedirect(reverse_lazy('user:main'))
        else:
            form = RegisterForm()
        return render(request, self.template_name, {'form': form})



class CustomLoginView(View):
    model = User
    form_class = LoginForm
    template_name = "user/login.html"
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})


    def post(self, request):
        
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")        
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)              
                return HttpResponseRedirect(reverse_lazy('user:main'))

        return render(request, "user/login.html", {})    



class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse_lazy('user:login')) 


class UsuariosList(PermissionRequiredMixin, ListView):
    permission_required = ("user.view_user")
    
    model = UserProfile
    template_name = 'user/usuarios_list.html'
        
    paginate_by = 10
    context_object_name = 'userprofiles'

    def get_queryset(self):
            # QuerySet por defecto
            queryset = UserProfile.objects.all()
            # Check the form value is submitted or not
            if self.request.GET.keys():
                # Verifica campo de búsqueda
                if self.request.GET.get('buscar') != None:
                    keyword = self.request.GET.get('buscar')
                    # Query filtrado por término de búsqueda (nombre, apellido, username, email, cargo, perfil, rut)

                    filtro_user = User.objects.filter(
                                                    Q(first_name__icontains=keyword) |
                                                    Q(last_name__icontains=keyword) |
                                                    Q(username__icontains=keyword) |
                                                    Q(email__icontains=keyword)
                                                )

                    filtro_cargo = UserCargo.objects.filter(id_cargo__in= Cargo.objects.filter(nombre_cargo__icontains=keyword)).values('id_usuario')
                    filtro_perfil = Perfil.objects.filter(nombre_perfil__icontains=keyword)

                    queryset = UserProfile.objects.filter(
                                                    Q(user__in=filtro_user) | 
                                                    Q(user__in=filtro_cargo) |
                                                    Q(rut__icontains=keyword) |
                                                    Q(id_perfil__in=filtro_perfil)
                                                )

            return queryset


# Perfiles
class PerfilList(PermissionRequiredMixin, ListView):
    permission_required = ("user.view_perfil")

    model = Perfil    
    paginate_by = 10
    context_object_name = 'perfiles'


class PerfilCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("user.add_perfil")

    model = Perfil
    form_class = PerfilForm

    success_message = "Usuario fue creado con éxito."
    success_url = reverse_lazy('user:perfiles-list')


    def form_valid(self, form):
        super().form_valid(form) 
        perfil = form.save()

        Log.InsertarLog(self.request.user, 'Se creó un nuevo Perfil Id ' + str(self.object.pk) + " - " + perfil.nombre_perfil, 0)       
        return HttpResponseRedirect(reverse_lazy('user:perfiles-list'))



class PerfilUpdate(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("user.change_perfil")

    model = Perfil
    form_class = PerfilForm
    
    success_message = "Usuario fue actualizado con éxito."
    success_url = reverse_lazy('user:perfiles-list')


    def form_valid(self, form):
        super().form_valid(form) 
        perfil = form.save()

        

        Log.InsertarLog(self.request.user, 'Se actualizó el Perfil Id ' + str(perfil.id) + " a " + perfil.nombre_perfil, 0)
        return HttpResponseRedirect(reverse_lazy('user:perfiles-list'))


class PerfilDelete(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    permission_required = ("user.delete_perfil")

    model = Perfil
    context_object_name = 'perfil'


    def form_valid(self, form):
        id_perfil =  self.object.id
        nombre_perfil = self.object.nombre_perfil

        self.object.delete()

        Log.InsertarLog(self.request.user, 'Se eliminó el Perfil Id ' + str(id_perfil) + " - " + nombre_perfil, 0) 
        messages.success(self.request, "Perfil fue eliminado con éxito.")

        return HttpResponseRedirect(reverse_lazy('user:perfiles-list'))



class UsuarioView(PermissionRequiredMixin, UpdateView):
    permission_required = ("user.change_user")

    model = User
    form_class = UsuarioForm 
    template_name = 'user/perfil_gestion.html'



class PerfilUsuarioInline(InlineFormSetFactory):
    model = UserProfile
    form_class = UserProfileForm
    factory_kwargs = {'extra': 0, 'max_num': None, 'can_order': False, 'can_delete': False}



class PerfilDepartamentoInline(InlineFormSetFactory):
    model = UserDepartamento
    form_class = UserDepartamentoForm
    factory_kwargs = {'extra': 0, 'max_num': None, 'can_order': False, 'can_delete': False}



class PerfilCargoInline(InlineFormSetFactory):
    model = UserCargo
    form_class = UserCargoForm
    factory_kwargs = {'extra': 0, 'max_num': None, 'can_order': False, 'can_delete': False}



class GestionPerfilUpdate(PermissionRequiredMixin, SuccessMessageMixin, UpdateWithInlinesView):
    permission_required = ("user.view_user", "user.change_user", "user.view_userdepartamento", "user.change_userdepartamento","user.view_usercargo", "user.change_usercargo")

    model = User
    form_class = UsuarioForm 
    inlines = [PerfilUsuarioInline, PerfilDepartamentoInline, PerfilCargoInline]
    template_name = 'user/perfil_gestion.html'
    success_message = "Perfil actualizado con éxito."

    def form_valid(self, form):
        if form.is_valid():
            usuario = form.save()
            print(usuario.userprofile.id_perfil)
            group = Group.objects.get(id=usuario.userprofile.id_perfil.id)
            usuario.groups.clear()
            usuario.groups.add(group)
            
            Log.InsertarLog(self.request.user, 'Se actualizó el Usuario Id ' + str(usuario.id), 0)            
            return redirect (to='user:usuarios-list')



def loadSubDepartamentos(request):
    id_dpto = request.GET.get('dpto')
    subdepartamentos = Subdepartamento.objects.filter(departamento=id_dpto).order_by('departamento')
    return render(request, 'user/subdepartamentos_list_options.html', {'subdepartamentos': subdepartamentos})



def loadUnidades(request):
    id_subdpto = request.GET.get('subdpto')
    unidades = Unidad.objects.filter(subdepartamento_id=id_subdpto).order_by('subdepartamento')
    return render(request, 'user/unidades_list_options.html', {'unidades': unidades})


@permission_required("user.view_user")
def ExportarExcelFuncionarios(request):    

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Funcionarios"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Funcionarios')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Rut', 'Nombre', 'Apellido', 'Usuario', 'Email', 'Perfil', 'Anexo', 'Cargo', 'Estado']

    ws.col(0).width = int(20 * 260) 
    ws.col(1).width = int(60 * 260)
    ws.col(2).width = int(60 * 260)
    ws.col(3).width = int(30 * 260)
    ws.col(4).width = int(40 * 260)
    ws.col(5).width = int(30 * 260)
    ws.col(6).width = int(20 * 260)
    ws.col(7).width = int(40 * 260)
    ws.col(8).width = int(20 * 260)

    ws.write_merge(0, 0, 0, 8, 'LISTADO FUNCIONARIOS', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    rows = UserProfile.objects.all().values_list('rut', 'user__first_name', 'user__last_name', 'user__username', 'user__email', 'id_perfil__nombre_perfil', 'anexo', 'user__usuario_cargo__id_cargo', 'estado')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):           
            if col_num == 7:
                cargo = UserCargo.objects.filter(id_cargo = row[col_num]).values_list('id_cargo__nombre_cargo')
                ws.write(row_num, col_num, cargo[0][0] if cargo else '', style)
            elif col_num == 8:
                estado = int(row[col_num])
                ws.write(row_num, col_num, settings.ESTADO[0][estado], style)
            else:
                ws.write(row_num, col_num, row[col_num], style)


    wb.save(response)
    return response



def error_404(request, exception):
        data = {}
        return render(request,'user/404.html', data)


def error_403(request, exception):
        data = {}
        return render(request,'user/403.html', data)
