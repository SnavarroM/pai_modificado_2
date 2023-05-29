from cProfile import label
from datetime import datetime, date
from email.policy import default
from secrets import choice
from sqlite3 import Date
from django import forms
from django.forms.widgets import NumberInput
from django.conf import settings

from departamentos.models import Departamento, Subdepartamento, Unidad
from cargos.models import Cargo
from user.models import UserDepartamento, UserProfile
from .models import FormularioSR, FormularioSRHistorial, FormularioSRDerivacion
from formularioSR.templatetags import formulariosr_filters



class FormularioSRForm(forms.ModelForm):

    id_departamento = forms.ModelChoiceField(queryset = Departamento.objects.all(), label = "Departamento",
    empty_label = "Seleccione Departamento", widget = forms.Select(attrs={'class': 'form-select disabled form-header', 'readonly': 'true'}))

    id_sub_departamento = forms.ModelChoiceField(queryset = Subdepartamento.objects.all(), label = "Sub Departamento",
    empty_label = "Seleccione Sub Departamento", required=False, widget = forms.Select(attrs={'class': 'form-select disabled form-header', 'readonly': 'true'}))

    id_unidad = forms.ModelChoiceField(queryset = Unidad.objects.all(), label = "Unidad",
    empty_label = "Seleccione Unidad", required=False, widget = forms.Select(attrs={'class': 'form-select disabled form-header', 'readonly': 'true'}))

    id_cargo = forms.ModelChoiceField(queryset = Cargo.objects.all(), label = "Cargo",
    empty_label = "Seleccione Cargo", widget = forms.Select(attrs={'class': 'form-select disabled form-header', 'readonly': 'true'}))

    tipo_formulario = forms.ChoiceField(choices = settings.TIPO_FORMULARIO, label = "Tipo de Formulario", widget = forms.Select(attrs={'class': 'form-select select2 form-header'}))
    fecha_ingreso = forms.DateField(label="Fecha Ingreso", initial=date.today, widget = forms.DateInput(attrs={'class': 'form-control disabled form-header'}))
    rut_solicitante = forms.CharField(label='', widget = forms.HiddenInput(attrs={'class':'d-none form-hidden'}), required=False)
    estado_solicitud = forms.CharField(label='', widget = forms.HiddenInput(attrs={'class':'d-none form-hidden'}), required=False)
    anexo = forms.CharField(label='Anexo', required=False, widget = forms.TextInput({'class': 'form-control disabled', 'readonly': 'true', 'value': 0}))

    class Meta:
        model = FormularioSR
        fields = ('fecha_ingreso', 'tipo_formulario', 'anexo', 'email', 'id_cargo', 'id_departamento', 'id_sub_departamento', 'id_unidad', 'comentarios', 'rut_solicitante', 'estado_solicitud')

        widgets = {
            'folioSR': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}),        
            #'anexo': forms.TextInput(attrs={'class': 'form-control disabled', 'readonly': 'true', 'required': 'false'}),
            'email': forms.TextInput(attrs={'class': 'form-control disabled', 'readonly': 'true'}),
            'comentarios': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input', 'readonly': 'true'}),
        }


class FuncionariosModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.first_name + ' ' + obj.last_name




class FormularioSRHistorialForm(forms.ModelForm):

    comentarios = forms.CharField(label='Respuesta', widget=forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}), required=False)

    class Meta:
        model = FormularioSRHistorial
        fields = ('comentarios', 'indicaciones')

        widgets = {
            'indicaciones': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
            #'estado_solicitud': forms.HiddenInput(),
        }


    def save(self, commit=True):        
        instance = super().save(commit=commit)

        print(">>> data historial: ", self.cleaned_data['id_historial'])
        print(">>> data formulario: ", self.cleaned_data['id_formulario'])
        print("data derivacion: ", self.data)
        print("estado: ", self.data.getlist('estado_solicitud')[0])
        

        if commit:            
            instance.save()

            respuesta = self.cleaned_data['comentarios']
            edo_solicitud = int(self.data.getlist('estado_solicitud')[0])

            if respuesta:
                edo_solicitud += 1

            SRHistorial = FormularioSRHistorial()
            SRHistorial.id_formulario = self.cleaned_data['id_formulario']
            SRHistorial.folio_formularioSR = self.cleaned_data['id_formulario'].folioSR
            SRHistorial.fecha_ingreso = datetime.now().strftime('%Y-%m-%d')
            SRHistorial.hora_ingreso = datetime.now().strftime('%H:%M:%S')
            SRHistorial.estado_solicitud = edo_solicitud
            SRHistorial.comentarios = respuesta
            SRHistorial.indicaciones = self.cleaned_data['indicaciones']
            SRHistorial.estado = True
            SRHistorial.save()

            tipo_formulario = self.data['tipo_formulario']

            if (tipo_formulario == "SOLICITUD"):
                formulariosr_filters.enviar_notificacion_derivacion(self.cleaned_data['id_formulario'], self.data, self.cleaned_data['id_historial'])




class FormularioSRReclamoForm(forms.ModelForm):

    class Meta:
        model = FormularioSRHistorial
        fields = ('comentarios',)

        widgets = {
            'comentarios': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
        }


    def save(self, commit=True):        
        instance = super().save(commit=commit)

        print(">>> data reclamo: ", self.cleaned_data)
        print("data: ", self.data)
        print("estado: ", self.data.getlist('estado_solicitud')[0])

        if commit:            
            instance.save()

            SRHistorial = FormularioSRHistorial()
            SRHistorial.folio_formularioSR = self.cleaned_data['id_formulario'].folioSR
            SRHistorial.id_formulario = self.cleaned_data['id_formulario']
            SRHistorial.fecha_ingreso = datetime.now().strftime('%Y-%m-%d')
            SRHistorial.hora_ingreso = datetime.now().strftime('%H:%M:%S')
            SRHistorial.estado_solicitud = self.data.getlist('estado_solicitud')[0]
            SRHistorial.comentarios = self.cleaned_data['comentarios']
            
            if (self.data['tipo_formulario'] == "SOLICITUD"):
                SRHistorial.indicaciones = self.data['indicaciones']
            
            SRHistorial.estado = True
            SRHistorial.save()

            respuesta = self.data['srhistorial-0-comentarios']
            if respuesta:
                print("rsp: ", respuesta)
                formulariosr_filters.enviar_notificacion_respuesta_solicitante(self)




class FormularioSRDerivacionForm(forms.ModelForm):

    rut_derivado = forms.ModelChoiceField(queryset = UserProfile.objects.all().filter(id__in = FormularioSR.get_funcionarios_adminterna()), 
                                        to_field_name="rut", label = "Derivar a", required=True, empty_label = "Seleccione Funcionario", 
                                        widget = forms.Select(attrs={'class': 'form-select select2'})
                                    )


    id_formulario = forms.HiddenInput()

    class Meta:
        model = FormularioSRDerivacion
        fields = ('rut_derivado', 'id_formulario')


    def save(self, commit=True):        
        instance = super().save(commit=commit)

        if commit:            
            instance.rut_derivado = self.cleaned_data['rut_derivado'].rut
            instance.action_on_save = True
            instance.save()

        return instance