# transporte/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from juarez_mueve.decorators import rol_requerido

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Unidad, Ruta
from .serializers import UnidadSerializer
from .forms import UnidadForm, RutaForm
from juarez_mueve.models import Profile


# ==========================
#   VISTA DEL MAPA PRINCIPAL
# ==========================
@login_required
def mapa_principal(request):
    return render(request, 'mapa.html')


# ==========================
#   API REST PARA EL MAPA
# ==========================
class UnidadViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UnidadSerializer

    def get_queryset(self):
        qs = Unidad.objects.filter(activo=True)

        # Filtro por tipo (transporte o basura)
        tipo = self.request.query_params.get("tipo")
        if tipo in ["transporte", "basura"]:
            qs = qs.filter(tipo=tipo)

        # Filtro por empresa según el usuario logueado
        user = self.request.user
        profile = getattr(user, "profile", None)

        if profile and profile.empresa and profile.rol != "admin_app":
            qs = qs.filter(empresa=profile.empresa)

        return qs


@api_view(["GET"])
def unidades_con_ubicacion(request):
    """
    API actual que usas para pintar marcadores de unidades.
    """
    qs = Unidad.objects.all().select_related("ruta", "empresa")
    serializer = UnidadSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def rutas_mapa(request):
    rutas = Ruta.objects.prefetch_related("puntos").all()
    data = []
    for ruta in rutas:
        puntos = [
            {"latitud": p.latitud, "longitud": p.longitud, "orden": p.orden}
            for p in ruta.puntos.all().order_by("orden")
        ]
        data.append({
            "id": ruta.id,
            "nombre": ruta.nombre,
            "descripcion": ruta.descripcion,
            "color": getattr(ruta, "color", "#2563eb"),
            "puntos": puntos,
        })
    return Response({"rutas": data})


def api_rutas(request):
    rutas = Ruta.objects.all()
    data = []

    for ruta in rutas:
        puntos = ruta.puntos.order_by("orden").values("latitud", "longitud")
        data.append({
            "id": ruta.id,
            "nombre": ruta.nombre,
            "descripcion": ruta.descripcion,
            "puntos": list(puntos)
        })

    return JsonResponse({"rutas": data})
# ==========================
#   VISTAS ADMIN (CRUD)
# ==========================

def _get_profile(request):
    return Profile.objects.get(user=request.user)


def _get_empresa_actual(request):
    profile = _get_profile(request)
    # admin_app ve todas, otros solo su empresa
    return None if profile.rol == "admin_app" else profile.empresa


@login_required
@rol_requerido('APP_ADMIN', 'EMPRESA_ADMIN', 'COORDINADOR_TRANSPORTE', 'COORDINADOR_BASURA')
def listar_unidades(request):
    profile = request.user.profile

    # Admin general ve todo
    if profile.rol == 'APP_ADMIN':
        unidades = Unidad.objects.all()
    else:
        unidades = Unidad.objects.filter(empresa=profile.empresa)

    filtro = request.GET.get('tipo')

    if filtro and filtro != "todas":
        unidades = unidades.filter(tipo=filtro)

    return render(request, 'transporte/unidades_list.html', {
        'unidades': unidades,
        'filtro': filtro or "todas"
    })


@login_required
@rol_requerido('APP_ADMIN', 'EMPRESA_ADMIN')
def crear_unidad(request):
    if request.method == "POST":
        form = UnidadForm(request.POST)
        if form.is_valid():
            unidad = form.save(commit=False)
            if request.user.profile.rol != "APP_ADMIN":
                unidad.empresa = request.user.profile.empresa
            unidad.save()
            messages.success(request, "Unidad creada correctamente.")
            return redirect('listar_unidades')
    else:
        form = UnidadForm()

    return render(request, 'transporte/unidad_form.html', {'form': form})


@login_required
@rol_requerido('APP_ADMIN', 'EMPRESA_ADMIN', 'COORDINADOR_TRANSPORTE', 'COORDINADOR_BASURA')
def editar_unidad(request, pk):
    unidad = get_object_or_404(Unidad, pk=pk)

    form = UnidadForm(request.POST or None, instance=unidad)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Unidad modificada correctamente.")
        return redirect('listar_unidades')

    return render(request, 'transporte/unidad_form.html', {'form': form})


@login_required
@rol_requerido('APP_ADMIN', 'EMPRESA_ADMIN')
def toggle_unidad(request, pk):
    unidad = get_object_or_404(Unidad, pk=pk)
    unidad.activa = not unidad.activa
    unidad.save()
    return redirect('listar_unidades')


@login_required
def toggle_unidad_activa(request, pk):
    profile = _get_profile(request)
    empresa_actual = _get_empresa_actual(request)

    if profile.rol not in ["admin_app", "admin_empresa"]:
        messages.error(request, "No tienes permiso para modificar unidades.")
        return redirect("unidades_lista")

    unidad = get_object_or_404(Unidad, pk=pk)

    if empresa_actual and unidad.empresa != empresa_actual and profile.rol != "admin_app":
        messages.error(request, "No puedes modificar unidades de otra empresa.")
        return redirect("unidades_lista")

    unidad.activo = not unidad.activo
    unidad.save()
    messages.success(request, f"Unidad {'activada' if unidad.activo else 'desactivada'} correctamente.")
    return redirect("unidades_lista")


# ==========================
#   CRUD de Rutas
# ==========================
@login_required
def lista_rutas(request):
    empresa_actual = _get_empresa_actual(request)

    # Por ahora las rutas no dependen de empresa, pero se puede adaptar.
    rutas = Ruta.objects.all().order_by("nombre")

    context = {
        "rutas": rutas,
        "empresa_actual": empresa_actual,
    }
    return render(request, "transporte/rutas_lista.html", context)


@login_required
def crear_ruta(request):
    profile = _get_profile(request)

    if profile.rol not in ["admin_app", "admin_empresa"]:
        messages.error(request, "No tienes permiso para crear rutas.")
        return redirect("rutas_lista")

    if request.method == "POST":
        form = RutaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ruta creada correctamente.")
            return redirect("rutas_lista")
    else:
        form = RutaForm()

    return render(request, "transporte/ruta_form.html", {
        "form": form,
        "modo": "crear",
    })


@login_required
def editar_ruta(request, pk):
    profile = _get_profile(request)

    if profile.rol not in ["admin_app", "admin_empresa"]:
        messages.error(request, "No tienes permiso para editar rutas.")
        return redirect("rutas_lista")

    ruta = get_object_or_404(Ruta, pk=pk)

    if request.method == "POST":
        form = RutaForm(request.POST, instance=ruta)
        if form.is_valid():
            form.save()
            messages.success(request, "Ruta actualizada correctamente.")
            return redirect("rutas_lista")
    else:
        form = RutaForm(instance=ruta)

    return render(request, "transporte/ruta_form.html", {
        "form": form,
        "modo": "editar",
        "ruta": ruta,
    })
