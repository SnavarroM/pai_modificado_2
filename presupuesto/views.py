import xlwt
import datetime

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.db.models import Q

from .models import PresupuestoCategoria, PresupuestoDepartamento, PresupuestoSubDepartamento
from logs.models import Log
from .forms import  PresupuestoCategoriaForm, AsignacionPresupuestoForm, \
                    PresupuestoDepartamentoFormSet, PresupuestoSubDepartamentoFormSet



# Cuenta Presupuestaria
class PresupuestoCategoriaList(PermissionRequiredMixin, ListView):
    permission_required = ("presupuesto.view_presupuestocategoria")    

    model = PresupuestoCategoria
    context_object_name = 'prescategorias'

    paginate_by = 10


    def get_queryset(self):
        # QuerySet por defecto
        queryset = PresupuestoCategoria.objects.all()
        # Check the form value is submitted or not
        if self.request.GET.keys():
            # Verifica campo de búsqueda
            if self.request.GET.get('buscar') != '':
                keyword = self.request.GET.get('buscar')
                # Query filtrado por término de búsqueda (nombre_categoria)
                queryset = PresupuestoCategoria.objects.filter( Q(id_categoria__nombre_categoria__icontains=keyword) )
        return queryset




class PresupuestoCategoriaCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("presupuesto.add_presupuestocategoria")

    model = PresupuestoCategoria
    form_class = PresupuestoCategoriaForm
    success_url = reverse_lazy('presupuesto:cuentas-list')

    def form_valid(self, form):
        super().form_valid(form) 
        ppto = form.save()

        Log.InsertarLog(self.request.user, 'Se creó una nueva Unidad de Medida Id ' + str(self.object.pk) + " - " + str(ppto.id_categoria) + " - " + str(ppto.marco_presupuestario), 0)

        messages.success(self.request, ("Cuenta Presupuestaria fue creada con éxito."))
        return HttpResponseRedirect(reverse_lazy('presupuesto:cuentas-list'))




