from django.shortcuts import render

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
