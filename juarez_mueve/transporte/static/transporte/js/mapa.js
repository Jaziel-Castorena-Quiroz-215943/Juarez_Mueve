// Inicialización Leaflet (ya lo tienes)
const map = L.map('map').setView([31.6904, -106.4245], 13);
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap &copy; CARTO'
}).addTo(map);

// Contenedor de marcadores por identificador
const marcadores = {}; // {'Bus 15': L.marker(...) }

// Colores / iconos para tipos
function styleForTipo(tipo){
    if(tipo === 'transporte') return { color: '#16a34a', radius: 9 }; // verde
    if(tipo === 'basura') return { color: '#f59e0b', radius: 9 }; // amarillo
    return { color: '#6b7280', radius: 8 };
}

// Crear o actualizar marcador
function upsertMarker(unidad){
    if(!unidad.ultima_ubicacion) return;
    const id = unidad.identificador || unidad.id;
    const lat = unidad.ultima_ubicacion.latitud;
    const lng = unidad.ultima_ubicacion.longitud;
    const tipo = unidad.tipo;
    const style = styleForTipo(tipo);

    if(marcadores[id]){
        // mover con animación sencilla (no nativa en circleMarker)
        marcadores[id].setLatLng([lat, lng]);
    } else {
        const marker = L.circleMarker([lat, lng], {
    radius: style.radius,
    fillColor: style.color,
    color: "#333",
    weight: 1,
    fillOpacity: 1
}).addTo(map);

// Guardamos la unidad dentro del marcador
marker.unidadData = unidad;

// Evento para actualizar panel
marker.on('click', function() {
    actualizarPanel(this.unidadData);
});

marcadores[id] = marker;

    }
}

// Fetch a la API y actualizar todos los marcadores
async function fetchAndUpdate(){
    try {
        const res = await fetch('/api/unidades/');
        if(!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();

        // marcar existentes como vistos
        const vistos = new Set();

        data.forEach(u => {
            upsertMarker(u);
            const id = u.identificador || u.id;
            vistos.add(id);
        });

        // opcional: remover marcadores que ya no vienen en la API
        Object.keys(marcadores).forEach(id => {
            if(!vistos.has(id)){
                map.removeLayer(marcadores[id]);
                delete marcadores[id];
            }
        });

    } catch(err){
        console.error('Error fetching unidades:', err);
    }
}

// Primer fetch y luego poll cada 5s
fetchAndUpdate();
setInterval(fetchAndUpdate, 5000);

function actualizarPanel(unidad) {
    const panel = document.getElementById('panel-detalles');
    if (!panel) return;

    const ultima = unidad.ultima_ubicacion ? `
        <p class="text-sm text-gray-500">Última actualización: ${unidad.ultima_ubicacion.timestamp}</p>
        <p class="mt-1 text-sm"><strong>Lat:</strong> ${unidad.ultima_ubicacion.latitud.toFixed(5)}</p>
        <p class="text-sm"><strong>Lng:</strong> ${unidad.ultima_ubicacion.longitud.toFixed(5)}</p>
    ` : `<p class="text-sm text-red-600">Sin ubicación registrada</p>`;

    panel.innerHTML = `
        <h3 class="font-semibold text-lg mb-1">${unidad.identificador}</h3>
        <p class="text-sm text-gray-600 capitalize">Tipo: ${unidad.tipo}</p>
        ${unidad.ruta ? `<p class="text-sm">Ruta asignada: ${unidad.ruta}</p>` : ''}
        <hr class="my-2">
        ${ultima}
        <button class="mt-4 px-4 py-2 bg-[#3AB54A] text-white rounded-lg w-full">
            Ver Detalles
        </button>
    `;
}