class PresupuestoCategoriaUpdate(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("presupuesto.change_presupuestocategoria")

    model = PresupuestoCategoria
    form_class = PresupuestoCategoriaForm
    success_url = reverse_lazy('presupuesto:cuentas-list')

    def form_valid(self, form):
        super().form_valid(form) 
        ppto = form.save() 

        Log.InsertarLog(self.request.user, 'Se actualizó el Insumo Id ' + str(ppto.id) + " - " + ppto.id_categoria + " - " + ppto.marco_presupuestario, 0)

        messages.success(self.request, ("Cuenta Presupuestaria fue actualizada con éxito."))
        return HttpResponseRedirect(reverse_lazy('presupuesto:cuentas-list'))



# Asignación de Presupuesto

class AsignacionPresupuestoDptoInline():
    model = PresupuestoCategoria
    form_class = AsignacionPresupuestoForm
    template_name = "presupuesto/asignacionpresupuesto_form.html"


    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            
            if formset_save_func is not None:            
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('presupuesto:cuentas-list')


    def formset_presupuestodpto_valid(self, formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        presupuestodpto = formset.save(commit=False)  # self.save_formset(formset, contact)
        for pptodpto in presupuestodpto:
            pptodpto.id_presupuesto_categoria = self.object
            pptodpto.save()


    def formset_presupuestosubdpto_valid(self, formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        presupuestosubdpto = formset.save(commit=False)  # self.save_formset(formset, contact)
        for pptosubdpto in presupuestosubdpto:
            pptosubdpto.id_presupuesto_categoria = self.object
            pptosubdpto.save()



class AsignacionPresupuesto(SuccessMessageMixin, AsignacionPresupuestoDptoInline, CreateView):

    success_message = "Asignación de Presupuesto fue creada con éxito."
    success_url = reverse_lazy('presupuesto:cuentas-list')


    def get_context_data(self, **kwargs):
        ctx = super(AsignacionPresupuesto, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx


    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'presupuestodpto': PresupuestoDepartamentoFormSet(prefix='presupuestodpto'),
                'presupuestosubdpto': PresupuestoSubDepartamentoFormSet(prefix='presupuestosubdpto')
            }
        else:
            return {
                'presupuestodpto': PresupuestoDepartamentoFormSet(self.request.POST or None, self.request.FILES or None, prefix='presupuestodpto'),
                'presupuestosubdpto': PresupuestoSubDepartamentoFormSet(self.request.POST or None, self.request.FILES or None, prefix='presupuestosubdpto'),
            }



class AsignacionPresupuestoUpdate(SuccessMessageMixin, AsignacionPresupuestoDptoInline, UpdateView):

    success_message = "Asignación de Presupuesto se actualizó con éxito."
    success_url = reverse_lazy('presupuesto:cuentas-list')

    def get_initial(self, **kwargs):
        initial = super(AsignacionPresupuestoUpdate, self).get_initial()
        initial['id_presupuesto_categoria'] = self.kwargs.get('pk')
        return initial


    def get_context_data(self, **kwargs):
        ctx = super(AsignacionPresupuestoUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx


    def get_named_formsets(self):
        return {
                'presupuestodpto': PresupuestoDepartamentoFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='presupuestodpto'),
                'presupuestosubdpto': PresupuestoSubDepartamentoFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='presupuestosubdpto'),
            }



def loadMontoPresupuestario(request):
    id_cta = request.GET.get('cuenta')
    presupuesto = PresupuestoCategoria.objects.filter(id=id_cta).values('id_categoria', 'marco_presupuestario')
    return JsonResponse({'data' : presupuesto[0] if presupuesto else None}, safe=False)



# Excel
@permission_required("presupuesto.view_presupuestocategoria")
def ExportarExcelCtasPresupuestarias(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Cuentas Presupuestarias"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Cuentas Presupuestarias')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Categoría', 'Marco Presupuestario']

    ws.col(0).width = int(100 * 260) 
    ws.col(1).width = int(50 * 260)

    ws.write_merge(0, 0, 0, 1, 'LISTADO CUENTAS PRESUPUESTARIAS', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    style_cantidades = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;', "$ 0,#")

    rows = PresupuestoCategoria.objects.all().values_list('id_categoria__nombre_categoria', 'marco_presupuestario')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):                       
            if col_num == 1:
                ws.write(row_num, col_num, row[col_num], style_cantidades)
            else:
                ws.write(row_num, col_num, row[col_num], style)

    wb.save(response)
    return response



@permission_required("presupuesto.view_presupuestocategoria", "presupuesto.view_presupuestodepartamento", "presupuesto.view_presupuestosubdepartamento")
def ExportarExcelAsignacionPresupuesto(request, pk):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Asignación Presupuestaria"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'

# Hoja Centro de Responsabilidad

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Centro Responsabilidad')

    #Cabecera hoja, primera fila
    row_num = 3

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Categoría', 'Marco Presupuestario']

    ws.col(0).width = int(150 * 260) 
    ws.col(1).width = int(50 * 260)

    ws.write_merge(0, 0, 0, 1, 'ASIGNACIÓN DE PRESUPUESTO', header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    style_cantidades = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;', "$ 0,#")
    footer_cantidades = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;', "$ 0,#")

    ws.write_merge(7, 7, 0, 1, 'CENTRO DE RESPONSABILIDAD', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)


    rows = PresupuestoCategoria.objects.filter(id = pk).values_list('id_categoria__nombre_categoria', 'marco_presupuestario')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):                       
            if col_num == 1:
                ws.write(row_num, col_num, row[col_num], style_cantidades)
            else:
                ws.write(row_num, col_num, row[col_num], style)


    row_num = 8
    columns = ['Departamento', 'Monto']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    rows = PresupuestoDepartamento.objects.filter(id_presupuesto_categoria = pk).distinct().values_list('id_departamento__nombre_dpto', 'presupuesto')

    total = 0
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):                       
            if col_num == 1:
                total += row[col_num]
                ws.write(row_num, col_num, row[col_num], style_cantidades)
            else:
                ws.write(row_num, col_num, row[col_num], style)


    ws.write(row_num + 1, 0, "TOTAL", header_style)
    ws.write(row_num + 1, 1, total, footer_cantidades)

# Hoja Centro de Costo

    ws = wb.add_sheet('Centro de Costo')

    #Cabecera hoja, primera fila
    row_num = 3

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Categoría', 'Marco Presupuestario']

    ws.col(0).width = int(150 * 260) 
    ws.col(1).width = int(50 * 260)

    ws.write_merge(0, 0, 0, 2, 'ASIGNACIÓN DE PRESUPUESTO', header_style)
    ws.write_merge(7, 7, 0, 2, 'CENTRO DE COSTO', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    rows = PresupuestoCategoria.objects.filter(id = pk).values_list('id_categoria__nombre_categoria', 'marco_presupuestario')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):                       
            if col_num == 1:
                ws.write(row_num, col_num, row[col_num], style_cantidades)
            else:
                ws.write(row_num, col_num, row[col_num], style)


    row_num = 8
    columns = ['Departamento', 'Sub Departamento', 'Monto']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    rows = PresupuestoSubDepartamento.objects.filter(id_presupuesto_categoria = pk).values_list('id_departamento__nombre_dpto', 'id_subdepartamento__nombre_sub_dpto', 'presupuesto')

    total = 0
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):                       
            if col_num == 2:
                total += row[col_num]
                ws.write(row_num, col_num, float(row[col_num]), style_cantidades)
            else:
                ws.write(row_num, col_num, row[col_num], style)

    ws.write(row_num + 1, 0, "TOTAL", header_style)
    ws.write(row_num + 1, 1, "", header_style)
    ws.write(row_num + 1, 2, total, footer_cantidades)

    wb.save(response)
    return response