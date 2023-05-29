import datetime
import xlwt
import os

from django.http import HttpResponse

from django.db.models import Sum, IntegerField, OuterRef, Subquery, F
from django.db.models.functions import Coalesce
from django.db import models
from django.views.generic.list import ListView
from django.template.loader import get_template
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.contrib.staticfiles import finders
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO

from cierreMensual.models import CierreMensual, CierreMensualInsumo
from formularioInsumos.models import Formulario, FormularioInsumo
from formularioSR.models import FormularioSR
from inventario.models import Inventario
from insumos.models import Insumo
from formularioInsumos.templatetags import formularios_filters
from formularioSR.templatetags import formulariosr_filters


    ##  Cierre Mensual   ##
class CierreMensualReport(PermissionRequiredMixin, ListView):
    permission_required = ("reportes.view_cierremensualinsumo")
        
    model = CierreMensualInsumo
    context_object_name = 'cierremensual'
    template_name = "reportes/cierremensual_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cierres = list(CierreMensual.objects.all().values_list('id_cierre_mensual', 'fecha_cierre'))
        context['objCierre'] = cierres

        return context


    def get_queryset(self):
        # QuerySet por defecto
        queryset = CierreMensualInsumo.objects.all()
        # Check the form value is submitted or not
        if self.request.GET.keys():
            # Verifica campo de búsqueda
            
            if self.request.GET.get('filtro') != None:
                filtro = self.request.GET.get('filtro')

            #if self.request.GET.get('buscar') != None:
            #    keyword = self.request.GET.get('buscar')                

                queryset = CierreMensualInsumo.objects.filter(id_cierre_mensual = filtro)

        return queryset




    ##  Cierre Mensual  -   Exportar a Excel   ##



