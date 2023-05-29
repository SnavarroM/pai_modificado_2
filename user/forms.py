from http.client import REQUEST_ENTITY_TOO_LARGE
from tabnanny import verbose
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from departamentos.models import Departamento, Subdepartamento, Unidad
from cargos.models import Cargo
from .models import Perfil, UserCargo, UserDepartamento, UserProfile


class RegisterForm(UserCreationForm):

    rut = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', }))
    first_name = forms.CharField(max_length=100,required=True,widget=forms.TextInput(attrs={'class': 'form-control',}), label="Nombre")
    last_name = forms.CharField(max_length=100,required=True,widget=forms.TextInput(attrs={'class': 'form-control', }), label="Apellido")
    username = forms.CharField(max_length=100,required=True,widget=forms.TextInput(attrs={'class': 'form-control', }), label="Usuario")
    email = forms.EmailField(required=True,widget=forms.TextInput(attrs={'class': 'form-control',}), label="Email")
    password1 = forms.CharField(max_length=50,required=True,widget=forms.PasswordInput(attrs={'class': 'form-control','data-toggle': 'password','id': 'password',}), label="Password")
    password2 = forms.CharField(max_length=50,required=True,widget=forms.PasswordInput(attrs={'class': 'form-control','data-toggle': 'password','id': 'password',}), label="Confirmar Password")
    anexo = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control',}), label="Anexo")


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username','email', 'password1', 'password2', 'rut', 'anexo')



class LoginForm(forms.ModelForm):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class':'form-control', }), label="Usuario")
    password = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput(attrs={'class':'form-control','data-toggle':'password','id':'password',}), label="Password")

    class Meta:
        model = User
        fields = ('username', 'password')
        excludes = ('first_name', 'last_name', 'email')



# Edición y Asignación de Perfiles, Departamentos, Cargos a Usuarios

class UsuarioForm(forms.ModelForm):

    first_name = forms.CharField(max_length=100,required=True,widget=forms.TextInput(attrs={'class': 'form-control',}), label="Nombre")
    last_name = forms.CharField(max_length=100,required=True,widget=forms.TextInput(attrs={'class': 'form-control', }), label="Apellido")
    username = forms.CharField(max_length=100,required=True,widget=forms.TextInput(attrs={'class': 'form-control disabled', }), label="Usuario")
    email = forms.EmailField(required=True,widget=forms.TextInput(attrs={'class': 'form-control',}), label="Email")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username','email')
        excludes = ('password1', 'password2')



class PerfilForm(forms.ModelForm):

    class Meta:
        model = Perfil
        fields = ('nombre_perfil', 'estado')

        widgets = {
            'nombre_perfil': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }



class UserProfileForm(forms.ModelForm):

    rut = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control disabled'}))
    anexo = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control',}), label="Anexo")
    id_perfil = forms.ModelChoiceField(queryset=Perfil.objects.all(), empty_label="Seleccione Perfil de Usuario", label="Perfil Usuario", widget = forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = UserProfile
        fields = ('rut', 'anexo', 'id_perfil')



class UserDepartamentoForm(forms.ModelForm):

    id_departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), empty_label="Seleccione Departamento", label="Departamento", widget = forms.Select(attrs={'class': 'form-select', 'id':'id_user_departamento'}))
    id_sub_departamento = forms.ModelChoiceField(queryset=Subdepartamento.objects.all(), empty_label="Seleccione Subdepartamento", required=False, label="Sub Departamento", widget = forms.Select(attrs={'class': 'form-select', 'id':'id_user_subdepartamento'}))
    id_unidad = forms.ModelChoiceField(queryset=Unidad.objects.all(), empty_label="Seleccione Unidad", label="Unidad", required=False, widget = forms.Select(attrs={'class': 'form-select', 'id':'id_user_unidad'}))
    
    class Meta:
        model = UserDepartamento
        fields = ('id_departamento', 'id_sub_departamento', 'id_unidad')



class UserCargoForm(forms.ModelForm):

    id_cargo = forms.ModelChoiceField(queryset=Cargo.objects.all(), empty_label="Seleccione Cargo", label="Cargo", widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = UserCargo
        fields = ('id_cargo',)
