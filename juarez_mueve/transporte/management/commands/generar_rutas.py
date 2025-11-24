from django.core.management.base import BaseCommand
from django.db import transaction
from transporte.models import Ruta, PuntoRuta
import random

class Command(BaseCommand):
    help = "Elimina todas las rutas y genera 20 nuevas con 5 puntos por ruta agrupados por zonas"

    ZONAS = {
        "NORTE":  { "lat": 31.75, "lng": -106.40 },
        "SUR":    { "lat": 31.60, "lng": -106.40 },
        "CENTRO": { "lat": 31.67, "lng": -106.42 },
        "ORIENTE":{ "lat": 31.68, "lng": -106.35 },
        "PONIENTE":{"lat": 31.68, "lng": -106.49 },
    }

    NOMBRES_BASE = [
        "Express", "Rápida", "Conexión", "Urbana",
        "Indiobus", "BravoBus", "Linea", "Circuito",
        "Ronda", "Ruta"
    ]

    COLORES = [
        "#FF5733", "#33FF57", "#3357FF", "#FBC531",
        "#E84118", "#9C88FF", "#00A8FF", "#4CD137",
        "#487EB0", "#8C7AE6"
    ]

    def generar_nombre(self):
        base = random.choice(self.NOMBRES_BASE)
        num = random.randint(1, 99)
        return f"{base} {num}"

    def generar_puntos(self, base_lat, base_lng):
        puntos = []
        for _ in range(5):
            lat = base_lat + random.uniform(-0.02, 0.02)
            lng = base_lng + random.uniform(-0.02, 0.02)
            puntos.append((lat, lng))
        return puntos

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Eliminando rutas actuales..."))
        Ruta.objects.all().delete()
        PuntoRuta.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Rutas eliminadas."))

        self.stdout.write(self.style.WARNING("Generando nuevas rutas..."))

        for i in range(20):
            zona = random.choice(list(self.ZONAS.keys()))
            centro = self.ZONAS[zona]

            nombre = self.generar_nombre()
            color = random.choice(self.COLORES)
            puntos = self.generar_puntos(centro["lat"], centro["lng"])

            ruta = Ruta.objects.create(
                nombre=f"{nombre} - {zona}",
                color=color,
                origen=f"Zona {zona}",
                destino=f"Zona {zona}"
            )

            for idx, (lat, lng) in enumerate(puntos, start=1):
                PuntoRuta.objects.create(
                    ruta=ruta,
                    orden=idx,
                    latitud=lat,
                    longitud=lng
                )

        self.stdout.write(self.style.SUCCESS("✔ Se crearon 20 rutas nuevas correctamente."))
