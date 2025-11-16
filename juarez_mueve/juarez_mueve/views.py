from django.shortcuts import render, redirect
# 🚨 Eliminar las importaciones manuales: from django.contrib.auth import authenticate, login
# 🚨 Eliminar las importaciones manuales: from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from django.db.models import Q
from django.contrib.auth.models import User # Mantener User para signup

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

def login_view(request):
    # 🚨 CÓDIGO ELIMINADO: Eliminamos todo el bloque 'if request.method == "POST":'
    # Esta lógica es redundante y conflictiva, ya que allauth debe manejar el POST.
    
    # 🚨 IMPORTANTE: Asegúrate de que esta plantilla sea la que allauth usa
    # para sus errores (colocando una copia en /templates/account/login.html)
    return render(request, "juarez_mueve/login.html")


def signup(request):
    # ... (El código de signup queda sin cambios, ya que está bien)
    if request.method == "POST":
        # Datos
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

        # Crear perfil
        profile = Profile.objects.get(user=user)
        profile.telefono = data["phone"]
        profile.colonia = data["neighborhood"]
        profile.rol = "CIUDADANO"  # 🔒 seguridad
        profile.save()

        messages.success(request, "Cuenta creada correctamente. Ahora inicia sesión.")
        return redirect('login')

    return render(request, 'juarez_mueve/signup.html')