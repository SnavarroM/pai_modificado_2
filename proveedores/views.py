import datetime
import xlwt

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.conf import settings

from .models import Proveedor
from .forms import ProveedorForm
from logs.models import Log
from django.db.models import Q




class ProveedorList(PermissionRequiredMixin, ListView):
    permission_required = ("proveedores.view_proveedor")

    model = Proveedor
    context_object_name = 'proveedores'


    def get_queryset(self):
        # QuerySet por defecto
        queryset = Proveedor.objects.all()
        # Check the form value is submitted or not
        if self.request.GET.keys():
            # Verifica campo de búsqueda
            if self.request.GET.get('buscar') != '':
                keyword = self.request.GET.get('buscar')
                # Query filtrado por término de búsqueda (nombre_cargo)
                queryset = Proveedor.objects.filter( 
                                                    Q(nombre_proveedor__icontains=keyword) | 
                                                    Q(rut_proveedor__icontains=keyword)
                                            )
        return queryset




class ProveedorCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("proveedores.add_proveedor")

    model = Proveedor
    form_class = ProveedorForm

    success_message = "Proveedor fue creado con éxito."
    success_url = reverse_lazy('proveedores:proveedores-list')


    def form_valid(self, form):
        super().form_valid(form) 
        proveedor = form.save(commit=False)         
        proveedor.nombre_proveedor = self.request.POST.get('nombre_proveedor').upper()            
        proveedor.save()

        Log.InsertarLog(self.request.user, 'Se creó un nuevo Proveedor Id ' + str(self.object.pk) + " - " + proveedor.nombre_proveedor, 0)        
        return HttpResponseRedirect(reverse_lazy('proveedores:proveedores-list'))



class ProveedorUpdate(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("proveedores.change_proveedor")

    model = Proveedor
    form_class = ProveedorForm

    success_message = "Proveedor fue actualizado con éxito."
    success_url = reverse_lazy('proveedores:proveedores-list')


    def form_valid(self, form):
        super().form_valid(form) 
        proveedor = form.save(commit=False)         
        proveedor.nombre_proveedor = self.request.POST.get('nombre_proveedor').upper()            
        proveedor.save()

        Log.InsertarLog(self.request.user, 'Se actualizó el Proveedor Id ' + str(proveedor.id) + " a " + proveedor.nombre_proveedor, 0)        
        return HttpResponseRedirect(reverse_lazy('proveedores:proveedores-list'))



class ProveedorDelete(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    permission_required = ("proveedores.delete_proveedor")

    model = Proveedor
    context_object_name = 'proveedor'


    def form_valid(self, form):
        id_proveedor =  self.object.id
        nombre_proveedor = self.object.nombre_proveedor

        self.object.delete()

        Log.InsertarLog(self.request.user, 'Se eliminó el Proveedor Id ' + str(id_proveedor) + " - " + nombre_proveedor, 0) 
        messages.success(self.request, "Proveedor fue eliminado con éxito.")

        return HttpResponseRedirect(reverse_lazy('proveedores:proveedores-list'))






# Exportar a Excel
@permission_required("proveedores.view_proveedor")
def ExportarExcel(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Proveedores"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Proveedores')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['RUT', 'Proveedor', 'Estado']

    ws.col(0).width = int(20 * 260) 
    ws.col(1).width = int(100 * 260)
    ws.col(2).width = int(30 * 260)

    ws.write_merge(0, 0, 0, 4, 'LISTADO DE PROVEEDORES', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    #style.borders = borders

    rows = Proveedor.objects.all().values_list('rut_proveedor', 'nombre_proveedor', 'estado')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num < 2:
                ws.write(row_num, col_num, row[col_num], style)
            else:
                estado = int(row[col_num])
                ws.write(row_num, col_num, settings.ESTADO[0][estado], style)

    wb.save(response)
    return response