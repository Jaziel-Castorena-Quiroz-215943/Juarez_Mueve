from django.core.management.base import BaseCommand
from transporte.models import Ruta, PuntoRuta, Unidad, UbicacionTiempoReal
import random

class Command(BaseCommand):
    help = "Genera rutas y camiones de transporte de manera aleatoria"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Eliminando rutas antiguas..."))
        PuntoRuta.objects.all().delete()
        Ruta.objects.all().delete()

        # 20 rutas nuevas
        TOTAL_RUTAS = 20
        TOTAL_CAMIONES = 50

        nombres_posibles = [
            "Independencia", "Tecnológico", "Panamericano", "Zaragoza", "Aztecas",
            "Parajes", "Misiones", "Centro", "Durango", "Morelos",
            "Valle Dorado", "Henequén", "Riveras", "Torres", "Senderos"
        ]

        zonas = {
            "Norte": (31.75, 31.80, -106.50, -106.40),
            "Centro": (31.68, 31.70, -106.45, -106.38),
            "Sur": (31.55, 31.62, -106.50, -106.35),
            "Poniente": (31.67, 31.74, -106.55, -106.50),
            "Valle": (31.60, 31.67, -106.30, -106.20),
        }

        def coord_aleatoria():
            zona = random.choice(list(zonas.keys()))
            lat_min, lat_max, lng_min, lng_max = zonas[zona]
            return round(random.uniform(lat_min, lat_max), 6), round(random.uniform(lng_min, lng_max), 6)

        rutas_creadas = []

        self.stdout.write(self.style.WARNING("Creando 20 rutas nuevas..."))

        for i in range(TOTAL_RUTAS):
            nombre = random.choice(nombres_posibles) + f" #{i+1}"
            ruta = Ruta.objects.create(nombre=nombre)

            # Crear 5 puntos
            for orden in range(1, 6):
                lat, lng = coord_aleatoria()
                PuntoRuta.objects.create(
                    ruta=ruta,
                    orden=orden,
                    latitud=lat,
                    longitud=lng
                )

            rutas_creadas.append(ruta)

        self.stdout.write(self.style.SUCCESS("Rutas creadas correctamente."))

        # Crear camiones
        identificadores_base = ["INDIOBUS", "BRAVOBUS", "EXPRESS1A", "JUAREZZARAGOZA", "JUAREZBUS"]

        self.stdout.write(self.style.WARNING("Creando camiones de transporte..."))

        # Borramos unidades antiguas de transporte
        Unidad.objects.filter(tipo="transporte").delete()

        for i in range(TOTAL_CAMIONES):
            base = random.choice(identificadores_base)
            identificador = f"{base}-{random.randint(100,999)}"

            ruta_asignada = random.choice(rutas_creadas)

            unidad = Unidad.objects.create(
                identificador=identificador,
                tipo="transporte",
                ruta=ruta_asignada,
                activo=True
            )

            # Ubicación inicial (primer punto de la ruta)
            primer_punto = ruta_asignada.puntos.first()
            UbicacionTiempoReal.objects.create(
                unidad=unidad,
                latitud=primer_punto.latitud,
                longitud=primer_punto.longitud
            )

        self.stdout.write(self.style.SUCCESS("Camiones creados y ubicaciones asignadas."))

        self.stdout.write(self.style.SUCCESS("Proceso completado con éxito."))
