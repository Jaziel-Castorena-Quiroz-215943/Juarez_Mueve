// static/transporte/js/mapa.js

// 1. Crear mapa centrado en Ciudad Juárez
const map = L.map('map').setView([31.6911, -106.4245], 12);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// 2. Iconos para transporte y basura
const iconTransporte = L.icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/61/61225.png',
    iconSize: [26, 26],
    iconAnchor: [13, 26]
});

const iconBasura = L.icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/3500/3500833.png',
    iconSize: [26, 26],
    iconAnchor: [13, 26]
});

// 3. Estado de marcadores en memoria
let unidadesMarkers = []; // { marker, tipo, data }

// 4. Cargar datos desde la API
function cargarUnidades() {
    fetch('/transporte/api/unidades/')
        .then(res => res.json())
        .then(data => {
            limpiarMarcadores();

            data.forEach(u => {
                if (!u.ultima_ubicacion) return; // si no hay posición, no la pintamos

                const lat = u.ultima_ubicacion.latitud;
                const lng = u.ultima_ubicacion.longitud;
                const tipo = u.tipo; // 'transporte' o 'basura'

                const icon = tipo === 'basura' ? iconBasura : iconTransporte;

                const marker = L.marker([lat, lng], { icon }).addTo(map);

                marker.on('click', () => mostrarInfoUnidad(u));

                // Guardamos referencia
                unidadesMarkers.push({ marker, tipo, data: u });
            });

            actualizarEstadisticas();
        })
        .catch(err => {
            console.error('Error cargando unidades:', err);
        });
}

// 5. Limpiar marcadores actuales
function limpiarMarcadores() {
    unidadesMarkers.forEach(obj => {
        map.removeLayer(obj.marker);
    });
    unidadesMarkers = [];
}

// 6. Mostrar información en el panel derecho
function mostrarInfoUnidad(u) {
    const panel = document.getElementById('panel-detalles');

    const tipoLabel = u.tipo === 'basura'
        ? 'Recolección de basura'
        : 'Transporte público';

    const rutaTexto = u.ruta_nombre ? u.ruta_nombre : 'Sin ruta asignada';

    const fecha = u.ultima_ubicacion
        ? new Date(u.ultima_ubicacion.timestamp).toLocaleString()
        : 'Sin datos';

    panel.innerHTML = `
        <h3 class="font-semibold text-lg mb-2">Unidad ${u.identificador}</h3>
        <p class="text-sm text-gray-600 mb-1"><strong>Tipo:</strong> ${tipoLabel}</p>
        <p class="text-sm text-gray-600 mb-1"><strong>Ruta:</strong> ${rutaTexto}</p>
        <p class="text-xs text-gray-500 mt-2">
            Última actualización: ${fecha}
        </p>
    `;
}

// 7. Actualizar estadísticas de la derecha
function actualizarEstadisticas() {
    const transporteActivos = unidadesMarkers.filter(m => m.tipo === 'transporte').length;
    const basuraActiva = unidadesMarkers.filter(m => m.tipo === 'basura').length;

    const spanTransporte = document.getElementById('stat-transporte');
    const spanBasura = document.getElementById('stat-basura');

    if (spanTransporte) spanTransporte.textContent = transporteActivos;
    if (spanBasura) spanBasura.textContent = basuraActiva;
}

// 8. Filtros de botones
function mostrarTodos() {
    unidadesMarkers.forEach(obj => {
        if (!map.hasLayer(obj.marker)) obj.marker.addTo(map);
    });
    actualizarEstadisticas();
}

function filtrarPorTipo(tipoBuscado) {
    unidadesMarkers.forEach(obj => {
        if (obj.tipo === tipoBuscado) {
            if (!map.hasLayer(obj.marker)) obj.marker.addTo(map);
        } else {
            if (map.hasLayer(obj.marker)) map.removeLayer(obj.marker);
        }
    });
    actualizarEstadisticas();
}

