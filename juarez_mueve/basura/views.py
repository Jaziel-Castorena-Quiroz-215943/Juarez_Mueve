from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import UnidadRecoleccion
from .serializers import UnidadRecoleccionSerializer
from django.shortcuts import render
from django.conf import settings

def mapa_basura(request):
    return render(request, "basura/basura_mapa.html", {
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY
    })

@api_view(['GET'])
def api_unidades_basura(request):
    unidades = UnidadRecoleccion.objects.all()
    serializer = UnidadRecoleccionSerializer(unidades, many=True)
    
    return Response({
        "unidades": serializer.data
    })


@api_view(['GET'])
def posiciones_camiones(request):
    unidades = UnidadRecoleccion.objects.all()

    data = []
    for u in unidades:
        data.append({
            "id": u.id,
            "codigo": u.codigo_unidad,
            "zona": u.zona,
            "estado": u.estado,
            "lat": u.latitud,
            "lng": u.longitud,
        })

    return Response({"unidades": data})

