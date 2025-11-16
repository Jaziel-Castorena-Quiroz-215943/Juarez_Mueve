from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from juarez_mueve.decorators import rol_requerido
from juarez_mueve.models import Profile, Empresa
from transporte.models import Unidad



@login_required
@rol_requerido('APP_ADMIN', 'EMPRESA_ADMIN', 'COORDINADOR_TRANSPORTE', 'COORDINADOR_BASURA')
def dashboard(request):
    profile = request.user.profile

    if profile.rol == 'APP_ADMIN':
        unidades = Unidad.objects.all()
    else:
        unidades = Unidad.objects.filter(empresa=profile.empresa)

    total_unidades = unidades.count()
    transporte_activo = unidades.filter(tipo='transporte').count()
    basura_activa = unidades.filter(tipo='basura').count()

    return render(request, "panel/dashboard.html", {
        "profile": profile,
        "empresa_actual": profile.empresa,
        "unidades": unidades,
        "total_unidades": total_unidades,
        "transporte_activo": transporte_activo,
        "basura_activa": basura_activa,
    })
