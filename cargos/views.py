import datetime
import xlwt

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from cargos.forms import CargoForm
from .models import Cargo
from logs.models import Log
from django.db.models import Q




class CargoList(PermissionRequiredMixin, ListView):
    permission_required = ("cargos.view_cargo")

    model = Cargo
    context_object_name = 'cargos'
    
    def get_queryset(self):
        # QuerySet por defecto
        queryset = Cargo.objects.all()
        # Check the form value is submitted or not
        if self.request.GET.keys():
            # Verifica campo de búsqueda
            if self.request.GET.get('buscar') != '':
                keyword = self.request.GET.get('buscar')
                # Query filtrado por término de búsqueda (nombre_cargo)
                queryset = Cargo.objects.filter( Q(nombre_cargo__icontains=keyword) )
        return queryset



class CargoDetail(PermissionRequiredMixin, DetailView):
    permission_required = ("cargos.view_cargo")

    model = Cargo
    context_object_name = 'cargo'



class CargoCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("cargos.add_cargo")

    model = Cargo
    form_class = CargoForm

    success_message = "Cargo fue creado con éxito."
    success_url = reverse_lazy('cargos:cargos-list')

    def form_valid(self, form):
        super().form_valid(form) 
        cargo = form.save(commit=False)         
        cargo.nombre_cargo = self.request.POST.get('nombre_cargo').upper()            
        cargo.save()

        Log.InsertarLog(self.request.user, 'Se creó un nuevo Cargo Id ' + str(self.object.pk) + " - " + cargo.nombre_cargo, 0)        
        return HttpResponseRedirect(reverse_lazy('cargos:cargos-list'))



class CargoUpdate(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("cargos.change_cargo")

    model = Cargo
    form_class = CargoForm

    success_message = "Cargo fue actualizado con éxito."
    success_url = reverse_lazy('cargos:cargos-list')


    def form_valid(self, form):
        super().form_valid(form) 
        cargo = form.save(commit=False)         
        cargo.nombre_cargo = self.request.POST.get('nombre_cargo').upper()            
        cargo.save()

        Log.InsertarLog(self.request.user, 'Se actualizó el Cargo Id ' + str(cargo.id) + " a " + cargo.nombre_cargo, 0)        
        return HttpResponseRedirect(reverse_lazy('cargos:cargos-list'))



class CargoDelete(SuccessMessageMixin, DeleteView):
    model = Cargo
    context_object_name = 'cargo'


    def form_valid(self, form):
        id_cargo =  self.object.id
        nombre_cargo = self.object.nombre_cargo

        self.object.delete()

        Log.InsertarLog(self.request.user, 'Se eliminó el Cargo Id ' + str(id_cargo) + " - " + nombre_cargo, 0)             
        messages.success(self.request, "Cargo fue eliminado con éxito.")
        
        return HttpResponseRedirect(reverse_lazy('cargos:cargos-list'))



# Exportar Excel
def ExportarExcel(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Cargos"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Cargos')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Cargo', 'Estado']

    ws.col(0).width = int(100 * 260) 
    ws.col(1).width = int(15 * 260)

    ws.write_merge(0, 0, 0, 4, 'LISTADO DE CARGOS', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    rows = Cargo.objects.all().values_list('nombre_cargo', 'estado')
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