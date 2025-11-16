from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from django.db.models import Q

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
    if request.method == "POST":
        user_input = request.POST.get("email")  
        password = request.POST.get("password")

        # Primero intentamos buscar por username o email
        try:
            user = User.objects.get(Q(username=user_input) | Q(email=user_input))
            username = user.username
        except User.DoesNotExist:
            messages.error(request, "Usuario o contraseña incorrectos")
            return render(request, "login.html")

        # Autenticamos usando el username real
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")  # Cambia por la ruta que va después del login
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "juarez_mueve/login.html")


def signup(request):
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
