import xlwt
import datetime


from django.conf import settings
from django.db.models import Q, Value
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils.timesince import timesince

from formularioSR.templatetags import formulariosr_filters
from formularioInsumos.templatetags import formularios_filters

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views import View

from .models import FormularioSR, FormularioSRHistorial, FormularioSRDerivacion
from user.models import UserCargo, UserDepartamento, UserProfile
from .forms import FormularioSRForm, FormularioSRHistorialForm, FormularioSRReclamoForm, FormularioSRDerivacionForm
from logs.models import Log

from extra_views import UpdateWithInlinesView, InlineFormSetFactory




class FormularioSRList(PermissionRequiredMixin, ListView):
    permission_required = 'formularioSR.view_formulariosr'    

    model = FormularioSR
    context_object_name = 'formulariosr'
    paginate_by = 10
    ordering = ['-pk']


    def get_queryset(self):
        # QuerySet por defecto
        if (self.request.user.userprofile.id_perfil.id == 4):
            queryset = FormularioSR.objects.filter(rut_jefe_aprobador = self.request.user.userprofile.rut)
        elif (self.request.user.userprofile.id_perfil.id == 2) or (self.request.user.userprofile.id_perfil.id == 5):
            queryset = FormularioSR.objects.filter(rut_solicitante = self.request.user.userprofile.rut)
        else:
            queryset = FormularioSR.objects.all()
        # Check the form value is submitted or not
        if self.request.GET.keys():
            # Verifica campo de búsqueda
            if self.request.GET.get('buscar') != '':
                keyword = self.request.GET.get('buscar')

                filtro_user = UserProfile.objects.filter(
                                                            Q(user__first_name__icontains=keyword) |
                                                            Q(user__last_name__icontains=keyword)
                                                    ).values('rut')

                try:
                    if '-' in keyword:
                        fecha_ingreso = datetime.strptime(keyword, "%d-%m-%Y").date()
                    else:
                        fecha_ingreso = None
                except Exception as e:
                    raise e

                # Query filtrado por término de búsqueda (folio, fecha_ingreso, solicitante, tipo_formulario)
                if (self.request.user.userprofile.id_perfil.id == 4):
                    queryset = FormularioSR.objects.filter(rut_jefe_aprobador__in=self.request.user.userprofile.rut).filter( 
                                                        Q(folioSR__icontains=keyword) | 
                                                        Q(tipo_formulario__icontains=keyword) |
                                                        Q(fecha_ingreso=fecha_ingreso)                                                        
                                                )

                elif (self.request.user.userprofile.id_perfil.id in list(2, 5)):
                    queryset = FormularioSR.objects.filter(rut_solicitante__in=self.request.user.userprofile.rut).filter( 
                                                        Q(folioSR__icontains=keyword) | 
                                                        Q(tipo_formulario__icontains=keyword) |
                                                        Q(fecha_ingreso=fecha_ingreso)                                                        
                                                )                    

                else:
                    queryset = FormularioSR.objects.filter( 
                                                        Q(folioSR__icontains=keyword) | 
                                                        Q(tipo_formulario__icontains=keyword) |
                                                        Q(fecha_ingreso=fecha_ingreso) |
                                                        Q(rut_solicitante__in=filtro_user)
                                                )
        return queryset



class FormularioSRDetail(PermissionRequiredMixin, DetailView):
    permission_required = ("formularioSR.view_formulariosr")

    model = FormularioSR
    context_object_name = 'formulariosr'

    def get_context_data(self, **kwargs):
        context = super(FormularioSRDetail, self).get_context_data(**kwargs)
        srhistorial = FormularioSRHistorial.objects.filter(folio_formularioSR = self.object.folioSR).order_by('-pk').first()     

        #if (self.object.tipo_formulario == 'SOLICITUD'):
        context['hist_edosolic'] = settings.ESTADO_FORMULARIOSR[srhistorial.estado_solicitud - 1][1]
        #else:
        #    context['hist_edosolic'] = settings.ESTADO_FORMULARIO[srhistorial.estado_solicitud - 1][1]

        context['hist_respuesta'] = srhistorial.comentarios
        context['hist_indicacion'] = srhistorial.indicaciones

        return context




class FormularioSRCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("formularioSR.add_formulariosr")

    model = FormularioSR
    form_class = FormularioSRForm


    def get_initial(self):
        initial = super(FormularioSRCreate, self).get_initial()

        userCargo = UserCargo.objects.filter(id_usuario=self.request.user.id)
        userDpto = UserDepartamento.objects.filter(id_usuario=self.request.user.id)
        solicitante = UserProfile.objects.filter(user=self.request.user)  

        initial.update({'email': self.request.user.email,
                        'anexo': self.request.user.userprofile.anexo,
                        'id_cargo': userCargo[0].id_cargo if userCargo else None,
                        'id_departamento': userDpto[0].id_departamento if userDpto else None,
                        'id_sub_departamento': userDpto[0].id_sub_departamento if userDpto else None,
                        'id_unidad':  userDpto[0].id_unidad if userDpto else None,
                        'rut_solicitante': solicitante[0].rut if solicitante else None,
                    })
        return initial


    def form_valid(self, form):
        super().form_valid(form) 
        formsr = form.save()

        Log.InsertarLog(self.request.user, 'Se ingresó una nueva Solicitud o Reclamo Id ' + str(self.object.pk) + " - Folio " + formsr.folioSR + " - " + formsr.tipo_formulario, 0)

        messages.success(self.request, ("Formulario ingresado con éxito."))
        return HttpResponseRedirect(reverse_lazy('formularioSR:formulariosr-list'))


    def get_success_url(self):
        idForm = self.object.pk
        return reverse_lazy('formulariosr:formulariosr-detail', kwargs={'pk': idForm})



class FormularioSRCierre(PermissionRequiredMixin, SuccessMessageMixin, View):
    permission_required = ("formularioSR.add_formulariosr", "formularioSR.add_formulariosrhistorial")

    model = FormularioSR
    form_class = FormularioSRForm
    

    def get(self, request, pk, edo):
        
        objFSR = FormularioSR.objects.get(id_formulario = pk)
        objSRHist = FormularioSRHistorial.objects.filter(id_formulario_id = pk).order_by('id_historial').last()
        
        estados = [4, 5]
        
        if (edo in estados):
            SRHistorial = FormularioSRHistorial()
            SRHistorial.id_formulario = objFSR
            SRHistorial.folio_formularioSR = objFSR.folioSR
            SRHistorial.fecha_ingreso = datetime.datetime.now().strftime('%Y-%m-%d')
            SRHistorial.hora_ingreso = datetime.datetime.now().strftime('%H:%M:%S')
            SRHistorial.comentarios = objSRHist.comentarios                                  
            SRHistorial.indicaciones = objSRHist.indicaciones                                  
            SRHistorial.estado_solicitud = edo                                  
            SRHistorial.estado = True
            SRHistorial.save()
                
            return HttpResponseRedirect(reverse_lazy('formulariosr:formulariosr-detail', kwargs={'pk': pk}))


class FormularioSRHistorialInline(InlineFormSetFactory):
    model = FormularioSRHistorial
    form_class = FormularioSRHistorialForm
    factory_kwargs = {'extra': 0, 'min_num': 1, 'max_num': 1, 'can_order': False, 'can_delete': False}




class FormularioSRReclamoInline(InlineFormSetFactory):
    model = FormularioSRHistorial
    form_class = FormularioSRReclamoForm
    factory_kwargs = {'extra': 0, 'max_num': None, 'can_order': False, 'can_delete': False}




class FormularioSRDerivacionInline(InlineFormSetFactory):
    model = FormularioSRDerivacion
    form_class = FormularioSRDerivacionForm
    factory_kwargs = {'extra': 0, 'max_num': None, 'can_order': False, 'can_delete': False}




class FormularioSRSolicitudUpdate(PermissionRequiredMixin, SuccessMessageMixin, UpdateWithInlinesView):
        permission_required = ("formularioSR.change_formulariosr", "formularioSR.change_formulariosrhistorial")

        model = FormularioSR
        form_class = FormularioSRForm
        inlines = [FormularioSRHistorialInline, FormularioSRDerivacionInline]
        template_name = 'formularioSR/formulariosr_solicitud.html'


        def get_context_data(self, **kwargs):
            ctx = super(FormularioSRSolicitudUpdate, self).get_context_data(**kwargs)            
            ctx['folio_solicitud'] = FormularioSR.objects.filter(id_formulario = self.object.pk).values_list('folioSR').first()[0]
            estados_solicitud = FormularioSRHistorial.objects.filter(id_formulario = self.object.pk).values_list('estado_solicitud').last()
            if (estados_solicitud):
                ctx['edo_solicitud'] = estados_solicitud[0]
            else: 
                ctx['edo_solicitud'] = 0
            return ctx


        def get_success_url(self):
            idForm = self.object.pk
            return reverse_lazy('formulariosr:formulariosr-detail', kwargs={'pk': idForm})



