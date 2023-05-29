import xlwt
import datetime

from msilib.schema import ListView
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.conf import settings

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

from departamentos.templatetags import departamentos_filters
from .forms import DepartamentoForm, SubDepartamentoForm, UnidadForm
from .models import Departamento, Subdepartamento, Unidad
from user.models import UserProfile, User
from logs.models import Log


#   Departamento 
class DptoListView(PermissionRequiredMixin, ListView):
    permission_required = ("departamentos.view_departamento")

    model = Departamento  
    context_object_name = 'departamentos'
    
    paginate_by = 10


    def get_queryset(self):
        # QuerySet por defecto
        queryset = Departamento.objects.all()
        # Verifica si el formulario fue enviado o no 
        if self.request.GET.keys():
            # Verifica campo de búsqueda
            if self.request.GET.get('buscar') != '':
                keyword = self.request.GET.get('buscar')

                # Query filtrado por término de búsqueda 
                filtro_user = User.objects.filter(first_name__icontains=keyword)
                filtro_funcionario = UserProfile.objects.filter(user__in=filtro_user).values_list('rut')
                
                queryset = Departamento.objects.filter( 
                                Q(id_dpto__icontains=keyword) |                                                     # Código Departamento
                                Q(nombre_dpto__icontains=keyword) |                                                 # Nombre Departamento
                                Q(rut_jefe__icontains=keyword) |                                                    # Rut Jefe
                                Q(rut_jefe_subrogante__icontains=keyword) |                                         # Rut Jefe Subrogante
                                Q(rut_jefe__in = filtro_funcionario) |                                              # Nombre Jefe
                                Q(rut_jefe_subrogante__in = filtro_funcionario)                                     # Nombre Jefe Subrogante
                        )
        return queryset



class DptoCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("departamentos.add_departamento")

    model = Departamento
    form_class = DepartamentoForm


    def post(self, request):
        if request.method == 'POST':
            form = DepartamentoForm(request.POST)
            if form.is_valid():
                
                dpto = form.save(commit=False)
                dpto.nombre_dpto = request.POST.get('nombre_dpto').upper()
                dpto.rut_jefe = request.POST.get('rut_jefe')
                dpto.rut_jefe_subrogante = request.POST.get('rut_jefe_subrogante')
                dpto.save()

                Log.InsertarLog(self.request.user, 'Se creó un nuevo Departamento Id ' + str(self.object.pk) + " - " + dpto.nombre_dpto, 0)        

                messages.success(request, ("Departamento fue creado con éxito."))
                return HttpResponseRedirect(reverse_lazy('departamentos:dptos-list'))



class DptoUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("departamentos.change_departamento")

    model = Departamento
    form_class = DepartamentoForm


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()


        if form.is_valid():
            dpto = form.save(commit=False)
            dpto.nombre_dpto = self.request.POST.get('nombre_dpto').upper()
            dpto.rut_jefe = self.request.POST.get('rut_jefe')
            dpto.rut_jefe_subrogante = self.request.POST.get('rut_jefe_subrogante')        
            dpto.save()

            Log.InsertarLog(self.request.user, 'Se actualizó el Departamento Id ' + str(dpto.id_dpto) + " a " + dpto.nombre_dpto, 0)

            messages.success(request, ("Departamento fue actualizado con éxito."))
            return HttpResponseRedirect(reverse_lazy('departamentos:dptos-list'))
        else:
            return self.form_invalid(form)



#   Sub Departamento 
class SubDptoListView(PermissionRequiredMixin, ListView):
    permission_required = ("departamentos.view_subdepartamento")

    model = Subdepartamento    
    context_object_name = 'subdepartamentos'
    
    paginate_by = 10
    ordering = ['id_sub_dpto']


    def get_queryset(self):
        # QuerySet por defecto
        queryset = Subdepartamento.objects.all()
        # Check the form value is submitted or not
        if self.request.GET.keys():
            # Verifica campo de búsqueda
            if self.request.GET.get('buscar') != '':
                keyword = self.request.GET.get('buscar')
                
                # Query filtrado por término de búsqueda 

                filtro_user = User.objects.filter(first_name__icontains=keyword)
                filtro_funcionario = UserProfile.objects.filter(user__in=filtro_user).values_list('rut')
                
                queryset = Subdepartamento.objects.filter( 
                                Q(id_sub_dpto__icontains=keyword) |
                                Q(nombre_sub_dpto__icontains=keyword) |
                                Q(departamento__nombre_dpto__icontains=keyword) |
                                Q(rut_jefe__icontains=keyword) |
                                Q(rut_jefe_subrogante__icontains=keyword) | 
                                Q(rut_jefe__in=filtro_funcionario) |
                                Q(rut_jefe_subrogante__in=filtro_funcionario)
                        )
        return queryset



class SubDptoCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("departamentos.add_subdepartamento")

    model = Subdepartamento
    form_class = SubDepartamentoForm


    def post(self, request):
        if request.method == 'POST':
            form = SubDepartamentoForm(request.POST)

            if form.is_valid():                
                subdpto = form.save(commit=False)
                subdpto.nombre_sub_dpto = self.request.POST.get('nombre_sub_dpto').upper()
                subdpto.rut_jefe = request.POST.get('rut_jefe')
                subdpto.rut_jefe_subrogante = request.POST.get('rut_jefe_subrogante')
                subdpto.save()

                Log.InsertarLog(self.request.user, 'Se creó un nuevo Subdepartamento Id ' + str(self.object.pk) + " a " + subdpto.nombre_sub_dpto, 0)

                messages.success(request, ("Subdepartamento fue creado con éxito."))
                return HttpResponseRedirect(reverse_lazy('departamentos:subdptos-list'))



class SubDptoUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("departamentos.change_subdepartamento")

    model = Subdepartamento
    form_class = SubDepartamentoForm


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            subdpto = form.save(commit=False)
            subdpto.nombre_sub_dpto = self.request.POST.get('nombre_sub_dpto').upper()
            subdpto.rut_jefe = self.request.POST.get('rut_jefe')
            subdpto.rut_jefe_subrogante = self.request.POST.get('rut_jefe_subrogante')      
            subdpto.save()

            Log.InsertarLog(self.request.user, 'Se actualizó el Subdepartamento Id ' + str(subdpto.id_sub_dpto) + " a " + subdpto.nombre_sub_dpto, 0)

            messages.success(request, ("Subdepartamento fue creado con éxito."))
            return HttpResponseRedirect(reverse_lazy('departamentos:subdptos-list'))
        else:
            return self.form_invalid(form)


#   Unidad 
class UnidadListView(PermissionRequiredMixin, ListView):
    permission_required = ("departamentos.view_unidad")

    model = Unidad    
    context_object_name = 'unidades'
    
    paginate_by = 10
    ordering = ['id_unidad']


    def get_queryset(self):
        # QuerySet por defecto
        queryset = Unidad.objects.all()
        # Check the form value is submitted or not
        if self.request.GET.keys():
            # Verifica campo de búsqueda
            if self.request.GET.get('buscar') != '':
                keyword = self.request.GET.get('buscar')
                
                # Query filtrado por término de búsqueda 
                filtro_user = User.objects.filter(first_name__icontains=keyword)
                filtro_funcionario = UserProfile.objects.filter(user__in=filtro_user).values_list('rut')
                
                queryset = Unidad.objects.filter( 
                                Q(id_unidad__icontains=keyword) |
                                Q(nombre_unidad__icontains=keyword) |
                                Q(subdepartamento__nombre_sub_dpto__icontains=keyword) |
                                Q(rut_jefe__icontains=keyword) |
                                Q(rut_jefe_subrogante__icontains=keyword)  | 
                                Q(rut_jefe__in=filtro_funcionario) |
                                Q(rut_jefe_subrogante__in=filtro_funcionario)
                        )
        return queryset



class UnidadCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("departamentos.add_unidad")
    model = Unidad
    form_class = UnidadForm


    def post(self, request):
        if request.method == 'POST':
            form = UnidadForm(request.POST)
            if form.is_valid():

                unidad = form.save(commit=False)
                unidad.nombre_unidad = self.request.POST.get('nombre_unidad').upper()
                unidad.rut_jefe = self.request.POST.get('rut_jefe')
                unidad.rut_jefe_subrogante = self.request.POST.get('rut_jefe_subrogante')
                unidad.save()

                Log.InsertarLog(self.request.user, 'Se creó una nueva Unidad Id ' + str(self.object.pk) + " a " + unidad.nombre_unidad, 0)

                messages.success(request, ("Unidad fue creada con éxito."))
                return HttpResponseRedirect(reverse_lazy('departamentos:unidades-list'))



class UnidadUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("departamentos.change_unidad")

    model = Unidad
    form_class = UnidadForm


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            print("valid")
            unidad = form.save(commit=False)
            unidad.nombre_unidad = self.request.POST.get('nombre_unidad').upper()
            unidad.rut_jefe = self.request.POST.get('rut_jefe')
            unidad.rut_jefe_subrogante = self.request.POST.get('rut_jefe_subrogante')       
            unidad.save()

            Log.InsertarLog(self.request.user, 'Se actualizó el Subdepartamento Id ' + str(unidad.id_unidad) + " a " + unidad.nombre_unidad, 0)

            messages.success(request, ("Unidad fue actualizada con éxito."))
            return HttpResponseRedirect(reverse_lazy('departamentos:unidades-list'))
        else:
            return self.form_invalid(form)




# Exportar a Excel
@permission_required("departamentos.view_departamento")
def ExportarExcelDptos(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Departamentos"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Departamentos-Unidades')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Id', 'Nombre Departamento/Unidad', 'Jefe', 'Jefe Subrogante', 'Estado']

    ws.col(0).width = int(20 * 260) 
    ws.col(1).width = int(100 * 260)
    ws.col(2).width = int(30 * 260)
    ws.col(3).width = int(30 * 260)
    ws.col(4).width = int(15 * 260)

    ws.write_merge(0, 0, 0, 4, 'LISTADO DE DEPARTAMENTOS / UNIDADES', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    #style.borders = borders

    rows = Departamento.objects.all().values_list('id_dpto', 'nombre_dpto', 'rut_jefe', 'rut_jefe_subrogante', 'estado')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num == 2 or col_num == 3:
                jefe = departamentos_filters.get_nombre_jefe(row[col_num])
                ws.write(row_num, col_num, str(jefe), style)
            elif col_num == 4:
                estado = int(row[col_num])
                ws.write(row_num, col_num, settings.ESTADO[0][estado], style)
            else:
                ws.write(row_num, col_num, row[col_num], style)


    wb.save(response)
    return response


@permission_required("departamentos.view_subdepartamento")
def ExportarExcelSubDptos(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Subdepartamentos"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('SubDepartamentos-SubUnidades')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Id. Dpto', 'Departamento / Unidad', 'Id. SubDpto', 'Subdepartamento / SubUnidad', 'Jefe', 'Jefe Subrogante', 'Estado']

    ws.col(0).width = int(20 * 260) 
    ws.col(1).width = int(100 * 260)
    ws.col(2).width = int(20 * 260)
    ws.col(3).width = int(100 * 260)
    ws.col(4).width = int(30 * 260)
    ws.col(5).width = int(30 * 260)
    ws.col(6).width = int(15 * 260)

    ws.write_merge(0, 0, 0, 6 , 'LISTADO DE SUBDEPARTAMENTOS / SUB UNIDADES', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    #style.borders = borders

    rows = Subdepartamento.objects.all().values_list('departamento__id_dpto', 'departamento__nombre_dpto', 'id_sub_dpto', 'nombre_sub_dpto', 'rut_jefe', 'rut_jefe_subrogante', 'estado')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num == 4 or col_num == 5:
                jefe = departamentos_filters.get_nombre_jefe(row[col_num])
                ws.write(row_num, col_num, str(jefe), style)
            elif col_num == 6:
                estado = int(row[col_num])
                ws.write(row_num, col_num, settings.ESTADO[0][estado], style)
            else:
                ws.write(row_num, col_num, row[col_num], style)


    wb.save(response)
    return response



@permission_required("departamentos.view_unidad")
def ExportarExcelUnidades(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Unidades"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Unidades')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Id. Dpto', 'Departamento / Unidad', 'Id. SubDpto', 'Subdepartamento / SubUnidad', 'Id. Unidad / Sección', 'Unidad / Sección', 'Estado']

    ws.col(0).width = int(20 * 260) 
    ws.col(1).width = int(100 * 260)
    ws.col(2).width = int(20 * 260)
    ws.col(3).width = int(100 * 260)
    ws.col(4).width = int(20 * 260)
    ws.col(5).width = int(100 * 260)
    ws.col(6).width = int(15 * 260)

    ws.write_merge(0, 0, 0, 7, 'LISTADO UNIDADES / SECCIONES', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    rows = Unidad.objects.all().values_list('subdepartamento__departamento__id_dpto', 'subdepartamento__departamento__nombre_dpto', 'subdepartamento__id_sub_dpto', 'subdepartamento__nombre_sub_dpto', 'id_unidad', 'nombre_unidad', 'estado')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):           
            if col_num == 6:
                estado = int(row[col_num])
                ws.write(row_num, col_num, settings.ESTADO[0][estado], style)
            else:
                ws.write(row_num, col_num, row[col_num], style)


    wb.save(response)
    return response