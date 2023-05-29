import xlwt
import datetime
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

from formularioInsumos.templatetags import formularios_filters
from departamentos.templatetags import departamentos_filters

from departamentos.models import Subdepartamento, Unidad
from insumos.models import Insumo
from .models import Formulario, FormularioHistorial, FormularioInsumo
from .forms import FormularioForm, FormularioInsumoFormSet, FormularioInsumoJefaturaFormSet, \
                FormularioInsumoAdminInternaFormSet, FormularioInsumoBodegaFormSet
from user.models import UserCargo, UserDepartamento, UserProfile
from logs.models import Log




class FormularioInsumoList(PermissionRequiredMixin, ListView):
    permission_required = ("formularioInsumos.view_formulario")

    model = Formulario
    context_object_name = 'formularios'

    paginate_by = 10
    ordering = ['-pk']


    def get_queryset(self):

        # QuerySet por defecto
        if (self.request.user.userprofile.id_perfil.id == 4):
            queryset = Formulario.objects.filter(rut_jefe_aprobador = self.request.user.userprofile.rut)
        elif (self.request.user.userprofile.id_perfil.id == 5):
            queryset = Formulario.objects.filter(rut_solicitante = self.request.user.userprofile.rut)
        else:
            queryset = Formulario.objects.all()
        
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
                        fecha_creacion = str(datetime.strptime(keyword, "%d-%m-%Y").date())
                    else:
                        fecha_creacion = None
                except Exception as e:
                    raise e
                
                # Query filtrado por término de búsqueda (folio, fecha_creacion, rut_solicitante, rut_jefe_aprobador)
                if (self.request.user.userprofile.id_perfil.id == 4):
                    queryset = Formulario.objects.filter(rut_jefe_aprobador__in=self.request.user.userprofile.rut).filter( 
                                                                            Q(folio__icontains=keyword) | 
                                                                            Q(rut_solicitante__in=filtro_user) |
                                                                            Q(fecha_creacion=fecha_creacion)                                                        
                                                                        )
                elif (self.request.user.userprofile.id_perfil.id == 5):
                    queryset = Formulario.objects.filter(rut_solicitante__in=self.request.user.userprofile.rut).filter( 
                                                                            Q(folio__icontains=keyword) | 
                                                                            Q(rut_jefe_aprobador__in=filtro_user) |
                                                                            Q(fecha_creacion=fecha_creacion)                                                        
                                                                        )
                else:
                    queryset = Formulario.objects.filter( 
                                                        Q(folio__icontains=keyword) | 
                                                        Q(rut_solicitante__in=filtro_user) |
                                                        Q(rut_jefe_aprobador__in=filtro_user) |
                                                        Q(fecha_creacion=fecha_creacion)                                                        
                                                )

        return queryset



class FormularioCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("formularioInsumos.add_formulario")
    model = Formulario
    form_class = FormularioForm

    success_message = "Solicitud de Insumo fue creada con éxito."    

    def form_valid(self, form):
        super().form_valid(form) 
        formulario = form.save()

        Log.InsertarLog(self.request.user, 'Se creó una nueva solicitud de Insumos Id ' + str(self.object.pk), 0)
        # Enviar notificación a Jefatura
        # Enviar notificación a Encargado de Bodega

        return HttpResponseRedirect(reverse_lazy('formularios:formularios-list'))




class FormularioInsumoInline():
    model = Formulario
    form_class = FormularioForm
    #template_name = "formularioInsumos/formulario_form.html"


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
        return redirect('formularios:formularios-list')


    def formset_detallesolicitud_valid(self, formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        detallesolicitud = formset.save(commit=False)
        for detsolic in detallesolicitud:
            detsolic.id_folio = self.object
            detsolic.precio = formularios_filters.get_precio_producto(detsolic.id_insumo.id)
            detsolic.save()




class FormularioInsumoCreate(SuccessMessageMixin, FormularioInsumoInline, CreateView):
    template_name = "formularioInsumos/formulario_form.html"
    success_message = "Solicitud de Insumo fue creada con éxito."
    success_url = reverse_lazy('formularios:formularios-list')


    def get_initial(self):
        initial = super(FormularioInsumoCreate, self).get_initial()

        userDpto = UserDepartamento.objects.filter(id_usuario=self.request.user.id)
        solicitante = UserProfile.objects.filter(user=self.request.user)        
        admin_interna = Subdepartamento.objects.filter(nombre_sub_dpto__icontains = "ADMINISTRACIÓN INTERNA")

        if (userDpto):
            if userDpto[0].id_unidad is not None:
                aprobador = userDpto[0].id_unidad.rut_jefe
            elif userDpto[0].id_sub_departamento is not None:
                aprobador = userDpto[0].id_sub_departamento.rut_jefe                
            elif userDpto[0].id_departamento is not None:
                aprobador = userDpto[0].id_departamento.rut_jefe
        else:
            aprobador = None

        if (admin_interna):
            if admin_interna[0].rut_jefe is not None:
                jefe_admint = admin_interna[0].rut_jefe

        initial.update({'id_departamento': userDpto[0].id_departamento if userDpto else None,
                        'id_sub_departamento': userDpto[0].id_sub_departamento if userDpto else None,
                        'id_unidad': userDpto[0].id_unidad if userDpto else None,
                        'rut_solicitante': solicitante[0].rut if solicitante else None,
                        'rut_jefe_aprobador': aprobador,
                        'rut_admin_interna': jefe_admint,
                    })
        return initial


    def get_context_data(self, **kwargs):
        ctx = super(FormularioInsumoCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx


    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'detallesolicitud': FormularioInsumoFormSet(prefix='detallesolicitud')
            }
        else:
            return {
                'detallesolicitud': FormularioInsumoFormSet(self.request.POST or None, self.request.FILES or None, prefix='detallesolicitud'),
            }




class FormularioInsumoJefatura(SuccessMessageMixin, FormularioInsumoInline, UpdateView):
    template_name = "formularioInsumos/formulario_form_jefatura.html"
    #success_message = "Solicitud de Insumo fue aprobada con éxito."
    #success_url = reverse_lazy('formularios:formularios-list')


    def get_context_data(self, **kwargs):
        ctx = super(FormularioInsumoJefatura, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        ctx['folio_solicitud'] = Formulario.objects.filter(id_formulario = self.object.pk).values_list('folio').first()[0]
        return ctx


    def get_named_formsets(self):
            return {
                'detallesolicitud': FormularioInsumoJefaturaFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='detallesolicitud')
            }


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()


        if form.is_valid():
            form_jefatura = form.save(commit=False)
            
            named_formsets = self.get_named_formsets()
            for name, formset in named_formsets.items():
                detsolic = formset.save(commit=False)
                for d in detsolic:
                    d.save()

            form_jefatura.save()

            edoSolicitud = self.request.POST.get('estado_solicitud')
            formularios_filters.set_formulario_historial(self, edoSolicitud)   


            if (edoSolicitud == '2'):
                formularios_filters.enviar_notificacion_aprobacion_jefatura(self, form_jefatura)

            if (edoSolicitud == '5'):
                formularios_filters.enviar_notificacion_rechazo(self, form_jefatura)


            # SHistorial = FormularioHistorial()
            # SHistorial.id_folio_formulario = self.object
            # SHistorial.estado_formulario = edoSolicitud
            # SHistorial.rut_gestor = self.request.user.userprofile.rut
            # SHistorial.estado = True
            # SHistorial.save()
            
            Log.InsertarLog(self.request.user, 'Se actualizó el estado de la Solicitud Id ' + str(self.object.pk) + " a " + settings.ESTADO_APROBACION_SOLICITUD[int(edoSolicitud)-1][1], 0)

            messages.success(request, ("Solicitud de Insumo fue actualizada con éxito."))
            return HttpResponseRedirect(reverse_lazy('formularios:formularios-list'))




class FormularioInsumoAdminInterna(SuccessMessageMixin, FormularioInsumoInline, UpdateView):
    template_name = "formularioInsumos/formulario_form_admin_interna.html"
    success_message = "Solicitud de Insumo fue aprobada con éxito."
    success_url = reverse_lazy('formularios:formularios-list')


    def get_context_data(self, **kwargs):
        ctx = super(FormularioInsumoAdminInterna, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        ctx['folio_solicitud'] = Formulario.objects.filter(id_formulario = self.object.pk).values_list('folio').first()[0]
        return ctx


    def get_named_formsets(self):
            return {
                'detallesolicitud': FormularioInsumoAdminInternaFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='detallesolicitud')
            }


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            form_admin = form.save(commit=False)
            edoSolicitud = self.request.POST.get('estado_solicitud')
            
            named_formsets = self.get_named_formsets()
            for name, formset in named_formsets.items():
                detsolic = formset.save(commit=False)
                for d in detsolic:
                    d.save()

                    if (edoSolicitud == '3'):
                        Insumo.disminuir_cantidad_insumo(d.id_insumo.codigo_insumo, d.cantidad_aprobada_jefatura, d.id_folio.rut_solicitante)

            form_admin.save()

            formularios_filters.set_formulario_historial(self, edoSolicitud)
        
            if (edoSolicitud == '3'):    
                #formularios_filters.get_tabla_resumen_solicitud(form_admin)
                formularios_filters.enviar_notificacion_aprobacion_adminterna(self, form_admin)
            
            # SHistorial = FormularioHistorial()
            # SHistorial.id_folio_formulario = self.object
            # SHistorial.estado_formulario = edoSolicitud
            # SHistorial.rut_gestor = self.request.user.userprofile.rut
            # SHistorial.estado = True
            # SHistorial.save()

            #print (self.object.pk, self.request.POST.get('rut_solicitante'))
            formularios_filters.set_inventario_solicitud(self.object.pk, self.request.POST.get('rut_solicitante'))

            Log.InsertarLog(self.request.user, 'Se actualizó el estado de la Solicitud Id ' + str(self.object.pk) + " a " + settings.ESTADO_APROBACION_SOLICITUD[int(edoSolicitud)-1][1], 0)

            messages.success(request, ("Solicitud de Insumo fue actualizada con éxito."))
            return HttpResponseRedirect(reverse_lazy('formularios:formularios-list'))




class FormularioInsumoBodega(SuccessMessageMixin, FormularioInsumoInline, UpdateView):
    template_name = "formularioInsumos/formulario_form_encargado_bodega.html"


    def get_context_data(self, **kwargs):
        ctx = super(FormularioInsumoBodega, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        ctx['folio_solicitud'] = Formulario.objects.filter(id_formulario = self.object.pk).values_list('folio').first()[0]
        return ctx


    def get_named_formsets(self):
            return {
                'detallesolicitud': FormularioInsumoBodegaFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='detallesolicitud')
            }


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        edoSolicitud = self.request.POST.get('estado_solicitud')

        formularios_filters.set_formulario_historial(self, edoSolicitud)

        # SHistorial = FormularioHistorial()
        # SHistorial.id_folio_formulario = self.object
        # SHistorial.estado_formulario = edoSolicitud
        # SHistorial.rut_gestor = self.request.user.userprofile.rut
        # SHistorial.estado = True
        # SHistorial.save()

        Log.InsertarLog(self.request.user, 'Se actualizó el estado de la Solicitud Id ' + str(self.object.pk) + " a " + settings.ESTADO_APROBACION_SOLICITUD[int(edoSolicitud)-1][1], 0)

        messages.success(request, ("Solicitud de Insumo fue entregada con éxito."))
        return HttpResponseRedirect(reverse_lazy('formularios:formularios-list'))



def InsumossinStock(request):
    productos = list( Insumo.objects.filter(saldo = 0).values_list('id').all() )
    return JsonResponse({'data' : productos if productos else None}, safe=False)



# Excel
@permission_required("formularioInsumos.view_formulario")
def ExportarExcelFormulario(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Lista de Solicitud de Insumos"' + datetime.now().strftime('%d-%m-%Y %H.%M.%S') + '".xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Solicitud de Insumos')

    #Cabecera hoja, primera fila
    row_num = 2

    header_style = xlwt.easyxf('font:height 200, bold True; pattern: pattern solid, fore_colour indigo; font: colour white, bold True; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')

    columns = ['Folio', 'Fecha Solicitud', 'Solicitante', 'Costo', 'Estado', 'Autoriza']

    ws.col(0).width = int(30 * 260) 
    ws.col(1).width = int(30 * 260)
    ws.col(2).width = int(50 * 260)
    ws.col(3).width = int(30 * 260)
    ws.col(4).width = int(50 * 260)
    ws.col(5).width = int(50 * 260)

    ws.write_merge(0, 0, 0, 5 , 'LISTADO SOLICITUD DE INSUMOS', header_style)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    style = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;')
    style_cantidades = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;', "$ #,###.0")

    if (request.user.userprofile.id_perfil.id == 4):
        rows = Formulario.objects.filter(rut_jefe_aprobador = request.user.userprofile.rut).values_list('folio', 'fecha_creacion', 'rut_solicitante', 'id_formulario', 'id_formulario', 'rut_jefe_aprobador')
    elif (request.user.userprofile.id_perfil.id == 5):
        rows = Formulario.objects.filter(rut_solicitante = request.user.userprofile.rut).values_list('folio', 'fecha_creacion', 'rut_solicitante', 'id_formulario', 'id_formulario', 'rut_jefe_aprobador')
    else:
        rows = Formulario.objects.all().values_list('folio', 'fecha_creacion', 'rut_solicitante', 'id_formulario', 'id_formulario', 'rut_jefe_aprobador')

    
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):

            if col_num == 2:
                    solicitante = formularios_filters.get_nombre_solicitante(str(row[col_num]))
                    ws.write(row_num, col_num, str(solicitante), style) 

            elif col_num == 3: 
                costo = formularios_filters.get_costo_formulario(row[col_num])                    
                ws.write(row_num, col_num, '$ ' + str(costo), style)

            elif col_num == 4:
                edo_solicitud = formularios_filters.get_edo_solicitud_insumo(row[col_num])
                ws.write(row_num, col_num, edo_solicitud, style)

            elif col_num == 5:
                    jefe = departamentos_filters.get_nombre_jefe(row[col_num])
                    ws.write(row_num, col_num, str(jefe), style)

            else:
                ws.write(row_num, col_num, row[col_num], style)

    wb.save(response)
    return response