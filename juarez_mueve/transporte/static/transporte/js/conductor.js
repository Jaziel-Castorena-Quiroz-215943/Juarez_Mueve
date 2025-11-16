let map;
let rutaPolyline = null;
let watchId = null;


function initMap() {
    const mapDiv = document.getElementById("map");

    map = new google.maps.Map(mapDiv, {
        center: { lat: 31.6904, lng: -106.4245 },
        zoom: 13,
        mapId: "DEMO_MAP"
    });

    const rutaId = mapDiv.dataset.rutaId;
    if (rutaId) {
        cargarRuta(rutaId);
    }
}


// ==========================
// CARGAR RUTA
// ==========================
function cargarRuta(rutaId) {
    fetch(`/api/ruta/${rutaId}/`)
        .then(res => res.json())
        .then(data => {
            const puntos = data.puntos.map(p => ({ lat: p.latitud, lng: p.longitud }));

            rutaPolyline = new google.maps.Polyline({
                path: puntos,
                strokeColor: data.color,
                strokeWeight: 4,
                map: map
            });

            map.setCenter(puntos[0]);
        });
}


// ==========================
// ACTIVAR GPS
// ==========================
document.getElementById("btn-activar-gps")?.addEventListener("click", () => {
    if (!navigator.geolocation) {
        alert("Tu navegador no soporta GPS.");
        return;
    }

    watchId = navigator.geolocation.watchPosition(
        async (pos) => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;

            const unidadId = document.getElementById("map").dataset.unidadId;

            await fetch(`/api/unidad/${unidadId}/ubicacion/`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
                body: JSON.stringify({ lat, lng })
            });

            console.log("Ubicación actualizada:", lat, lng);
        },
        (err) => console.error(err),
        { enableHighAccuracy: true, maximumAge: 0 }
    );
});


// ==========================
// CSRF Helper
// ==========================
function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}
