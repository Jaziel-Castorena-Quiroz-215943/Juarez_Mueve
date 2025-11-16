from rest_framework import serializers
from .models import Unidad, UbicacionTiempoReal, PuntoRuta, Ruta

class UbicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UbicacionTiempoReal
        fields = ('latitud', 'longitud', 'timestamp')

class UnidadSerializer(serializers.ModelSerializer):
    ultima_ubicacion = serializers.SerializerMethodField()

    class Meta:
        model = Unidad
        fields = ('id','identificador','tipo','ruta','ultima_ubicacion')

    def get_ultima_ubicacion(self, obj):
        ultima = obj.ubicaciones.order_by('-timestamp').first()
        if not ultima:
            return None
        return {
            'latitud': ultima.latitud,
            'longitud': ultima.longitud,
            'timestamp': ultima.timestamp
        }

class PuntoRutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuntoRuta
        fields = ("latitud", "longitud", "orden")


class RutaMapaSerializer(serializers.ModelSerializer):
    puntos = PuntoRutaSerializer(many=True)

    class Meta:
        model = Ruta
        fields = ("id", "nombre", "puntos")