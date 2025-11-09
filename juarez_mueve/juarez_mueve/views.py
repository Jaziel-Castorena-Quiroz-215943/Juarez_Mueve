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
        user_input = request.POST.get("email")  # campo del formulario
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
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        phone = request.POST.get("phone")
        neighborhood = request.POST.get("neighborhood")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Validaciones básicas
        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ese usuario ya está registrado.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Ese correo ya está registrado.")
            return redirect('signup')

        # Crear usuario
        user = User.objects.create_user(
            username=username,
            password=password1,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        # Guardar perfil
        profile = Profile.objects.get(user=user)
        profile.phone = phone
        profile.neighborhood = neighborhood
        profile.save()

        messages.success(request, "Cuenta creada correctamente. Ahora inicia sesión.")
        return redirect('login')

    return render(request, 'juarez_mueve/signup.html')
