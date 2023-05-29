from django import forms
from .models import Cargo


class CargoForm(forms.ModelForm):

    class Meta:
        model = Cargo
        fields = ('nombre_cargo', 'estado')

        widgets = {
            'nombre_cargo': forms.TextInput(attrs={'class': 'form-control text-uppercase'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }