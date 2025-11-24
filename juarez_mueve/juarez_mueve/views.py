from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings

from juarez_mueve.models import Profile, Empresa
from transporte.models import Unidad, Ruta, UbicacionTiempoReal
from .forms import CrearConductorForm, CrearCamionForm


# ============================================================
#                        INDEX
# ============================================================

def index(request):
    beneficios = [
        "Geolocalización Precisa",
        "Mayor Eficiencia",
        "Transparencia",
        "Multiplataforma",
        "Datos en Tiempo Real",
        "Panel Administrativo"
    ]
    return render(request, 'juarez_mueve/index.html', {
        'beneficios': beneficios
    })


# ============================================================
#                        LOGIN
# ============================================================

def login_view(request):
    return render(request, "juarez_mueve/login.html")


# ============================================================
#                   REGISTRO CIUDADANO
# ============================================================

def signup(request):
    if request.method == "POST":
        fields = ["first_name", "last_name", "email", "username",
                  "phone", "neighborhood", "password1", "password2"]
        data = {f: request.POST.get(f) for f in fields}

        # Validaciones
        if data["password1"] != data["password2"]:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('signup')

        if User.objects.filter(username=data["username"]).exists():
            messages.error(request, "Ese usuario ya está registrado.")
            return redirect('signup')

        if User.objects.filter(email=data["email"]).exists():
            messages.error(request, "Ese correo ya está registrado.")
            return redirect('signup')

        # Crear usuario
        user = User.objects.create_user(
            username=data["username"],
            password=data["password1"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"]
        )

        # Actualizar perfil autogenerado
        profile = Profile.objects.get(user=user)
        profile.telefono = data["phone"]
        profile.colonia = data["neighborhood"]
        profile.rol = "CIUDADANO"
        profile.save()

        messages.success(request, "Cuenta creada correctamente. Ahora inicia sesión.")
        return redirect('login')

    return render(request, 'juarez_mueve/signup.html')


# ============================================================
#              DASHBOARD (ADMIN / COORDINADOR)
# ============================================================

def dashboard(request):

    # ============================================================
    #                    CREAR CONDUCTOR
    # ============================================================
    if request.method == "POST" and "add_conductor" in request.POST:
        form = CrearConductorForm(request.POST)

        if form.is_valid():
            nombre = form.cleaned_data["nombre"]
            apellido = form.cleaned_data["apellido"]
            correo = form.cleaned_data["correo"]
            contraseña = form.cleaned_data["contraseña"]
            rol = form.cleaned_data["rol"]

            # Crear usuario
            user = User.objects.create_user(
                username=correo,
                email=correo,
                password=contraseña,
                first_name=nombre,
                last_name=apellido
            )

            # Crear perfil
            Profile.objects.create(
                user=user,
                rol=rol
            )

            messages.success(request, "Conductor registrado correctamente.")
            return redirect("dashboard")

        else:
            messages.error(request, "Error al agregar el conductor.")
            print("Errores conductor:", form.errors)

    # ============================================================
    #                    CREAR CAMIÓN
    # ============================================================
    if request.method == "POST" and "add_camion" in request.POST:
        form = CrearCamionForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Camión registrado correctamente.")
            return redirect("dashboard")
        else:
            messages.error(request, "Error en el formulario del camión.")
            print("Errores camión:", form.errors)

    # ============================================================
    #                    DATOS PARA LA VISTA
    # ============================================================

    conductor_form = CrearConductorForm()
    camion_form = CrearCamionForm()

    empresa_actual = None
    if hasattr(request.user, "profile"):

        if request.user.profile.rol in ["COORDINADOR_TRANSPORTE", "COORDINADOR_BASURA"]:
            empresa_actual = request.user.profile.empresa

        elif request.user.profile.rol in ["APP_ADMIN", "EMPRESA_ADMIN"]:
            empresa_actual = None  # Ve todas las unidades

    # ================= Obtener unidades =====================
    if empresa_actual:
        unidades = Unidad.objects.filter(empresa=empresa_actual)
    else:
        unidades = Unidad.objects.all()

    total_unidades = unidades.count()
    transporte_activo = unidades.filter(tipo="transporte", activo=True).count()
    basura_activa = unidades.filter(tipo="basura", activo=True).count()

    context = {
        "empresa_actual": empresa_actual,
        "unidades": unidades,
        "total_unidades": total_unidades,
        "transporte_activo": transporte_activo,
        "basura_activa": basura_activa,
        "conductor_form": conductor_form,
        "camion_form": camion_form,
    }

    return render(request, "panel/dashboard.html", context)


# ============================================================
#                    PANEL DEL CONDUCTOR
# ============================================================

@login_required
def panel_conductor(request):
    profile = request.user.profile

    if profile.rol not in ["CONDUCTOR", "RECOLECTOR"]:
        return redirect("dashboard")

    ruta = getattr(profile, "ruta_asignada", None)

    try:
        unidad = Unidad.objects.get(conductor=request.user)
    except Unidad.DoesNotExist:
        unidad = None

    context = {
        "ruta": ruta,
        "unidad": unidad,
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
    }

    return render(request, "conductor/panel.html", context)

# ============================================================
#                      PERFIL DEL USUARIO
# ============================================================

@login_required
def perfil(request):
    profile = request.user.profile  # Tu modelo Profile

    if request.method == "POST":
        # Campos editables
        profile.telefono = request.POST.get("telefono")
        profile.colonia = request.POST.get("colonia")
        profile.direccion = request.POST.get("direccion")
        profile.save()

        messages.success(request, "Cambios guardados correctamente.")
        return redirect("perfil")

    return render(request, "juarez_mueve/perfil.html", {
        "profile": profile
    })