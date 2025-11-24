from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import render
from django.http import JsonResponse
from django.apps import apps 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from .forms import RutaForm, QuejaForm
from .models import Unidad, Ruta, Queja, UbicacionTiempoReal
from .serializers import UnidadSerializer
from .google_directions import obtener_puntos_ruta
from .models import PuntoRuta
from django.db.models import OuterRef, Subquery


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

def enviar_queja(request):
    if request.method == "POST":
        mensaje = request.POST.get("mensaje", "").strip()

        if not mensaje:
            return JsonResponse({"ok": False, "error": "Mensaje vacío"})

        queja = Queja.objects.create(
            usuario=request.user if request.user.is_authenticated else None,
            mensaje=mensaje
        )

        return JsonResponse({"ok": True})

    return JsonResponse({"ok": False, "error": "Método inválido"})

def api_unidades(request):
    """
    Devuelve JSON con las últimas ubicaciones de unidades.
    Estructura devuelta:
    {
        "transportes": [{id, identificador, latitud, longitud, ruta, nombre, numero_economico, ...}, ...],
        "basura": [...]
    }
    """
    # Obtener todas las unidades activas
    unidades = Unidad.objects.filter(activo=True)

    transportes_list = []
    basura_list = []

    # Alternativa eficiente: iterar y obtener última ubicación por unidad
    for u in unidades:
        last = u.ubicaciones.order_by('-timestamp').first()
        if not last:
            continue

        item = {
            "id": u.id,
            "identificador": u.identificador,
            "latitud": last.latitud,
            "longitud": last.longitud,
            "ruta": u.ruta.id if u.ruta else None,
            "ruta_nombre": u.ruta.nombre if u.ruta else None,
            "tipo": u.tipo,
            "nombre": getattr(u, "nombre", None) or u.identificador,
            # añade campos adicionales si los tienes en tu modelo/unidad
        }

        if u.tipo == "transporte":
            transportes_list.append(item)
        else:
            basura_list.append(item)

    return JsonResponse({
        "transportes": transportes_list,
        "basura": basura_list
    })

def api_unidades_basura(request):
    UnidadRecoleccion = apps.get_model("basura", "UnidadRecoleccion")

    qs = UnidadRecoleccion.objects.filter(estado="ACTIVO")

    unidades = []

    for u in qs:
        unidades.append({
            "id": u.id,
            "identificador": u.codigo_unidad,
            "zona": u.zona,
            "lat": u.latitud,
            "lng": u.longitud,
            "estado": u.estado,
        })

    return JsonResponse({"unidades": unidades})