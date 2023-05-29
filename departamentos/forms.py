from django import forms
from django.contrib.auth.models import User

from .models import Departamento, Subdepartamento, Unidad
from user.models import UserProfile


class DepartamentoForm(forms.ModelForm):

    rut_jefe = forms.ModelChoiceField(queryset = UserProfile.objects.all(), to_field_name="rut", label = "Jefatura",
    empty_label = "Seleccione Jefe", required=True, widget = forms.Select(attrs={'class': 'form-select select2', 'required':'true'}))

    rut_jefe_subrogante = forms.ModelChoiceField(queryset = UserProfile.objects.all(), to_field_name="rut", label = "Jefatura Subrogante",
    empty_label = "Seleccione Subrogante", required=False, widget = forms.Select(attrs={'class': 'form-select select2'}))


    class Meta:
        model = Departamento
        fields = ('id_dpto', 'nombre_dpto', 'rut_jefe', 'rut_jefe_subrogante')

        widgets = {
            'id_dpto': forms.NumberInput(attrs={'class': 'form-control', 'min':'0'}),
            'nombre_dpto': forms.TextInput(attrs={'class': 'form-control text-uppercase'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }



class SubDepartamentoForm(forms.ModelForm):

    departamento = forms.ModelChoiceField(queryset = Departamento.objects.all(), label = "Departamento",
    empty_label = "Seleccione Departamento", widget = forms.Select(attrs={'class': 'form-select select2',}))

    rut_jefe = forms.ModelChoiceField(queryset = UserProfile.objects.all(), to_field_name="rut", label = "Jefatura",
    empty_label = "Seleccione Jefe", widget = forms.Select(attrs={'class': 'form-select select2'}))

    rut_jefe_subrogante = forms.ModelChoiceField(queryset = UserProfile.objects.all(), to_field_name="rut", label = "Jefatura Subrogante",
    empty_label = "Seleccione Subrogante", required=False, widget = forms.Select(attrs={'class': 'form-select select2'}))


    class Meta:
        model = Subdepartamento
        fields = ('departamento', 'id_sub_dpto', 'nombre_sub_dpto', 'rut_jefe', 'rut_jefe_subrogante')

        widgets = {
            'id_sub_dpto': forms.NumberInput(attrs={'class': 'form-control', 'min':'0'}),
            'nombre_sub_dpto': forms.TextInput(attrs={'class': 'form-control text-uppercase'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }



class UnidadForm(forms.ModelForm):

    subdepartamento = forms.ModelChoiceField(queryset = Subdepartamento.objects.all(), label = "Sub Departamento",
    empty_label = "Seleccione Sub Departamento", widget = forms.Select(attrs={'class': 'form-select select2'}))

    rut_jefe = forms.ModelChoiceField(queryset = UserProfile.objects.all(), to_field_name="rut", label = "Jefatura",
    empty_label = "Seleccione Jefe", widget = forms.Select(attrs={'class': 'form-select select2'}))

    rut_jefe_subrogante = forms.ModelChoiceField(queryset = UserProfile.objects.all(), to_field_name="rut", label = "Jefatura Subrogante",
    empty_label = "Seleccione Subrogante", required=False, widget = forms.Select(attrs={'class': 'form-select select2'}))


    class Meta:
        model = Unidad
        fields = ('subdepartamento', 'id_unidad', 'nombre_unidad', 'rut_jefe', 'rut_jefe_subrogante')

        widgets = {
            'id_unidad': forms.NumberInput(attrs={'class': 'form-control', 'min':'0'}),
            'nombre_unidad': forms.TextInput(attrs={'class': 'form-control text-uppercase'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }