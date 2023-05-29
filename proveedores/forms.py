from django import forms

from .models import Proveedor


class ProveedorForm(forms.ModelForm):

    class Meta:
        model = Proveedor
        fields = ('rut_proveedor', 'nombre_proveedor', 'estado')

        widgets = {
            'rut_proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_proveedor': forms.TextInput(attrs={'class': 'form-control text-uppercase'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }