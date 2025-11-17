from rest_framework import serializers
from .models import UnidadRecoleccion

class UnidadRecoleccionSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = UnidadRecoleccion
        fields = [
            'codigo_unidad',
            'zona',
            'latitud',
            'longitud',
            'estado',
            'estado_display',
            'ultima_actualizacion'
        ]
