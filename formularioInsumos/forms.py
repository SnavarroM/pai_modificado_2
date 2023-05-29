from datetime import date
from django import forms
from django.forms.widgets import NumberInput
from django.forms import inlineformset_factory

from departamentos.models import Departamento, Subdepartamento, Unidad
from .models import Formulario, FormularioInsumo
from insumos.models import Insumo


class FormularioForm(forms.ModelForm):

    id_departamento = forms.ModelChoiceField(queryset = Departamento.objects.all(), label = "Departamento",
    empty_label = "Seleccione Departamento", widget = forms.Select(attrs={'class': 'form-select form-header disabled', 'readonly': 'true'}))

    id_sub_departamento = forms.ModelChoiceField(queryset = Subdepartamento.objects.all(), label = "Sub Departamento",
    empty_label = "Seleccione Sub Departamento", required=False, widget = forms.Select(attrs={'class': 'form-select form-header disabled', 'readonly': 'true'}))

    id_unidad = forms.ModelChoiceField(queryset = Unidad.objects.all(), label = "Unidad",
    empty_label = "Seleccione Unidad", required=False, widget = forms.Select(attrs={'class': 'form-select form-header disabled', 'readonly': 'true'}))

    fecha_creacion = forms.DateField(label="Fecha Creación", initial=date.today, widget = forms.DateInput(attrs={'class': 'form-control form-header disabled', 'readonly': 'true'}))

    rut_solicitante = forms.CharField(label='', widget = forms.HiddenInput(attrs={'class':'d-none form-hidden'}), required=False)
    rut_jefe_aprobador = forms.CharField(label='', widget = forms.HiddenInput(attrs={'class':'d-none form-hidden'}), required=False)
    rut_admin_interna = forms.CharField(label='', widget = forms.HiddenInput(attrs={'class':'d-none form-hidden'}), required=False)
    estado_solicitud = forms.CharField(label='', widget = forms.HiddenInput(attrs={'class':'d-none form-hidden'}), required=False)


    class Meta:
        model = Formulario
        fields = ('fecha_creacion', 'id_departamento', 'id_sub_departamento', 'id_unidad', 'rut_solicitante', 'rut_jefe_aprobador', 'rut_admin_interna', 'estado_solicitud')
        
        widgets = {
            'folio': forms.TextInput(attrs={'class': 'form-control form-header', 'disabled': 'disabled'}),        
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input', 'disabled': 'disabled'}),
        }



class FormularioInsumoForm(forms.ModelForm):

    id_insumo = forms.ModelChoiceField(queryset = Insumo.objects.all(), label = "Insumo", 
    empty_label = "Seleccione Insumo", widget = forms.Select(attrs={'class': 'form-select select2 col-md-2', 'required': 'true'}))

    class Meta:
        model = FormularioInsumo
        fields = ('id_insumo', 'cantidad')

        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control col-md-2', 'required': 'true', 'min': 1}),
        }




class FormularioInsumoJefaturaForm(forms.ModelForm):

    id_insumo = forms.ModelChoiceField(queryset = Insumo.objects.all(), label = "Insumo", 
    empty_label = "Seleccione Insumo", widget = forms.Select(attrs={'class': 'form-select disabled col-md-2', 'required': 'true'}))

    precio = forms.FloatField(widget = forms.NumberInput(attrs={'class': 'form-control disabled', 'readonly': 'true'}))

    class Meta:
        model = FormularioInsumo
        fields = ('id_insumo', 'cantidad', 'precio', 'cantidad_aprobada_jefatura')

        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control disabled col-md-2', 'required': 'true'}),
            'cantidad_aprobada_jefatura': forms.NumberInput(attrs={'class': 'form-control col-md-2', 'required': 'true'}),
        }




class FormularioInsumoAdminInternaForm(forms.ModelForm):

    id_insumo = forms.ModelChoiceField(queryset = Insumo.objects.all(), label = "Insumo", 
    empty_label = "Seleccione Insumo", widget = forms.Select(attrs={'class': 'form-select disabled col-md-2', 'required': 'true'}))

    precio = forms.FloatField(widget = forms.NumberInput(attrs={'class': 'form-control disabled', 'readonly': 'true'}))


    class Meta:
        model = FormularioInsumo
        fields = ('id_insumo', 'cantidad', 'precio', 'cantidad_aprobada_jefatura', 'cantidad_entregada')

        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control disabled col-md-2'}),
            'cantidad_aprobada_jefatura': forms.NumberInput(attrs={'class': 'form-control col-md-2 disabled'}),
            'cantidad_entregada': forms.NumberInput(attrs={'class': 'form-control col-md-2'}),
        }




class FormularioInsumoBodegaForm(forms.ModelForm):

    id_insumo = forms.ModelChoiceField(queryset = Insumo.objects.all(), label = "Insumo", 
    empty_label = "Seleccione Insumo", widget = forms.Select(attrs={'class': 'form-select disabled col-md-2', 'required': 'true'}))

    precio = forms.FloatField(widget = forms.NumberInput(attrs={'class': 'form-control disabled'}))


    class Meta:
        model = FormularioInsumo
        fields = ('id_insumo', 'cantidad', 'precio', 'cantidad_entregada')

        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control disabled col-md-2'}),
            'cantidad_entregada': forms.NumberInput(attrs={'class': 'form-control col-md-2'}),
        }




FormularioInsumoFormSet = inlineformset_factory(
    Formulario, FormularioInsumo, form=FormularioInsumoForm,
    extra=1, can_delete=False
)


FormularioInsumoJefaturaFormSet = inlineformset_factory(
    Formulario, FormularioInsumo, form=FormularioInsumoJefaturaForm,
    extra=0, can_delete=False
)


FormularioInsumoAdminInternaFormSet = inlineformset_factory(
    Formulario, FormularioInsumo, form=FormularioInsumoAdminInternaForm,
    extra=0, can_delete=False
)


FormularioInsumoBodegaFormSet = inlineformset_factory(
    Formulario, FormularioInsumo, form=FormularioInsumoBodegaForm,
    extra=0, can_delete=False
)