from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import render
from django.http import JsonResponse
from django.apps import apps 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from .forms import RutaForm
from .models import Unidad, Ruta
from .serializers import UnidadSerializer
from .google_directions import obtener_puntos_ruta
from .models import PuntoRuta


def mapa_principal(request):
    """
    Vista principal del mapa.
    """
    return render(request, 'mapa.html')


def mapa_ciudad(request):
    """
    Alias por si en algún lado aún se usa 'mapa_ciudad'.
    """
    return render(request, 'mapa.html')


class UnidadViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API REST básica para consultar unidades.
    """
    queryset = Unidad.objects.all()
    serializer_class = UnidadSerializer


@api_view(['GET'])
def unidades_con_ubicacion(request):
    """
    API que devuelve las unidades usando el serializer actual.
    """
    qs = Unidad.objects.all()
    serializer = UnidadSerializer(qs, many=True)
    return Response(serializer.data)


def api_unidades(request):
    """
    API para el mapa que combina:
    - Unidades de transporte (modelo Unidad, tipo='transporte')
    - Unidades de recolección de basura (modelo UnidadRecoleccion en app 'basura')
    Devuelve también conteos.
    """
    # Transporte público desde Unidad
    transportes = []
    qs_transporte = (
        Unidad.objects
        .filter(activo=True, tipo='transporte')
        .select_related('ruta')
        .prefetch_related('ubicaciones')
    )

    for u in qs_transporte:
        ultima_ubicacion = u.ubicaciones.order_by('-timestamp').first()

        transportes.append({
            "id": u.id,
            "nombre": u.identificador,
            "numero_economico": u.identificador,
            # IMPORTANTE: aquí mandamos el ID numérico de la ruta
            "ruta": u.ruta.id if u.ruta else None,
            "ruta_nombre": u.ruta.nombre if u.ruta else None,
            "latitud": ultima_ubicacion.latitud if ultima_ubicacion else None,
            "longitud": ultima_ubicacion.longitud if ultima_ubicacion else None,
            "estado": "ACTIVO" if u.activo else "INACTIVO",
        })

    # Modelo UnidadRecoleccion desde la app 'basura'
    UnidadRecoleccion = apps.get_model('basura', 'UnidadRecoleccion')

    basura_qs = UnidadRecoleccion.objects.filter(estado='ACTIVO').values(
        'id', 'nombre', 'codigo_unidad', 'zona',
        'latitud', 'longitud', 'estado'
    )

    basura = list(basura_qs)

    data = {
        "transportes": transportes,
        "basura": basura,
        "conteos": {
            "transportes_activos": len(transportes),
            "basura_activa": len(basura),
        }
    }
    return JsonResponse(data)

@api_view(["GET"])
def rutas_mapa(request):
    """
    Devuelve rutas con origen/destino, coordenadas y puntos.
    """
    rutas = Ruta.objects.all()
    data = []

    for ruta in rutas:
        puntos_lista = [
            {"lat": p.latitud, "lng": p.longitud}
            for p in ruta.puntos.all().order_by("orden")
        ]

        data.append({
            "id": ruta.id,
            "nombre": ruta.nombre,
            "origen": ruta.origen,
            "destino": ruta.destino,

            # ⬇️ Coordenadas añadidas (ANTES NO SE ENVIABAN)
            "origen_lat": ruta.origen_lat,
            "origen_lng": ruta.origen_lng,
            "destino_lat": ruta.destino_lat,
            "destino_lng": ruta.destino_lng,

            "color": ruta.color or "#2563eb",
            "puntos": puntos_lista,
        })

    return Response({"rutas": data})


def es_coordinador(user):
    # Ajusta esto a tu realidad: grupo, permiso, etc.
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(es_coordinador)
def gestionar_rutas(request):
    from .models import Ruta

    rutas = Ruta.objects.all().order_by("id")

    if request.method == "POST":
        form = RutaForm(request.POST)
        if form.is_valid():
            ruta = form.save()  # Guardamos ruta

            # Obtener puntos reales desde Google Directions
            if ruta.origen and ruta.destino:
                puntos = obtener_puntos_ruta(ruta.origen, ruta.destino)

                # Borrar puntos anteriores
                PuntoRuta.objects.filter(ruta=ruta).delete()

                # Guardar los nuevos puntos
                for idx, (lat, lng) in enumerate(puntos, start=1):
                    PuntoRuta.objects.create(
                        ruta=ruta,
                        orden=idx,
                        latitud=lat,
                        longitud=lng
                    )

            return redirect("gestionar_rutas")
    else:
        form = RutaForm()

    context = {
        "form": form,
        "rutas": rutas,
    }
    return render(request, "gestionar_rutas.html", context)
