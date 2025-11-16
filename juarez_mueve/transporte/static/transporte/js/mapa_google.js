let map;
let markers = [];
let filtroActual = "todos";

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 31.6904, lng: -106.4245 },
        zoom: 12,
        disableDefaultUI: false,
        mapId: "DEMO_MAP_ID"
    });

    cargarUnidades();
}

function cargarUnidades() {
    let url = "/transporte/api/unidades/";

    fetch(url)
        .then(r => r.json())
        .then(data => {
            limpiarMarcadores();

            data.forEach(u => {
                if (!u.ultima_ubicacion) return;

                let pos = {
                    lat: u.ultima_ubicacion.latitud,
                    lng: u.ultima_ubicacion.longitud
                };

                let iconUrl =
                    u.tipo === "basura"
                        ? "https://cdn-icons-png.flaticon.com/512/3500/3500833.png"
                        : "https://cdn-icons-png.flaticon.com/512/61/61225.png";

                let marker = new google.maps.Marker({
                    position: pos,
                    map: map,
                    icon: {
                        url: iconUrl,
                        scaledSize: new google.maps.Size(32, 32)
                    }
                });

                marker.addListener("click", () => mostrarInfo(u));
                markers.push({ marker, tipo: u.tipo, data: u });
            });

            actualizarStats();
        });
}

function limpiarMarcadores() {
    markers.forEach(m => m.marker.setMap(null));
    markers = [];
}

function mostrarInfo(u) {
    const panel = document.getElementById("panel-detalles");

    panel.innerHTML = `
        <h3 class="font-semibold text-lg mb-2">Unidad ${u.identificador}</h3>
        <p><strong>Tipo:</strong> ${u.tipo}</p>
        <p><strong>Ruta:</strong> ${u.ruta_nombre || "No asignada"}</p>
        <p class="text-xs text-gray-500 mt-2">
            Última actualización: ${new Date(u.ultima_ubicacion.timestamp).toLocaleString()}
        </p>
    `;
}

function actualizarStats() {
    let transporte = markers.filter(m => m.tipo === "transporte").length;
    let basura = markers.filter(m => m.tipo === "basura").length;

    document.getElementById("stat-transporte").textContent = transporte;
    document.getElementById("stat-basura").textContent = basura;
}

// Inicializar cuando cargue el script
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(initMap, 300);
});
