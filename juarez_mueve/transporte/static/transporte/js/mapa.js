// transporte/static/transporte/js/mapa.js

let map;
let userMarker = null;
let infoWindow = null;

// Rutas
let rutasData = [];
let rutasPolylines = [];

// Unidades
let unidadMarkers = {};      // id -> marker
let transporteMarkers = [];  // solo marcadores de transporte
let basuraMarkers = [];      // solo marcadores de basura

// Filtros
let currentTipoFiltro = "todos"; // "todos" | "transporte" | "basura"

// Auto-actualización
let autoUpdateTimer = null;
const AUTO_UPDATE_MS = 5000;

// Posición por defecto (Ciudad Juárez)
let userPosition = { lat: 31.6904, lng: -106.4245 };

function initMap() {
    const mapDiv = document.getElementById("map");
    if (!mapDiv) {
        console.error("No se encontró el div#map");
        return;
    }

    const apiUnidadesUrl = mapDiv.dataset.apiUnidadesUrl;
    const apiRutasUrl = mapDiv.dataset.apiRutasUrl;

    if (!apiUnidadesUrl || !apiRutasUrl) {
        console.error("Faltan data-api-unidades-url o data-api-rutas-url en el div#map");
        return;
    }

    // Crear mapa
    map = new google.maps.Map(mapDiv, {
        center: userPosition,
        zoom: 12,
    });

    infoWindow = new google.maps.InfoWindow();

    // Intentar obtener ubicación del usuario
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                userPosition = {
                    lat: pos.coords.latitude,
                    lng: pos.coords.longitude,
                };
                map.setCenter(userPosition);
                map.setZoom(13);

                if (userMarker) userMarker.setMap(null);
                userMarker = new google.maps.Marker({
                    position: userPosition,
                    map: map,
                    title: "Tu ubicación",
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 6,
                        fillColor: "#3AB54A",
                        fillOpacity: 1,
                        strokeWeight: 2,
                        strokeColor: "#ffffff",
                    },
                });
            },
            (err) => {
                console.warn("No se pudo obtener la ubicación del usuario:", err);
            }
        );
    }

    // Cargar rutas y poblar select
    fetch(apiRutasUrl)
        .then((res) => res.json())
        .then((data) => {
            rutasData = data.rutas || [];
            poblarSelectRutas(rutasData);
        })
        .catch((err) => {
            console.error("Error al cargar rutas:", err);
        });

    // Configurar botones
    setupButtons();

    // Primera carga de unidades y arrancar auto-actualización
    actualizarUnidades();
    autoUpdateTimer = setInterval(actualizarUnidades, AUTO_UPDATE_MS);
}

/* -------------------- RUTAS -------------------- */

function poblarSelectRutas(rutas) {
    const select = document.getElementById("select-rutas");
    if (!select) return;

    select.innerHTML = "";

    if (!rutas.length) {
        const opt = document.createElement("option");
        opt.textContent = "No hay rutas registradas";
        opt.disabled = true;
        select.appendChild(opt);
        return;
    }

    rutas.forEach((ruta) => {
        const opt = document.createElement("option");
        opt.value = ruta.id; // usaremos el id para filtrar
        opt.textContent = ruta.nombre;
        select.appendChild(opt);
    });
}

function obtenerRutasSeleccionadas() {
    const select = document.getElementById("select-rutas");
    if (!select) return [];

    const selected = [];
    for (const option of select.options) {
        if (option.selected && option.value) {
            selected.push(parseInt(option.value, 10));
        }
    }
    return selected;
}

function limpiarPolylines() {
    rutasPolylines.forEach((r) => r.setMap(null));
    rutasPolylines = [];
}

function dibujarRuta(ruta) {
    if (!ruta.puntos || ruta.puntos.length === 0) {
        console.warn(`Ruta "${ruta.nombre}" no tiene puntos.`);
        return;
    }

    const path = ruta.puntos.map((p) => ({ lat: p.lat, lng: p.lng }));

    const poly = new google.maps.Polyline({
        path,
        geodesic: true,
        strokeColor: ruta.color || "#2563eb",
        strokeOpacity: 0.9,
        strokeWeight: 4,
        map,
    });

    rutasPolylines.push(poly);

    // Ajustar el mapa para que se vea la ruta
    const bounds = new google.maps.LatLngBounds();
    path.forEach((pt) => bounds.extend(pt));
    map.fitBounds(bounds);
}

function dibujarRutasSeleccionadas() {
    limpiarPolylines();
    const rutaIds = obtenerRutasSeleccionadas();
    if (!rutaIds.length) return;

    rutasData
        .filter((r) => rutaIds.includes(r.id))
        .forEach((ruta) => {
            dibujarRuta(ruta);
        });
}

/* -------------------- UNIDADES (API) -------------------- */

function actualizarUnidades() {
    const mapDiv = document.getElementById("map");
    if (!mapDiv) return;
    const apiUrl = mapDiv.dataset.apiUnidadesUrl;
    if (!apiUrl) return;

    fetch(apiUrl)
        .then((res) => {
            if (!res.ok) throw new Error("Respuesta no OK de api/unidades");
            return res.json();
        })
        .then((data) => {
            procesarUnidadesDesdeApi(data);
        })
        .catch((err) => {
            console.error("Error actualizando unidades:", err);
        });
}

