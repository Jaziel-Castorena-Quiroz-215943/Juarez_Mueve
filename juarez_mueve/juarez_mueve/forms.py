from django import forms
from transporte.models import Unidad, Ruta


class CrearConductorForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    apellido = forms.CharField(max_length=100)
    correo = forms.EmailField()
    contraseña = forms.CharField(widget=forms.PasswordInput)
    rol = forms.ChoiceField(choices=[
        ("CONDUCTOR", "Conductor de Transporte"),
        ("RECOLECTOR", "Personal de Basura"),
    ])
    

class CrearCamionForm(forms.ModelForm):
    class Meta:
        model = Unidad
        fields = ["empresa", "identificador", "tipo", "ruta", "conductor", "activo"]

        widgets = {
            "empresa": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
            "identificador": forms.TextInput(attrs={"class": "border rounded p-2 w-full"}),
            "tipo": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
            "ruta": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
            "conductor": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
            "activo": forms.CheckboxInput(attrs={"class": "mr-2"}),
        }
