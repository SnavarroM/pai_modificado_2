from dataclasses import field
from email.policy import default
from urllib import request
from django import forms
from insumos.models import Insumo

from proveedores.models import Proveedor
from .models import Compra, CompraInsumo

from django.forms import inlineformset_factory



class CompraForm(forms.ModelForm):

    id_proveedor = forms.ModelChoiceField(queryset = Proveedor.objects.all(), label = "Proveedor",
    empty_label = "Seleccione Proveedor", widget = forms.Select(attrs={'class': 'form-select detalle-header', 'width': '100%'} ))

    fecha_compra = forms.DateField(label="Fecha Compra", widget = forms.DateInput(attrs={'type':'date', 'class': 'form-control detalle-header'}))
    rut_responsable = forms.CharField(label='', widget = forms.HiddenInput(attrs={'class':'detalle-hidden d-none'}), required=False)
    descuento = forms.IntegerField(label="Descuento ($)", widget = forms.NumberInput(attrs={'class': 'form-control detalle-footer'}))
    total_neto = forms.FloatField(label = "Total Neto", widget = forms.NumberInput(attrs={'class': 'form-control disabled detalle-footer', 'readonly': 'true'}), required = False)
    total_iva = forms.FloatField(label ="Total IVA", widget = forms.NumberInput(attrs={'class': 'form-control disabled detalle-footer', 'readonly': 'true'}), required = False)
    total_compra = forms.IntegerField(label = "Total Compra", widget = forms.NumberInput(attrs={'class': 'form-control disabled detalle-footer', 'readonly': 'true'}))

    class Meta:
        model = Compra
        fields = ('id_proveedor', 'fecha_compra', 'guia', 'orden_de_compra', 'descuento', 'total_neto', 'total_iva', 'total_compra', 'rut_responsable')

        widgets = {
            'guia': forms.TextInput(attrs={'class': 'form-control detalle-header'}),
            'orden_de_compra': forms.TextInput(attrs={'class': 'form-control detalle-header'}),
        }

    def __init__(self, *args, **kwargs):
            super(CompraForm, self).__init__(*args, **kwargs)            
            self.fields['fecha_compra'].widget.format = '%Y-%m-%d'           



class CompraInsumoForm(forms.ModelForm):

    id_insumo = forms.ModelChoiceField(queryset = Insumo.objects.all(), label = "Insumo",
    empty_label = "Seleccione Insumo", widget = forms.Select(attrs={'class': 'form-select select2 col-md-2'}))

    precio_promedio = forms.FloatField(widget = forms.NumberInput(attrs={'class': 'form-control col-md-2 disabled', 'readonly': 'true'}))
    precio_con_iva = forms.FloatField(widget = forms.NumberInput(attrs={'class': 'form-control col-md-2 disabled', 'readonly': 'true'}))    
    total = forms.FloatField(label = 'Total', widget = forms.NumberInput(attrs={'class': 'form-control col-md-2 disabled fw-bold', 'readonly': 'true'}))
    precio_unitario = forms.FloatField(widget = forms.NumberInput(attrs={'class': 'form-control col-md-2', 'required': 'true'}))

    class Meta:
        model = CompraInsumo
        fields = ('id_insumo', 'cantidad', 'precio_unitario', 'precio_con_iva', 'precio_promedio', 'total')

        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control col-md-2', 'required': 'true'}),
        }



CompraInsumoFormSet = inlineformset_factory(
    Compra, CompraInsumo, form=CompraInsumoForm,
    extra=1, can_delete=False
)