function procesarUnidadesDesdeApi(data) {
    const transportes = data.transportes || [];
    const basura = data.basura || [];

    const vistosIds = new Set();

    // TRANSPORTE
    transportes.forEach((u) => {
        if (!u.id || u.latitud == null || u.longitud == null) return;

        const id = u.id;
        const pos = new google.maps.LatLng(u.latitud, u.longitud);
        vistosIds.add(id);

        let marker = unidadMarkers[id];

        if (!marker) {
            // Crear nuevo marcador
            marker = new google.maps.Marker({
                position: pos,
                map: map,
                title: u.nombre || u.identificador || "Unidad de transporte",
                icon: {
                    url: "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
                },
            });

            marker._tipo = "transporte";
            marker._rutaId = u.ruta || null;
            marker._datos = u;

            marker.addListener("click", () => {
                mostrarInfoUnidad(u, "transporte", marker);
            });

            unidadMarkers[id] = marker;
        } else {
            // Actualizar datos y posición con animación
            marker._rutaId = u.ruta || marker._rutaId || null;
            marker._datos = u;
            moverAnimado(marker, pos);
        }
    });

    // BASURA
    basura.forEach((b) => {
        if (!b.id || b.latitud == null || b.longitud == null) return;

        const id = b.id;
        const pos = new google.maps.LatLng(b.latitud, b.longitud);
        vistosIds.add(id);

        let marker = unidadMarkers[id];

        if (!marker) {
            // Crear nuevo marcador
            marker = new google.maps.Marker({
                position: pos,
                map: map,
                title: b.nombre || b.codigo_unidad || "Unidad de basura",
                icon: {
                    url: "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
                },
            });

            marker._tipo = "basura";
            marker._rutaId = null;
            marker._datos = b;

            marker.addListener("click", () => {
                mostrarInfoUnidad(b, "basura", marker);
            });

            unidadMarkers[id] = marker;
        } else {
            marker._datos = b;
            moverAnimado(marker, pos);
        }
    });

    // Eliminar marcadores que ya no están en la API
    Object.keys(unidadMarkers).forEach((key) => {
        const id = parseInt(key, 10);
        if (!vistosIds.has(id)) {
            unidadMarkers[id].setMap(null);
            delete unidadMarkers[id];
        }
    });

    // Reconstruir arreglos de transporte/basura para estadísticas
    transporteMarkers = [];
    basuraMarkers = [];
    Object.values(unidadMarkers).forEach((m) => {
        if (m._tipo === "transporte") transporteMarkers.push(m);
        if (m._tipo === "basura") basuraMarkers.push(m);
    });

    aplicarFiltros();
    actualizarPanelEstadisticas();
}

/* -------------------- FILTROS Y BÚSQUEDA -------------------- */

function aplicarFiltros() {
    const rutaIds = obtenerRutasSeleccionadas();
    const hayRutas = rutaIds.length > 0;

    const inputBuscar = document.getElementById("input-buscar");
    const query = inputBuscar ? inputBuscar.value.toLowerCase().trim() : "";

    Object.values(unidadMarkers).forEach((marker) => {
        let visible = true;

        // Filtrar por tipo
        if (currentTipoFiltro === "transporte" && marker._tipo !== "transporte") {
            visible = false;
        }
        if (currentTipoFiltro === "basura" && marker._tipo !== "basura") {
            visible = false;
        }

        // Filtrar por rutas (solo transporte)
        if (visible && marker._tipo === "transporte" && hayRutas) {
            if (!marker._rutaId || !rutaIds.includes(marker._rutaId)) {
                visible = false;
            }
        }

        // Filtrar por texto
        if (visible && query) {
            const d = marker._datos || {};
            const texto =
                (d.nombre || d.identificador || d.codigo || d.codigo_unidad || "") +
                " " +
                (d.ruta_nombre || d.zona || "");
            if (!texto.toLowerCase().includes(query)) {
                visible = false;
            }
        }

        marker.setVisible(visible);
    });
}

function actualizarPanelEstadisticas() {
    const statTransporte = document.getElementById("stat-transporte");
    const statBasura = document.getElementById("stat-basura");

    if (statTransporte) statTransporte.textContent = transporteMarkers.length;
    if (statBasura) statBasura.textContent = basuraMarkers.length;
}

/* -------------------- ANIMACIÓN SUAVE -------------------- */

function moverAnimado(marker, destino) {
    const inicio = marker.getPosition();
    if (!inicio) {
        marker.setPosition(destino);
        return;
    }

    const pasos = 80;        // más pasos = más suave
    const duracion = 4000;   // ms
    const intervalo = duracion / pasos;

    let i = 0;

    const anim = setInterval(() => {
        i++;

        const lat = inicio.lat() + (destino.lat() - inicio.lat()) * (i / pasos);
        const lng = inicio.lng() + (destino.lng() - inicio.lng()) * (i / pasos);

        marker.setPosition(new google.maps.LatLng(lat, lng));

        if (i >= pasos) clearInterval(anim);
    }, intervalo);
}

