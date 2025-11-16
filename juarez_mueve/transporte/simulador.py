# transporte/simulador.py
import time
import random
from django.utils import timezone
from .models import Unidad, UbicacionTiempoReal, PuntoRuta

def mover_unidades(pausa=5):
    print("=== Simulador Juárez Mueve iniciado ===")

    while True:
        # ✅ Aquí estaba el problema: usar activo=True en lugar de estado="ACTIVO"
        unidades = Unidad.objects.filter(
            activo=True,
            ruta__isnull=False,
            tipo="transporte",
        )

        if not unidades.exists():
            print("[SIM] No hay unidades activas con ruta asignada.")
        else:
            for u in unidades:
                ruta = u.ruta
                puntos = list(ruta.puntos.all().order_by("orden"))

                if not puntos:
                    print(f"[SIM] Ruta '{ruta.nombre}' no tiene puntos, saltando unidad {u.identificador}.")
                    continue

                # Última ubicación registrada de esa unidad
                ultima = (
                    UbicacionTiempoReal.objects
                    .filter(unidad=u)
                    .order_by("-timestamp")
                    .first()
                )

                # Elegir siguiente punto en la ruta
                if ultima:
                    # Buscar en qué punto estaba y avanzar al siguiente
                    idx_actual = None
                    for i, p in enumerate(puntos):
                        if (
                            abs(p.latitud - ultima.latitud) < 0.0001
                            and abs(p.longitud - ultima.longitud) < 0.0001
                        ):
                            idx_actual = i
                            break

                    if idx_actual is None:
                        # Si no coincide con ningún punto, iniciar desde uno aleatorio
                        siguiente = random.choice(puntos)
                    else:
                        siguiente = puntos[(idx_actual + 5) % len(puntos)]
                else:
                    # Primera vez: arranca en el primer punto
                    siguiente = puntos[0]

                UbicacionTiempoReal.objects.create(
                    unidad=u,
                    latitud=siguiente.latitud,
                    longitud=siguiente.longitud,
                )

                print(
                    f"[{timezone.now().time()}] Unidad {u.identificador} "
                    f"movida a ({siguiente.latitud}, {siguiente.longitud})"
                )

        # Espera antes del siguiente "tick"
        time.sleep(pausa)
