import requests
from django.conf import settings

def obtener_puntos_ruta(origen, destino):
    """
    Llama a Google Directions API y devuelve una lista de puntos (lat, lng)
    para almacenar en PuntoRuta.
    """
    api_key = settings.GOOGLE_MAPS_API_KEY

    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": origen,
        "destination": destino,
        "mode": "driving",
        "key": api_key
    }

    r = requests.get(url, params=params)
    data = r.json()

    if data["status"] != "OK":
        print("Error Directions:", data.get("status"), data.get("error_message"))
        return []

    puntos = []

    route = data["routes"][0]
    legs = route["legs"]

    for leg in legs:
        for step in leg["steps"]:
            start = step["start_location"]
            end = step["end_location"]

            puntos.append((start["lat"], start["lng"]))
            puntos.append((end["lat"], end["lng"]))

    # Eliminar duplicados manteniendo orden
    final = []
    for p in puntos:
        if p not in final:
            final.append(p)

    return final
