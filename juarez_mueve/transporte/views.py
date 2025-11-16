from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Unidad, UbicacionTiempoReal
from .serializers import UnidadSerializer


def mapa_principal(request):
    return render(request, 'mapa.html')


@api_view(['GET'])
def unidades_con_ubicacion(request):
    """
    Devuelve unidades activas con su última ubicación,
    y los conteos para el panel derecho.
    """
    tipo = request.GET.get('tipo') 

    qs = Unidad.objects.all()

    if tipo in ['transporte', 'basura']:
        qs = qs.filter(tipo=tipo)

    data = []
    transporte_activo = 0
    basura_activa = 0

    for unidad in qs:
        ultima = unidad.ubicaciones.order_by('-timestamp').first()
        if not ultima:
            continue

        if unidad.tipo == 'transporte':
            transporte_activo += 1
        elif unidad.tipo == 'basura':
            basura_activa += 1

        data.append({
            'id': unidad.id,
            'identificador': unidad.identificador,
            'tipo': unidad.tipo,
            'latitud': ultima.latitud,
            'longitud': ultima.longitud,
            'timestamp': ultima.timestamp.isoformat(),
        })

    return Response({
        'unidades': data,
        'conteos': {
            'transporte_activo': transporte_activo,
            'basura_activa': basura_activa,
        }
    })


class UnidadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Unidad.objects.all()
    serializer_class = UnidadSerializer

# vista simple que devuelve solo unidades activas con ubicación (opcional)
@api_view(['GET'])
def unidades_con_ubicacion(request):
    qs = Unidad.objects.all()
    serializer = UnidadSerializer(qs, many=True)
    return Response(serializer.data)
