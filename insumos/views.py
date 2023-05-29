import datetime
import xlwt

from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.db.models import Q

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Categoria, Insumo, UnidadMedida
from .forms import InsumoForm, CategoriaForm, UnidadMedidaForm, InsumoFormUpdate
from logs.models import Log




# Insumos           
class InsumoList(PermissionRequiredMixin, ListView):   
    permission_required = ("insumos.view_insumo")

    model = Insumo    
    context_object_name = 'insumos'
    paginate_by = 10

    def get_queryset(self):
        # QuerySet por defecto
        queryset = Insumo.objects.all()
        # Check the form value is submitted or not
        if self.request.GET.keys():
            # Verifica campo de búsqueda
            if self.request.GET.get('buscar') != None:
                keyword = self.request.GET.get('buscar')
                # Query filtrado por término de búsqueda (codigo_insumo, denominación, nombre unidad de medida, nombre categoría)
                    
                filtro_unidad = UnidadMedida.objects.filter(nombre_unidad_medida__icontains=keyword)
                filtro_categoria = Categoria.objects.filter(nombre_categoria__icontains=keyword)
                
                queryset = Insumo.objects.filter(
                                                Q(codigo_insumo__icontains=keyword) | 
                                                Q(denominacion__icontains=keyword) |
                                                Q(unidad_medida__in=filtro_unidad) |
                                                Q(categoria__in=filtro_categoria) 
                                            )
                            
        return queryset



class InsumoDetail(PermissionRequiredMixin, DetailView):
    permission_required = ("insumos.view_insumo")

    model = Insumo
    context_object_name = 'insumo'


class InsumoCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("insumos.add_insumo")

    model = Insumo
    form_class = InsumoForm

    def form_valid(self, form):
        super().form_valid(form) 
        insumo = form.save()

        Log.InsertarLog(self.request.user, 'Se creó un nuevo Insumo Id ' + str(self.object.pk) + " - " + insumo.denominacion, 0)

        messages.success(self.request, ("Insumo fue creado con éxito."))
        return HttpResponseRedirect(reverse_lazy('insumos:insumos-list'))



