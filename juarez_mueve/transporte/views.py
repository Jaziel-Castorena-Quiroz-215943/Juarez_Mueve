from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from .models import Unidad
from .serializers import UnidadSerializer
from django.shortcuts import render

def mapa_principal(request):
    return render(request, 'mapa.html')


class UnidadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Unidad.objects.all()
    serializer_class = UnidadSerializer

# vista simple que devuelve solo unidades activas con ubicación (opcional)
@api_view(['GET'])
def unidades_con_ubicacion(request):
    qs = Unidad.objects.all()
    serializer = UnidadSerializer(qs, many=True)
    return Response(serializer.data)