// 9. Búsqueda por identificador o ruta
function buscarUnidad() {
    const input = document.getElementById('input-buscar');
    if (!input) return;

    const q = input.value.trim().toLowerCase();
    if (!q) return;

    let encontrado = null;

    for (const obj of unidadesMarkers) {
        const id = (obj.data.identificador || '').toLowerCase();
        const ruta = (obj.data.ruta_nombre || '').toLowerCase();
        if (id.includes(q) || ruta.includes(q)) {
            encontrado = obj;
            break;
        }
    }

    if (encontrado) {
        const latLng = encontrado.marker.getLatLng();
        map.setView(latLng, 15);
        mostrarInfoUnidad(encontrado.data);
    }
}

let rutasLayer = L.layerGroup().addTo(map);

function cargarRutas() {
    fetch('/transporte/api/rutas_mapa/')
        .then(res => res.json())
        .then(data => {
            rutasLayer.clearLayers();

            data.forEach(ruta => {
                if (!ruta.puntos || ruta.puntos.length === 0) return;

                // Ordenamos puntos por "orden" por si acaso
                const puntosOrdenados = ruta.puntos.sort(
                    (a, b) => a.orden - b.orden
                );

                const coords = puntosOrdenados.map(p => [p.latitud, p.longitud]);

                // Puedes cambiar color según tipo de ruta cuando tengas ese campo
                const polyline = L.polyline(coords, {
                    color: '#0077B6', // azul tipo SIT
                    weight: 5,
                    opacity: 0.8
                }).addTo(rutasLayer);

                // Tooltip con el nombre de la ruta
                polyline.bindTooltip(ruta.nombre, { sticky: true });
            });
        })
        .catch(err => {
            console.error("Error cargando rutas:", err);
        });
}

// 10. Mi ubicación
function irAMiUbicacion() {
    if (!navigator.geolocation) {
        alert('Tu navegador no soporta geolocalización.');
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const { latitude, longitude } = pos.coords;
            map.setView([latitude, longitude], 14);
            L.circle([latitude, longitude], {
                radius: 80,
                color: '#3AB54A',
                fillColor: '#3AB54A',
                fillOpacity: 0.3
            }).addTo(map);
        },
        () => {
            alert('No se pudo obtener tu ubicación.');
        }
    );
}

function cargarRutas() {
    fetch("/transporte/api/rutas/")
        .then(res => res.json())
        .then(data => {
            data.rutas.forEach(r => {
                const puntos = r.puntos.map(p => [p.latitud, p.longitud]);

                L.polyline(puntos, {
                    color: "#1d4ed8",
                    weight: 4,
                    opacity: 0.7
                }).addTo(map);
            });
        })
        .catch(err => console.error("Error rutas:", err));
}

// 11. Enlazar eventos a los botones
document.addEventListener('DOMContentLoaded', () => {
    const btnTodos = document.getElementById('btn-todos');
    const btnTransporte = document.getElementById('btn-transporte');
    const btnBasura = document.getElementById('btn-basura');
    const btnBuscar = document.getElementById('btn-buscar');
    const btnActualizar = document.getElementById('btn-actualizar');
    const btnUbicacion = document.getElementById('btn-ubicacion');

    if (btnTodos) btnTodos.addEventListener('click', mostrarTodos);
    if (btnTransporte) btnTransporte.addEventListener('click', () => filtrarPorTipo('transporte'));
    if (btnBasura) btnBasura.addEventListener('click', () => filtrarPorTipo('basura'));
    if (btnBuscar) btnBuscar.addEventListener('click', buscarUnidad);
    if (btnActualizar) btnActualizar.addEventListener('click', cargarUnidades);
    if (btnUbicacion) btnUbicacion.addEventListener('click', irAMiUbicacion);

    // Cargar la primera vez
    cargarUnidades();
    cargarRutas();
});

