from django import forms
from django.forms import inlineformset_factory
from .models import Categoria, PresupuestoCategoria, PresupuestoDepartamento, PresupuestoSubDepartamento, \
                    Departamento, Subdepartamento


# Marco Presupuestario
class PresupuestoCategoriaForm(forms.ModelForm):

    id_categoria = forms.ModelChoiceField(queryset = Categoria.objects.all(), label = "Categoría", 
    empty_label = "Seleccione Categoría", widget = forms.Select(attrs={'class': 'form-select select2 col-md-2', 'required': 'true'}))

    class Meta:
        model = PresupuestoCategoria
        fields = ('id_categoria', 'marco_presupuestario')
        
        widgets = {
            'marco_presupuestario': forms.NumberInput(attrs={'class': 'form-control col-md-2', 'required': 'true'}),
        }



# Cabecera Asignación Presupuesto
class AsignacionPresupuestoForm(forms.ModelForm):
    id_presupuesto_categoria = forms.ModelChoiceField(queryset = Categoria.objects.all(), label = "Categoría", 
    empty_label = "Seleccione Categoría", widget = forms.Select(attrs={'class': 'form-select col-md-2 disabled'}))

    extra_marco_presupuestario = forms.Field(label = "Marco Presupuestario", required = False, widget = forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))

    class Meta:
        model = PresupuestoCategoria
        fields = ('id_presupuesto_categoria', 'extra_marco_presupuestario')



class AsignacionPresupuestoDepartamentoForm(forms.ModelForm):
    id_presupuesto_categoria = forms.ModelChoiceField(queryset = Categoria.objects.all(), label = "Categoría", 
    empty_label = "Seleccione Categoría", required=True, widget = forms.Select(attrs={'class': 'form-select disabled'}))

    id_departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), label="Departamento", 
    empty_label="Seleccione Departamento", required=True, widget = forms.Select(attrs={'class': 'form-select disabled'}))

    presupuesto = forms.FloatField(required=True, widget = forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = PresupuestoDepartamento
        fields = ('id_presupuesto_categoria', 'id_departamento', 'presupuesto')



class AsignacionPresupuestoSubDepartamentoForm(forms.ModelForm):
    id_presupuesto_categoria = forms.ModelChoiceField(queryset = Categoria.objects.all(), label = "Categoría", 
    empty_label = "Seleccione Categoría", required=True, widget = forms.Select(attrs={'class': 'form-select disabled'}))

    id_departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), label="Departamento", 
    empty_label="Seleccione Departamento", required=True, widget = forms.Select(attrs={'class': 'form-select disabled'}))

    id_subdepartamento = forms.ModelChoiceField(queryset=Subdepartamento.objects.all(), label="Sub Departamento", 
    empty_label="Seleccione Sub Departamento", required=True, widget = forms.Select(attrs={'class': 'form-select disabled'}))

    presupuesto = forms.FloatField(required=True, widget = forms.NumberInput(attrs={'class': 'form-control col-md-2'}))

    class Meta:
        model = PresupuestoSubDepartamento
        fields = ('id_presupuesto_categoria', 'id_departamento', 'id_subdepartamento', 'presupuesto')



PresupuestoDepartamentoFormSet = inlineformset_factory(
    PresupuestoCategoria, PresupuestoDepartamento, form=AsignacionPresupuestoDepartamentoForm,
    extra=0, can_delete=False
)


PresupuestoSubDepartamentoFormSet = inlineformset_factory(
    PresupuestoCategoria, PresupuestoSubDepartamento, form=AsignacionPresupuestoSubDepartamentoForm,
    extra=0, can_delete=False
)