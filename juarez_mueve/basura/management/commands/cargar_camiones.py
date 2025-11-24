from django.core.management.base import BaseCommand
from basura.models import UnidadRecoleccion
import random
import string

class Command(BaseCommand):
    help = "Carga camiones de basura con códigos únicos"

    def generar_codigo_unico(self):
        """Genera un código único tipo CAM-ABC123."""
        while True:
            letras = ''.join(random.choices(string.ascii_uppercase, k=3))
            numeros = ''.join(random.choices(string.digits, k=3))
            codigo = f"CAM-{letras}{numeros}"
            if not UnidadRecoleccion.objects.filter(codigo_unidad=codigo).exists():
                return codigo

    def handle(self, *args, **options):
        total = 50  # <- puedes cambiar el número aquí

        for i in range(1, total + 1):
            codigo = self.generar_codigo_unico()

            UnidadRecoleccion.objects.create(
                nombre=f"Camión {i}",
                codigo_unidad=codigo,
                latitud=round(31.7 + random.uniform(-0.05, 0.05), 6),
                longitud=round(-106.4 + random.uniform(-0.05, 0.05), 6),
                estado="ACTIVO"
            )

        self.stdout.write(
            self.style.SUCCESS(f"{total} camiones cargados con códigos únicos")
        )
