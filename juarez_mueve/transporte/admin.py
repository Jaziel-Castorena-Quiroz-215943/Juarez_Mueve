# transporte/admin.py
from django.contrib import admin
from .models import Ruta, PuntoRuta, Unidad

# Inline para capturar los puntos de la ruta en la misma pantalla
class PuntoRutaInline(admin.TabularInline):
    model = PuntoRuta
    extra = 1


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    inlines = [PuntoRutaInline]


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ("identificador", "tipo", "empresa", "ruta", "activo")
    list_filter = ("tipo", "empresa", "activo")
