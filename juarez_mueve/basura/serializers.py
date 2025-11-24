from rest_framework import serializers
from .models import UnidadRecoleccion

class UnidadRecoleccionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)
    identificador = serializers.CharField(source='codigo_unidad')
    lat = serializers.FloatField(source='latitud')
    lng = serializers.FloatField(source='longitud')
    activo = serializers.SerializerMethodField()

    def get_activo(self, obj):
        return obj.estado == "ACTIVO"

    class Meta:
        model = UnidadRecoleccion
        fields = [
            'id',
            'identificador',
            'zona',
            'lat',
            'lng',
            'activo',
            'estado',
            'ultima_actualizacion'
        ]
