from django import forms
from transporte.models import Ruta, Camion
from django import forms
from django.contrib.auth.models import User
from juarez_mueve.models import Empresa, Profile

class ConductorForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    apellido = forms.CharField(max_length=100)
    correo = forms.EmailField()
    contraseña = forms.CharField(widget=forms.PasswordInput)

    def save(self, request):
        nombre = self.cleaned_data["nombre"]
        apellido = self.cleaned_data["apellido"]
        correo = self.cleaned_data["correo"]
        contraseña = self.cleaned_data["contraseña"]

        empresa = request.user.profile.empresa  # AHORA SÍ EXISTE

        # Crear usuario
        user = User.objects.create_user(
            username=correo,
            email=correo,
            password=contraseña,
            first_name=nombre,
            last_name=apellido
        )

        # Editar el perfil auto-creado
        profile = user.profile
        profile.rol = "CONDUCTOR"
        profile.empresa = empresa
        profile.save()

        return user



class RutaForm(forms.ModelForm):
    class Meta:
        model = Ruta
        fields = ['nombre', 'descripcion']


class CamionForm(forms.ModelForm):
    conductor = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__rol="CONDUCTOR"),
        required=False,
        label="Conductor asignado"
    )

    class Meta:
        model = Camion
        fields = ['identificador', 'tipo', 'empresa', 'ruta', 'activo']