@permission_required("reportes.view_cierremensualinsumo")
def CierreMensualExportarExcel(request, id):

    rows = CierreMensualInsumo.objects.filter(id_cierre_mensual = id).values_list('codigo_insumo', 'denominacion', 'id_unidad_medida__nombre_unidad_medida', 'saldo', 'precio', 'id_categoria__nombre_categoria', 'id_cierre_mensual__fecha_cierre')    
    fecha_cierre = rows[0][6].strftime('%d-%m-%Y')


    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Reporte Cierre Mensual Insumo"' + fecha_cierre + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Cierre Mensual ' + fecha_cierre)

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Código', 'Denominación', 'Unidad Medida', 'Saldo', 'Precio', 'Cuenta Presupuestaria']

    ws.col(0).width = int(20 * 260) 
    ws.col(1).width = int(100 * 260)
    ws.col(2).width = int(30 * 260)
    ws.col(3).width = int(15 * 260)
    ws.col(4).width = int(20 * 260)
    ws.col(5).width = int(50 * 260)

    ws.write_merge(0, 0, 0, 5, 'CIERRE MENSUAL INSUMOS [ ' + fecha_cierre + ' ]', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    #style.borders = borders
    
    for row in rows:
        row_num += 1
        for col_num in range(len(row)-1):
            ws.write(row_num, col_num, row[col_num], style)

    wb.save(response)
    return response



    ##  Solicitudes   ##
class SolicitudesReport(PermissionRequiredMixin, ListView):
    permission_required = ("reportes.view_formulariosr")
    
    model = FormularioSR
    context_object_name = 'formSR'
    template_name = "reportes/solicitudes_list.html"
    paginate_by = 10


    ##  Exportar a Excel   ##
@permission_required("reportes.view_formulariosr")
def SolicitudesExportarExcel(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Reporte Solicitudes Reclamos "' + str(datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S')) + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Solicitudes Reclamos ' + str(datetime.date.today().strftime('%d-%m-%Y')))

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Folio', 'Fecha Ingreso', 'Fecha Respuesta', 'Solicitante', 'Tipo Solicitud', 'Tiempo Respuesta']

    ws.col(0).width = int(20 * 260) 
    ws.col(1).width = int(20 * 260)
    ws.col(2).width = int(20 * 260)
    ws.col(3).width = int(80 * 260)
    ws.col(4).width = int(20 * 260)
    ws.col(5).width = int(20 * 260)

    ws.write_merge(0, 0, 0, 5, 'REPORTE DE SOLICITUDES', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    #style.borders = borders

    rows = FormularioSR.objects.all().values_list('folioSR', 'fecha_ingreso', 'fecha_respuesta', 'rut_solicitante', 'tipo_formulario', 'fecha_respuesta')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if (col_num in (1, 2)):
                ws.write(row_num, col_num, row[col_num].strftime('%d-%m-%Y'), style)
            elif (col_num == 3):
                ws.write(row_num, col_num, str(formularios_filters.get_nombre_solicitante(row[col_num])), style)
            elif (col_num == 5):
                ws.write(row_num, col_num, formulariosr_filters.get_difer_fechas(row[1], row[2]), style)
            else:
                ws.write(row_num, col_num, row[col_num], style)

    wb.save(response)
    return response



    ##  Inventario Productos ##
class InventarioReport(PermissionRequiredMixin, ListView):
    permission_required = ("reportes.view_inventario")
    
    model = Inventario
    context_object_name = "inventario"
    template_name = "reportes/inventario_list.html"
    paginate_by = 10

    def get_queryset(self):       
        subquery = Inventario.objects.filter(
            codigo_producto=OuterRef('codigo_insumo')
        ).values('codigo_producto', 'tipo_transaccion').annotate(
            total_cantidad=Sum('cantidad')
        ).values('codigo_producto', 'tipo_transaccion', 'total_cantidad')

        inventario = Insumo.objects.annotate(
            total_entradas=Coalesce(
                Subquery(subquery.filter(tipo_transaccion='E').values('total_cantidad')),
                0,
                output_field=IntegerField()
            ),
            total_salidas=Coalesce(
                Subquery(subquery.filter(tipo_transaccion='S').values('total_cantidad')),
                0,
                output_field=IntegerField()
            ),
            stock_actual=F('total_entradas') - F('total_salidas')
        ).values('codigo_insumo', 'denominacion', 'total_entradas', 'total_salidas', 'stock_actual').order_by('codigo_insumo')
        
        return inventario



    ##  Exportar a Excel   ##
@permission_required("reportes.view_inventario")
def InventarioExportarExcel(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Reporte Solicitudes Reclamos "' + str(datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S')) + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Inventario Productos ' + str(datetime.date.today().strftime('%d-%m-%Y')))

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Código Insumo', 'Denominación', 'Total Ingresos', 'Total Egresos', 'Stock Actual']

    ws.col(0).width = int(30 * 260) 
    ws.col(1).width = int(100 * 260)
    ws.col(2).width = int(20 * 260)
    ws.col(3).width = int(20 * 260)
    ws.col(4).width = int(20 * 260)

    ws.write_merge(0, 0, 0, 4, 'INVENTARIO DE PRODUCTOS', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    #style.borders = borders

    subquery = Inventario.objects.filter(
            codigo_producto=OuterRef('codigo_insumo')
        ).values('codigo_producto', 'tipo_transaccion').annotate(
            total_cantidad=Sum('cantidad')
        ).values('codigo_producto', 'tipo_transaccion', 'total_cantidad')

    rows = Insumo.objects.annotate(
            total_entradas=Coalesce(
                Subquery(subquery.filter(tipo_transaccion='E').values('total_cantidad')),
                0,
                output_field=IntegerField()
            ),
            total_salidas=Coalesce(
                Subquery(subquery.filter(tipo_transaccion='S').values('total_cantidad')),
                0,
                output_field=IntegerField()
            ),
            stock_actual=F('total_entradas') - F('total_salidas')
        ).values_list('codigo_insumo', 'denominacion', 'total_entradas', 'total_salidas', 'stock_actual').order_by('codigo_insumo')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], style)

    wb.save(response)
    return response



    ##  Generar Comprobante Solicitud PDF   ##
@permission_required("formularioInsumos.view_formulario", "formularioInsumos.view_formularioinsumo")
def GenerarComprobantePDF(request, id):
    solicitud = Formulario.objects.get(id_formulario=id)
    detalle = list(FormularioInsumo.objects.filter(id_folio_id=solicitud.id_formulario))

    template_path = "reportes/comprobante_solicitud.html"
    context = {'solicitud': solicitud, 'detalle': detalle}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=' + "Comprobante Solicitud Folio " + solicitud.folio +'.pdf'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error')
    return response


def link_callback(uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
        result = finders.find(uri)
        if result:
                if not isinstance(result, (list, tuple)):
                        result = [result]
                result = list(os.path.realpath(path) for path in result)
                path=result[0]
        else:
                sUrl = settings.STATIC_URL        # Typically /static/
                sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                mUrl = settings.MEDIA_URL         # Typically /media/
                mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/
                
                print(sUrl)
                print(sRoot)
                
                if uri.startswith(mUrl):
                        path = os.path.join(mRoot, uri.replace(mUrl, ""))
                elif uri.startswith(sUrl):
                        path = os.path.join(sRoot, uri.replace(sUrl, ""))
                else:
                        return uri
        # make sure that file exists
        if not os.path.isfile(path):
                raise Exception(
                        'media URI must start with %s or %s' % (sUrl, mUrl)
                )
        return path