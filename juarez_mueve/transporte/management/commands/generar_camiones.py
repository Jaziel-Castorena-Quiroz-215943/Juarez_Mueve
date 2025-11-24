from django.core.management.base import BaseCommand
from django.db import transaction
from transporte.models import Ruta, TransporteUnidad
import random

class Command(BaseCommand):
    help = "Genera camiones de transporte masivamente asignados a las rutas existentes"

    PREFIJOS = [
        "INDIOBUS",
        "BRAVOBUS",
        "JuarezZaragoza",
        "Express1A"
    ]

    def generar_identificador(self):
        prefijo = random.choice(self.PREFIJOS)
        numero = random.randint(100, 999)
        return f"{prefijo}-{numero}"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        rutas = list(Ruta.objects.all())

        if not rutas:
            self.stdout.write(self.style.ERROR("No existen rutas. Genera rutas primero."))
            return

        self.stdout.write(self.style.WARNING("Eliminando unidades actuales..."))
        TransporteUnidad.objects.all().delete()

        cantidad = 50
        self.stdout.write(self.style.WARNING(f"Generando {cantidad} unidades..."))

        for _ in range(cantidad):
            ruta = random.choice(rutas)

            # Punto inicial
            if ruta.puntos.exists():
                p = ruta.puntos.order_by("?").first()
                lat, lng = p.latitud, p.longitud
            else:
                # fallback si no tiene puntos
                lat = 31.69 + random.uniform(-0.03, 0.03)
                lng = -106.42 + random.uniform(-0.03, 0.03)

            identificador = self.generar_identificador()

            TransporteUnidad.objects.create(
                identificador=identificador,
                nombre=identificador,
                ruta=ruta,
                latitud=lat,
                longitud=lng,
                tipo="transporte"
            )

        self.stdout.write(self.style.SUCCESS("✔ Se generaron camiones de transporte correctamente."))