class FormularioSRReclamoUpdate(PermissionRequiredMixin, SuccessMessageMixin, UpdateWithInlinesView):
    permission_required = ("formularioSR.change_formulariosr")

    model = FormularioSR
    form_class = FormularioSRForm
    inlines = [FormularioSRReclamoInline,]
    template_name = 'formularioSR/formulariosr_solicitud.html'
    success_message = "Formulario ingresado con éxito."


    def get_context_data(self, **kwargs):
        ctx = super(FormularioSRReclamoUpdate, self).get_context_data(**kwargs)        
        ctx['folio_solicitud'] = FormularioSR.objects.filter(id_formulario = self.object.pk).values_list('folioSR').first()[0]
        return ctx


    def get_success_url(self):
        idForm = self.object.pk
        return reverse_lazy('formulariosr:formulariosr-detail', kwargs={'pk': idForm})



# Excel
@permission_required("formularioSR.view_formulariosr")
def ExportarExcelFormularioSR(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Solicitudes o Reclamos"' + datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Solicitudes-Reclamos')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Folio', 'Tipo Solicitud', 'Fecha Creación', 'Solicitante', 'Estado Solicitud', 'Tiempo Transcurrido']

    ws.col(0).width = int(30 * 260) 
    ws.col(1).width = int(30 * 260)
    ws.col(2).width = int(30 * 260)
    ws.col(3).width = int(50 * 260)
    ws.col(4).width = int(30 * 260)
    ws.col(5).width = int(30 * 260)

    ws.write_merge(0, 0, 0, 5 , 'LISTADO SOLICITUDES/RECLAMOS', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    style_cantidades = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;', "$ #,###.0")

    if (request.user.userprofile.id_perfil.id == 4):
        rows = FormularioSR.objects.filter(rut_jefe_aprobador = request.user.userprofile.rut).values_list('folioSR', 'tipo_formulario', 'folioSR', 'rut_solicitante', 'id_formulario', 'folioSR')
    elif (request.user.userprofile.id_perfil.id == 2) or (request.user.userprofile.id_perfil.id == 5):
        rows = FormularioSR.objects.filter(rut_solicitante = request.user.userprofile.rut).values_list('folioSR', 'tipo_formulario', 'folioSR', 'rut_solicitante', 'id_formulario', 'folioSR')
    else:
        rows = FormularioSR.objects.all().values_list('folioSR', 'tipo_formulario', 'folioSR', 'rut_solicitante', 'id_formulario', 'folioSR')
    

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):  
            if col_num == 2:
                ingreso = formulariosr_filters.get_fecha_hora_ingreso(row[col_num])
                ws.write(row_num, col_num, ingreso, style)
            elif col_num == 3:
                solicitante = formularios_filters.get_nombre_solicitante(row[col_num])
                ws.write(row_num, col_num, str(solicitante), style)
            elif col_num == 4:                     
                ws.write(row_num, col_num, formulariosr_filters.get_estado_solicitud(row[col_num]), style)
            elif col_num == 5:
                respuesta = formulariosr_filters.get_tiempo_respuesta(row[col_num])
                if respuesta != '':
                    ingreso = datetime.datetime.strptime(formulariosr_filters.get_fecha_hora_ingreso(row[0]), "%d-%m-%Y %H:%M:%S")
                    fecha_ingreso = datetime.datetime.strptime(str(ingreso), "%Y-%m-%d %H:%M:%S")
                    ws.write(row_num, col_num, str(formulariosr_filters.get_difer_fechas(fecha_ingreso, respuesta)), style)
                else:
                    ws.write(row_num, col_num, "", style)
            else:
                ws.write(row_num, col_num, row[col_num], style)

    wb.save(response)
    return response