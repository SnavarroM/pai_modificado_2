from django import forms
from .models import Categoria, Insumo, UnidadMedida


class InsumoForm(forms.ModelForm):
    
    unidad_medida = forms.ModelChoiceField(queryset=UnidadMedida.objects.all(), label="Unidad de Despacho",
    empty_label="Seleccione Unidad de Medida", widget = forms.Select(attrs={'class': 'form-select'}))

    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), label="Cuenta Presupuestaria",
    empty_label="Seleccione Categoría", widget = forms.Select(attrs={'class': 'form-select'}))

    saldo = forms.IntegerField(label="Stock", widget = forms.NumberInput(attrs={'class': 'form-control'}))

    stock_critico = forms.IntegerField(label="Stock Crítico (generar alarma)", widget = forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Insumo
        fields = ('codigo_insumo', 'denominacion', 'unidad_medida', 'saldo', 'stock_critico', 'categoria', 'estado'
        )
        
        widgets = {
            'codigo_insumo': forms.TextInput(attrs={'class': 'form-control'}),
            'denominacion': forms.TextInput(attrs={'class': 'form-control text-uppercase'}),        
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



class InsumoFormUpdate(forms.ModelForm):
    
    unidad_medida = forms.ModelChoiceField(queryset=UnidadMedida.objects.all(), label="Unidad de Despacho",
    empty_label="Seleccione Unidad de Medida", widget = forms.Select(attrs={'class': 'form-select'}))

    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), label="Cuenta Presupuestaria",
    empty_label="Seleccione Categoría", widget = forms.Select(attrs={'class': 'form-select'}))

    saldo = forms.IntegerField(label="Stock", widget = forms.NumberInput(attrs={'class': 'form-control disabled', 'readonly': 'true'}))

    stock_critico = forms.IntegerField(label="Stock Crítico (generar alarma)", widget = forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Insumo
        fields = ('codigo_insumo', 'denominacion', 'unidad_medida', 'saldo', 'stock_critico', 'categoria', 'estado'
        )
        
        widgets = {
            'codigo_insumo': forms.TextInput(attrs={'class': 'form-control disabled', 'readonly': 'true'}),
            'denominacion': forms.TextInput(attrs={'class': 'form-control text-uppercase'}),        
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



class CategoriaForm(forms.ModelForm):
        
    class Meta:
        model = Categoria
        fields = ('nombre_categoria', 'estado')
        
        widgets = {
            'nombre_categoria': forms.TextInput(attrs={'class': 'form-control text-uppercase'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class UnidadMedidaForm(forms.ModelForm):
        
    class Meta:
        model = UnidadMedida
        fields = ('nombre_unidad_medida', 'estado')
        
        widgets = {
            'nombre_unidad_medida': forms.TextInput(attrs={'class': 'form-control text-uppercase'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }