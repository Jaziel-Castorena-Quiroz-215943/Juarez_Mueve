from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from juarez_mueve.models import Empresa, Profile
from transporte.models import Ruta, Unidad
from .forms import ConductorForm, RutaForm, CamionForm
from django.shortcuts import render
from django.db.models import Count, Q
from transporte.models import Unidad, Ruta
from django.http import JsonResponse


def estadisticas(request):

    empresa_actual = getattr(request.user.profile, "empresa", None)

    filtro = {}
    if empresa_actual:
        filtro["empresa"] = empresa_actual

    unidades = Unidad.objects.filter(**filtro)

    # Conteos simples
    unidades_totales = unidades.count()
    unidades_activas = unidades.filter(activo=True).count()
    total_rutas = Ruta.objects.filter(**filtro).count()

    # Personal (conductores y recolectores)
    total_personal = Profile.objects.filter(
        rol__in=["CONDUCTOR", "RECOLECTOR"], empresa=empresa_actual
    ).count()

    transporte_activo = unidades.filter(tipo="transporte", activo=True).count()
    basura_activa = unidades.filter(tipo="basura", activo=True).count()

    # Unidades por ruta
    unidades_por_ruta = (
        unidades.values("ruta__nombre")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # Activos vs Inactivos
    activos_inactivos = {
        "activos": unidades.filter(activo=True).count(),
        "inactivos": unidades.filter(activo=False).count(),
    }

    # Distancia (estimada, por ahora)
    distancia_recorrida = unidades_activas * 12.4

    contexto = {
        "empresa_actual": empresa_actual,
        "unidades_totales": unidades_totales,
        "unidades_activas": unidades_activas,
        "total_rutas": total_rutas,
        "total_personal": total_personal,
        "transporte_activo": transporte_activo,
        "basura_activa": basura_activa,
        "unidades_por_ruta": list(unidades_por_ruta),
        "activos_inactivos": activos_inactivos,
        "distancia_recorrida": distancia_recorrida,
    }

    return render(request, "panel/estadisticas.html", contexto)

# Decorador para permitir solo usuarios administrativos
def admin_required(user):
    return hasattr(user, 'profile') and user.profile.rol in ['APP_ADMIN','EMPRESA_ADMIN','COORDINADOR_TRANSPORTE','COORDINADOR_BASURA']

@login_required
@user_passes_test(admin_required)
def dashboard(request):
    empresa_actual = request.user.profile.empresa if hasattr(request.user, 'profile') else None

    # Formularios
    conductor_form = ConductorForm()
    ruta_form = RutaForm()
    camion_form = CamionForm()

    # Manejo de POST
    if request.method == 'POST':
        if 'add_conductor' in request.POST:
            conductor_form = ConductorForm(request.POST)
            if conductor_form.is_valid():
                conductor_form.save(request)
                messages.success(request, 'Conductor agregado correctamente.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Error al agregar el conductor.')

        elif 'add_ruta' in request.POST:
            ruta_form = RutaForm(request.POST)
            if ruta_form.is_valid():
                ruta_form.save()
                messages.success(request, 'Ruta agregada correctamente.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Error al agregar la ruta.')

        elif 'add_camion' in request.POST:
            camion_form = CamionForm(request.POST)
            if camion_form.is_valid():
                camion = camion_form.save()

                # Crear unidad asociada
                Unidad.objects.create(
                    identificador = camion.identificador,
                    tipo = camion.tipo,
                    empresa = camion.empresa,
                    ruta = camion.ruta,
                    conductor = camion_form.cleaned_data.get("conductor"),
                    activo = camion.activo
                )

                messages.success(request, "Camión y unidad registrados correctamente.")
                return redirect("dashboard")

    # Datos para mostrar en la tabla
    if empresa_actual:
        unidades = Unidad.objects.filter(empresa=empresa_actual)
        total_unidades = unidades.count()
        transporte_activo = unidades.filter(tipo='transporte', activo=True).count()
        basura_activa = unidades.filter(tipo='basura', activo=True).count()
    else:
        unidades = Unidad.objects.all()
        total_unidades = unidades.count()
        transporte_activo = unidades.filter(tipo='transporte', activo=True).count()
        basura_activa = unidades.filter(tipo='basura', activo=True).count()

    context = {
        'empresa_actual': empresa_actual,
        'unidades': unidades,
        'total_unidades': total_unidades,
        'transporte_activo': transporte_activo,
        'basura_activa': basura_activa,
        'conductor_form': conductor_form,
        'ruta_form': ruta_form,
        'camion_form': camion_form,
    }

    return render(request, 'panel/dashboard.html', context)

def rutas_panel(request):
    empresa_actual = getattr(request.user.profile, "empresa", None)

    rutas = Ruta.objects.all()
    if empresa_actual:
        rutas = rutas.filter(empresa=empresa_actual)

    return render(request, "dashboard/rutas_panel.html", {
        "rutas": rutas,
        "empresa_actual": empresa_actual,
    })

def api_ruta_detalle(request, id):
    r = Ruta.objects.get(id=id)
    return JsonResponse({
        "id": r.id,
        "nombre": r.nombre,
        "numero": r.numero,
        "hora_inicio": str(r.hora_inicio),
        "hora_fin": str(r.hora_fin),
        "colonias": list(r.colonias.values_list("nombre", flat=True)),
        "unidades": list(r.unidades.values_list("identificador", flat=True)),
    })