class InsumoUpdate(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("insumos.change_insumo")
    
    model = Insumo
    form_class = InsumoFormUpdate

    success_message = "Insumo fue actualizado con éxito."
    success_url = reverse_lazy('insumos:insumos-list')

    def form_valid(self, form):
        super().form_valid(form) 
        insumo = form.save() 

        Log.InsertarLog(self.request.user, 'Se actualizó el Insumo Id ' + str(insumo.id) + " a " + insumo.denominacion, 0)

        messages.success(self.request, ("Insumo fue actualizado con éxito."))
        return HttpResponseRedirect(reverse_lazy('insumos:insumos-list'))



class InsumoDelete(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    permission_required = ("insumos.delete_insumo")

    model = Insumo
    context_object_name = 'insumo'
    
    success_message = "Insumo fue eliminado con éxito."
    success_url = reverse_lazy('insumos:insumos-list')
# Fin Insumos


# Categorías
class CategoriaList(PermissionRequiredMixin, ListView):
    permission_required = ("insumos.view_categoria")

    model = Categoria
    context_object_name = 'categorias'
    
    def get_queryset(self):
        # QuerySet por defecto
        queryset = Categoria.objects.all()
        # Check the form value is submitted or not
        if self.request.GET.keys():
            # Verifica campo de búsqueda
            if self.request.GET.get('buscar') != '':
                keyword = self.request.GET.get('buscar')
                # Query filtrado por término de búsqueda (nombre_categoria)
                queryset = Categoria.objects.filter( Q(nombre_categoria__icontains=keyword) )
        return queryset



class CategoriaDetail(PermissionRequiredMixin, DetailView):
    permission_required = ("insumos.view_categoria")

    model = Categoria
    context_object_name = 'categoria'



class CategoriaCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("insumos.add_categoria")

    model = Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy('insumos:categorias-list')


    def form_valid(self, form):
        super().form_valid(form) 
        categoria = form.save(commit=False)         
        categoria.nombre_categoria = self.request.POST.get('nombre_categoria').upper()            
        categoria.save()

        Log.InsertarLog(self.request.user, 'Se creó una nueva Categoría Id ' + str(self.object.pk) + " - " + categoria.nombre_categoria, 0)

        messages.success(self.request, ("Categoría fue creada con éxito."))
        return HttpResponseRedirect(reverse_lazy('insumos:categorias-list'))



class CategoriaUpdate(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("insumos.change_categoria")

    model = Categoria
    form_class = CategoriaForm

    success_url = reverse_lazy('insumos:categorias-list')


    def form_valid(self, form):
        super().form_valid(form) 
        categoria = form.save(commit=False)         
        categoria.nombre_categoria = self.request.POST.get('nombre_categoria').upper()            
        categoria.save()

        Log.InsertarLog(self.request.user, 'Se actualizó la categoría Id ' + str(categoria.id) + " a " + categoria.nombre_categoria, 0)

        messages.success(self.request, ("Categoría fue actualizada con éxito."))
        return HttpResponseRedirect(reverse_lazy('insumos:categorias-list'))



class CategoriaDelete(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    permission_required = ("insumos.delete_categoria")

    model = Categoria
    context_object_name = 'categoria'

    success_message = "Categoría fue eliminada con éxito."
    success_url = reverse_lazy('insumos:categorias-list')
# Fin Categorías



# Unidad de Medidas
class UnidadMedidaList(PermissionRequiredMixin, ListView):
    permission_required = ("insumos.view_unidadmedida")

    model = UnidadMedida
    context_object_name = 'unidadmedidas'

    def get_queryset(self):
        # QuerySet por defecto
        queryset = UnidadMedida.objects.all()
        # Check the form value is submitted or not
        if self.request.GET.keys():
            # Verifica campo de búsqueda
            if self.request.GET.get('buscar') != '':
                keyword = self.request.GET.get('buscar')
                # Query filtrado por término de búsqueda (nombre_unidad_medida)
                queryset = UnidadMedida.objects.filter( Q(nombre_unidad_medida__icontains=keyword) )
        return queryset



class UnidadMedidaDetail(PermissionRequiredMixin, DetailView):
    permission_required = ("insumos.view_unidadmedida")

    model = UnidadMedida
    context_object_name = 'unidadmedida'



class UnidadMedidaCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("insumos.add_unidadmedida")

    model = UnidadMedida
    form_class = UnidadMedidaForm

    success_url = reverse_lazy('insumos:unidadmedidas-list')

    def form_valid(self, form):
        super().form_valid(form) 
        unimedida = form.save(commit=False)         
        unimedida.nombre_unidad_medida = self.request.POST.get('nombre_unidad_medida').upper()            
        unimedida.save()

        Log.InsertarLog(self.request.user, 'Se creó una nueva Unidad de Medida Id ' + str(self.object.pk) + " - " + unimedida.nombre_unidad_medida, 0)

        messages.success(self.request, ("Unidad de Medida fue creada con éxito."))
        return HttpResponseRedirect(reverse_lazy('insumos:unidadmedidas-list'))



class UnidadMedidaUpdate(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("insumos.change_unidadmedida")

    model = UnidadMedida
    form_class = UnidadMedidaForm

    success_url = reverse_lazy('insumos:unidadmedidas-list')

    def form_valid(self, form):
        super().form_valid(form) 
        unimedida = form.save(commit=False)         
        unimedida.nombre_unidad_medida = self.request.POST.get('nombre_unidad_medida').upper()            
        unimedida.save()

        Log.InsertarLog(self.request.user, 'Se actualizó la Unidad de Medida Id ' + str(unimedida.id) + " a " + unimedida.nombre_unidad_medida, 0)

        messages.success(self.request, ("Unidad de Medida fue actualizada con éxito."))
        return HttpResponseRedirect(reverse_lazy('insumos:unidadmedidas-list'))



class UnidadMedidaDelete(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    permission_required = ("insumos.delete_unidadmedida")

    model = UnidadMedida
    context_object_name = 'unidadmedida'

    success_message = "Unidad de Medida fue eliminada con éxito."
    success_url = reverse_lazy('insumos:unidadmedidas-list')
# Fin Unidad de Medidas



# Exportar a Excel
@permission_required("insumos.view_insumo")
def ExportarExcel(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Insumos"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Insumos')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Código', 'Denominación', 'Unidad Medida', 'Saldo', 'Precio']

    ws.col(0).width = int(20 * 260) 
    ws.col(1).width = int(100 * 260)
    ws.col(2).width = int(30 * 260)
    ws.col(3).width = int(15 * 260)
    ws.col(4).width = int(15 * 260)

    ws.write_merge(0, 0, 0, 4, 'LISTADO DE INSUMOS', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    #style.borders = borders

    rows = Insumo.objects.all().values_list('codigo_insumo', 'denominacion', 'unidad_medida__nombre_unidad_medida', 'saldo', 'precio')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], style)

    wb.save(response)
    return response



@permission_required("insumos.view_unidadmedida")
def ExportarExcelUnidadMedida(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Unidades Medidas"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Unidades Medida')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Unidad Medida', 'Estado']

    ws.col(0).width = int(100 * 260) 
    ws.col(1).width = int(15 * 260)

    ws.write_merge(0, 0, 0, 4, 'LISTADO DE UNIDADES DE MEDIDAS', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    #style.borders = borders

    rows = UnidadMedida.objects.all().values_list('nombre_unidad_medida', 'estado')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num < 1:
                ws.write(row_num, col_num, row[col_num], style)
            else:
                estado = int(row[col_num])
                ws.write(row_num, col_num, settings.ESTADO[0][estado], style)

    wb.save(response)
    return response


@permission_required("insumos.view_categoria")
def ExportarExcelCategorias(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Categorías"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Categorías')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Unidad Medida', 'Estado']

    ws.col(0).width = int(100 * 260) 
    ws.col(1).width = int(15 * 260)

    ws.write_merge(0, 0, 0, 4, 'LISTADO DE CATEGORÍAS', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    #style.borders = borders

    rows = Categoria.objects.all().values_list('nombre_categoria', 'estado')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num < 1:
                ws.write(row_num, col_num, row[col_num], style)
            else:
                estado = int(row[col_num])
                ws.write(row_num, col_num, settings.ESTADO[0][estado], style)

    wb.save(response)
    return response