/* -------------------- INFO EN PANEL Y INFOWINDOW -------------------- */

function mostrarInfoUnidad(datos, tipo, marker) {
    let contenido = "";

    if (tipo === "transporte") {
        contenido = `
            <div style="min-width:220px">
                <strong>${datos.nombre || datos.identificador || "Unidad de transporte"}</strong><br>
                Ruta: ${datos.ruta_nombre || datos.ruta || "-"}<br>
            </div>
        `;
    } else {
        contenido = `
            <div style="min-width:220px">
                <strong>${datos.nombre || "Unidad de basura"}</strong><br>
                Código: ${datos.codigo_unidad || datos.identificador || "-"}<br>
                Zona: ${datos.zona || "-"}<br>
                Estado: ${datos.estado || "-"}
            </div>
        `;
    }

    // InfoWindow en el mapa
    infoWindow.setContent(contenido);
    infoWindow.open(map, marker);

    // Panel lateral
    const panel = document.getElementById("panel-detalles");
    if (!panel) return;

    if (tipo === "transporte") {
        panel.innerHTML = `
            <h3 class="font-semibold text-lg mb-3">Información de la unidad</h3>
            <p class="text-sm text-gray-700 mb-1">
                <strong>Tipo:</strong> Transporte público
            </p>
            <p class="text-sm text-gray-700 mb-1">
                <strong>Nombre:</strong> ${datos.nombre || datos.identificador || "-"}
            </p>
            <p class="text-sm text-gray-700 mb-1">
                <strong>Ruta:</strong> ${datos.ruta_nombre || datos.ruta || "-"}
            </p>
            <hr class="my-3">
            <h4 class="font-semibold text-sm mb-2">Estadísticas en vivo</h4>
            <div class="space-y-1 text-sm">
                <div class="flex justify-between">
                    <span>Transporte activo</span>
                    <span class="font-bold text-green-600">${transporteMarkers.length}</span>
                </div>
                <div class="flex justify-between">
                    <span>Recolección activa</span>
                    <span class="font-bold text-yellow-600">${basuraMarkers.length}</span>
                </div>
            </div>
        `;
    } else {
        panel.innerHTML = `
            <h3 class="font-semibold text-lg mb-3">Información de la unidad</h3>
            <p class="text-sm text-gray-700 mb-1">
                <strong>Tipo:</strong> Recolección de basura
            </p>
            <p class="text-sm text-gray-700 mb-1">
                <strong>Nombre:</strong> ${datos.nombre || "-"}
            </p>
            <p class="text-sm text-gray-700 mb-1">
                <strong>Código:</strong> ${datos.codigo_unidad || datos.identificador || "-"}
            </p>
            <p class="text-sm text-gray-700 mb-1">
                <strong>Zona:</strong> ${datos.zona || "-"}
            </p>
            <p class="text-sm text-gray-700 mb-3">
                <strong>Estado:</strong> ${datos.estado || "-"}
            </p>
            <hr class="my-3">
            <h4 class="font-semibold text-sm mb-2">Estadísticas en vivo</h4>
            <div class="space-y-1 text-sm">
                <div class="flex justify-between">
                    <span>Transporte activo</span>
                    <span class="font-bold text-green-600">${transporteMarkers.length}</span>
                </div>
                <div class="flex justify-between">
                    <span>Recolección activa</span>
                    <span class="font-bold text-yellow-600">${basuraMarkers.length}</span>
                </div>
            </div>
        `;
    }
}

/* -------------------- BOTONES UI -------------------- */

function setupButtons() {
    const btnUbicacion = document.getElementById("btn-ubicacion");
    const btnBuscar = document.getElementById("btn-buscar");
    const btnTodos = document.getElementById("btn-todos");
    const btnTransporte = document.getElementById("btn-transporte");
    const btnBasura = document.getElementById("btn-basura");
    const btnActualizar = document.getElementById("btn-actualizar");
    const inputBuscar = document.getElementById("input-buscar");

    if (btnUbicacion) {
        btnUbicacion.addEventListener("click", () => {
            if (userPosition) {
                map.panTo(userPosition);
                map.setZoom(14);
            }
        });
    }

    if (btnBuscar) {
        btnBuscar.addEventListener("click", () => {
            dibujarRutasSeleccionadas();
            aplicarFiltros();
        });
    }

    if (btnTodos) {
        btnTodos.addEventListener("click", () => {
            currentTipoFiltro = "todos";
            aplicarFiltros();
        });
    }

    if (btnTransporte) {
        btnTransporte.addEventListener("click", () => {
            currentTipoFiltro = "transporte";
            aplicarFiltros();
        });
    }

    if (btnBasura) {
        btnBasura.addEventListener("click", () => {
            currentTipoFiltro = "basura";
            aplicarFiltros();
        });
    }

    if (btnActualizar) {
        btnActualizar.addEventListener("click", () => {
            actualizarUnidades();
        });
    }

    if (inputBuscar) {
        inputBuscar.addEventListener("input", () => {
            aplicarFiltros();
        });
    }
}
