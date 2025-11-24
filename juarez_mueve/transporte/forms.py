# transporte/forms.py
from django import forms
from .models import Unidad, Ruta, Queja
from juarez_mueve.models import Empresa


class RutaForm(forms.ModelForm):
    class Meta:
        model = Ruta
        fields = ["nombre", "descripcion", "origen", "destino", "color"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "w-full border rounded px-3 py-2",
                "placeholder": "Ej. Ruta Acacias – UACJ"
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "w-full border rounded px-3 py-2",
                "rows": 2,
                "placeholder": "Descripción breve de la ruta"
            }),
            "origen": forms.TextInput(attrs={
                "class": "w-full border rounded px-3 py-2",
                "placeholder": "Punto de partida (usa el buscador del mapa)",
                "id": "id_origen"
            }),
            "destino": forms.TextInput(attrs={
                "class": "w-full border rounded px-3 py-2",
                "placeholder": "Punto de llegada (usa el buscador del mapa)",
                "id": "id_destino"
            }),
            "color": forms.TextInput(attrs={
                "class": "w-full border rounded px-3 py-2",
                "type": "color",
            }),
        }


class UnidadForm(forms.ModelForm):
    class Meta:
        model = Unidad
        fields = ["identificador", "tipo", "empresa", "ruta", "activo"]
        widgets = {
            "identificador": forms.TextInput(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
                "placeholder": "Ej. UACJ-01, GOB-23, WYN-BUS-7..."
            }),
            "tipo": forms.Select(attrs={
                "class": "w-full border rounded-lg px-3 py-2"
            }),
            "empresa": forms.Select(attrs={
                "class": "w-full border rounded-lg px-3 py-2"
            }),
            "ruta": forms.Select(attrs={
                "class": "w-full border rounded-lg px-3 py-2"
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "h-4 w-4"
            }),
        }

    def __init__(self, *args, **kwargs):
        empresa_actual = kwargs.pop("empresa", None)
        es_admin_global = kwargs.pop("es_admin_global", False)
        super().__init__(*args, **kwargs)

        # Si no es admin global, solo puede elegir su empresa
        if empresa_actual and not es_admin_global:
            self.fields["empresa"].queryset = Empresa.objects.filter(id=empresa_actual.id)
            self.fields["empresa"].initial = empresa_actual
            self.fields["empresa"].disabled = True
        else:
            # admin_app ve todas
            self.fields["empresa"].queryset = Empresa.objects.filter(activo=True)

class QuejaForm(forms.ModelForm):
    class Meta:
        model = Queja
        fields = ["mensaje"]
        widgets = {
            "mensaje": forms.Textarea(attrs={
                "class": "w-full border rounded-lg p-3 h-28",
                "placeholder": "Describe tu queja…"
            })
        }
