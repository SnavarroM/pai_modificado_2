from django import forms
from .models import Configuraciones
from user.models import UserProfile



class ConfiguracionesForm(forms.ModelForm):

    rut_encargado_bodega = forms.ModelChoiceField(queryset = UserProfile.objects.all(), to_field_name="rut", label = "Encargado de Bodega",
    empty_label = "Seleccione Encargado de Bodega", widget = forms.Select(attrs={'class': 'form-select select2'}))

    rut_responsable = forms.ModelChoiceField(queryset = UserProfile.objects.all(), to_field_name="rut", label = "Responsable",
    empty_label = "Seleccione Jefe", widget = forms.Select(attrs={'class': 'form-select select2'}))

    rut_secretaria_direccion = forms.ModelChoiceField(queryset = UserProfile.objects.all(), to_field_name="rut", label = "Jefatura",
    empty_label = "Seleccione Jefe", widget = forms.Select(attrs={'class': 'form-select select2'}))
    

    class Meta:
        model = Configuraciones
        fields = ('iva', 'rut_encargado_bodega', 'rut_responsable', 'rut_secretaria_direccion')