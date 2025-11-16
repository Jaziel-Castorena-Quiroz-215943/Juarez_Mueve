from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from juarez_mueve.models import Profile, Empresa
from transporte.models import Unidad


@login_required
def dashboard(request):
    # 🔹 Esto crea el Profile si no existía
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Solo estos roles pueden entrar al panel
    if profile.rol not in ['APP_ADMIN', 'EMPRESA_ADMIN', 'COORDINADOR']:
        return HttpResponseForbidden("No tienes permiso para ver este panel.")

    if profile.rol == 'APP_ADMIN':
        empresa_actual = None
        empresas = Empresa.objects.filter(activo=True)
        unidades = Unidad.objects.all()
    else:
        empresa_actual = profile.empresa
        empresas = Empresa.objects.filter(id=empresa_actual.id) if empresa_actual else Empresa.objects.none()
        unidades = Unidad.objects.filter(empresa=empresa_actual) if empresa_actual else Unidad.objects.none()

    total_unidades = unidades.count()
    transporte_activo = unidades.filter(tipo='transporte', activo=True).count()
    basura_activa = unidades.filter(tipo='basura', activo=True).count()

    context = {
        'profile': profile,
        'empresa_actual': empresa_actual,
        'empresas': empresas,
        'total_unidades': total_unidades,
        'transporte_activo': transporte_activo,
        'basura_activa': basura_activa,
        'unidades': unidades.select_related('ruta', 'empresa'),
    }
    return render(request, 'panel/dashboard.html', context)
