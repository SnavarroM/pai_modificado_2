import xlwt
import datetime
from multiprocessing import context
from urllib import request

from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.humanize.templatetags.humanize import intcomma

from insumos.models import Insumo
from proveedores.models import Proveedor
from inventario.models import Inventario
from .models import Compra, CompraInsumo
from .forms import CompraForm, CompraInsumoForm, CompraInsumoFormSet


class CompraList(PermissionRequiredMixin, ListView):
    permission_required = ("compras.view_compra")

    model = Compra
    context_object_name = 'compras'

    paginate_by = 10
    ordering = ['-pk']


    def get_queryset(self):
        # QuerySet por defecto
        queryset = Compra.objects.all()
        # Check the form value is submitted or not
        if self.request.GET.keys():
            # Verifica campo de búsqueda
            if self.request.GET.get('buscar') != None:
                keyword = self.request.GET.get('buscar')
                # Query filtrado por término de búsqueda (fecha factura, guia-factura, rut proveedor, nombre proveedor)
                
                filtro_nombre_proveedor = Proveedor.objects.filter(nombre_proveedor__icontains=keyword)
                filtro_rut_proveedor = Proveedor.objects.filter(rut_proveedor__icontains=keyword)

                try:
                    if keyword.count('-') > 1:                        
                        fecha_compra = str(datetime.strptime(keyword, "%d-%m-%Y").date())
                    else:
                        fecha_compra = None
                except Exception as e:
                    raise e

                
                
                queryset = Compra.objects.filter(
                                                Q(fecha_compra=fecha_compra) | 
                                                Q(guia=keyword) |
                                                Q(orden_de_compra=keyword) |
                                                Q(id_proveedor__in=filtro_nombre_proveedor) |
                                                Q(id_proveedor__in=filtro_rut_proveedor)
                                            )
                            
        return queryset



class CompraDetail(PermissionRequiredMixin, DetailView):
    permission_required = ("compras.view_compra")

    model = Compra
    context_object_name = 'compra'

    def get_context_data(self, **kwargs):
        context = super(CompraDetail, self).get_context_data(**kwargs)
        detallecompra = CompraInsumo.objects.filter(id_compra = self.object.id)      
        context['detallecompra'] = detallecompra        

        return context


class CompraInsumoInline():
    model = Compra
    form_class = CompraForm
    template_name = "compras/compra_form.html"


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
        return redirect('compras:compras-list')


    def formset_detallefactura_valid(self, formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        detallefactura = formset.save(commit=False)
        for detfact in detallefactura:
            detfact.id_compra = self.object
            detfact.save()

            # Actualizar precio y saldo de producto
            Insumo.update_precio_insumo(detfact.id_insumo.codigo_insumo, detfact.precio_promedio, detfact.id_compra.rut_responsable)
            Insumo.aumentar_cantidad_insumo(detfact.id_insumo.codigo_insumo, detfact.cantidad, detfact.id_compra.rut_responsable)

        # Ingresar producto a Inventario  |   'E' - Entrada de Producto
        Inventario.InsertarInventarioCompra(detallefactura, 'E') 




class CompraCreate(PermissionRequiredMixin, SuccessMessageMixin, CompraInsumoInline, CreateView):
    permission_required = ("compras.add_compra")

    success_message = "Factura de Compra fue creada con éxito."
    success_url = reverse_lazy('compras:compras-list')


    def get_initial(self):
        return {
            'rut_responsable': self.request.user.userprofile.rut,
            'descuento': 0
        }


    def get_context_data(self, **kwargs):
        ctx = super(CompraCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        ctx['valor_iva'] = str(float(settings.IVA) /100).replace(',','.')
        return ctx


    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'detallefactura': CompraInsumoFormSet(prefix='detallefactura')
            }
        else:
            return {
                'detallefactura': CompraInsumoFormSet(self.request.POST or None, self.request.FILES or None, prefix='detallefactura'),
            }



class CompraUpdate(PermissionRequiredMixin, SuccessMessageMixin, CompraInsumoInline, UpdateView):
    permission_required = ("compras.change_compra")

    success_message = "Factura de Compra actualizada con éxito."
    success_url = reverse_lazy('compras:compras-list')


    def get_context_data(self, **kwargs):
        ctx = super(CompraUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        ctx['valor_iva'] = str(float(settings.IVA) /100).replace(',','.')
        return ctx

    def get_named_formsets(self):
        return {
            'detallefactura': CompraInsumoFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='detallefactura'),
        }



def loadPrecioPromedio(request):
    id_insumo = request.GET.get('idinsumo')
    producto = list( Insumo.objects.filter(id = id_insumo).values_list('saldo', 'precio').all() )
    return JsonResponse({'data' : producto if producto else None}, safe=False)



def deleteDetalleInsumo(request, pk):
    try:
        detalle = CompraInsumo.objects.get(id=pk)
        idcompra = detalle.id_compra_id

    except CompraInsumo.DoesNotExist:                
        return redirect('compras:compra-update', pk=idcompra)

    detalle.delete()    
    return redirect('compras:compra-update', pk=idcompra)



@permission_required("compras.view_compra")
def ExportarExcelFacturas(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Facturas"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Facturas')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Fecha Factura', 'Guía', 'Orden de Compra', 'Rut Proveedor', 'Nombre Proveedor', 'Total Compra']

    ws.col(0).width = int(30 * 260) 
    ws.col(1).width = int(30 * 260)
    ws.col(2).width = int(30 * 260)
    ws.col(3).width = int(30 * 260)
    ws.col(4).width = int(100 * 260)
    ws.col(5).width = int(30 * 260)

    ws.write_merge(0, 0, 0, 5 , 'LISTADO FACTURAS', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    style_cantidades = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;', "$ 0,#")

    rows = Compra.objects.all().values_list('fecha_compra', 'guia', 'orden_de_compra', 'id_proveedor__rut_proveedor', 'id_proveedor__nombre_proveedor', 'total_compra')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)): 
            if (col_num == 0):
                ws.write(row_num, col_num, row[col_num].strftime('%d-%m-%Y'), style)                      
            elif col_num == 5:
                ws.write(row_num, col_num, row[col_num], style_cantidades)
            else:
                ws.write(row_num, col_num, row[col_num], style)

    wb.save(response)
    return response