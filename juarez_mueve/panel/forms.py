from django import forms
from juarez_mueve.models import Conductor, Ruta, Camion

class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        fields = ['nombre', 'licencia', 'empresa']

class RutaForm(forms.ModelForm):
    class Meta:
        model = Ruta
        fields = ['nombre', 'descripcion', 'empresa']

class CamionForm(forms.ModelForm):
    class Meta:
        model = Camion
        fields = ['identificador', 'tipo', 'empresa', 'ruta', 'activo']
