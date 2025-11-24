    let map;
    let userMarker = null;

    let rutasPaths = {};  // { [idRuta]: [ {lat, lng}, {lat, lng}, ... ] }
    let simInterval = null;  // para la simulación sobre rutas
    let unidadMarkers = {}; // mapa unidadId -> marker
    let updateIntervalMs = 5000; // 5 segundos
    let updateTimer = null;

    // Datos en memoria
    let rutasData = [];            // Rutas con origen/destino (de rutas_mapa)
    let unidadesData = null;       // Datos de /api/unidades/ (transportes + basura)

    // Elementos de mapas
    let transporteMarkers = [];
    let basuraMarkers = [];
    let rutasPolylines = [];       // Aquí guardaremos los DirectionsRenderer

    // InfoWindow para mostrar datos al hacer clic
    let infoWindow;

    // Directions service de Google
    let directionsService;

    // Guardar centro de usuario
    let userPosition = { lat: 31.6904, lng: -106.4245 }; // fallback Ciudad Juárez

    function initMap() {
        const mapDiv = document.getElementById("map");
        const apiUnidadesUrl = mapDiv.dataset.apiUnidadesUrl;
        const apiRutasUrl = mapDiv.dataset.apiRutasUrl;
        // Actualizar unidades cada 3 segundos


        // Crear mapa centrado en Juárez (luego se actualiza con la ubicación del usuario)
        map = new google.maps.Map(mapDiv, {
            center: userPosition,
            zoom: 12,
        });

        infoWindow = new google.maps.InfoWindow();
        directionsService = new google.maps.DirectionsService();

        // 1) Intentar obtener ubicación del usuario y solo mostrar su marcador
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

        // 2) Cargar rutas desde la API y llenar el <select>
        fetch(apiRutasUrl)
            .then((res) => res.json())
            .then((data) => {
                rutasData = data.rutas || [];
                poblarSelectRutas(rutasData);
            })
            .catch((err) => {
                console.error("Error al cargar rutas:", err);
            });

        // 3) Eventos de botones y filtros
        const btnUbicacion = document.getElementById("btn-ubicacion");
        const btnBuscar = document.getElementById("btn-buscar");
        const btnTodos = document.getElementById("btn-todos");
        const btnTransporte = document.getElementById("btn-transporte");
        const btnBasura = document.getElementById("btn-basura");

        if (btnUbicacion) {
            btnUbicacion.addEventListener("click", () => {
                if (userPosition) {
                    map.panTo(userPosition);
                    map.setZoom(14);
                }
            });
        }

        // Mostrar rutas seleccionadas y sus unidades de transporte
        if (btnBuscar) {
            btnBuscar.addEventListener("click", () => {
                const selectedIds = obtenerRutasSeleccionadas();
                mostrarRutasYUnidades(selectedIds, apiUnidadesUrl, "todos");
            });
        }

        if (btnTodos) {
            btnTodos.addEventListener("click", () => {
                const selectedIds = obtenerRutasSeleccionadas();
                mostrarRutasYUnidades(selectedIds, apiUnidadesUrl, "todos");
            });
        }

        if (btnTransporte) {
            btnTransporte.addEventListener("click", () => {
                const selectedIds = obtenerRutasSeleccionadas();
                mostrarRutasYUnidades(selectedIds, apiUnidadesUrl, "transporte");
            });
        }

        if (btnBasura) {
            btnBasura.addEventListener("click", () => {
                const selectedIds = obtenerRutasSeleccionadas();
                mostrarRutasYUnidades(selectedIds, apiUnidadesUrl, "basura");
            });
        }
    }

    /**
     * Llena el <select id="select-rutas"> con las rutas traídas de la API.
     */
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

    /**
     * Devuelve un array con los IDs de rutas seleccionadas en el select.
     */
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

    /**
     * Limpia todo y:
     * - Dibuja las rutas seleccionadas usando origen/destino (Directions API)
     * - Muestra unidades según tipoFiltro:
     *   - "todos" → transporte de esas rutas + toda la basura
     *   - "transporte" → solo transporte de esas rutas
     *   - "basura" → solo basura (todas), pero deja las rutas visibles
     */
    function mostrarRutasYUnidades(rutaIds, apiUnidadesUrl, tipoFiltro) {
        limpiarPolylines();
        limpiarMarkers();

        if (!rutaIds || rutaIds.length === 0) {
            actualizarPanelEstadisticas(0, 0);
            return;
        }

        // 1) Dibujar rutas seleccionadas con Directions API
        rutasData
            .filter((r) => rutaIds.includes(r.id))
            .forEach((ruta) => {
                dibujarRuta(ruta);
            });

        // 2) Cargar unidades si no lo hemos hecho antes
        if (!unidadesData) {
            fetch(apiUnidadesUrl)
                .then((res) => res.json())
                .then((data) => {
                    unidadesData = data;
                    dibujarUnidades(rutaIds, tipoFiltro);
                })
                .catch((err) => {
                    console.error("Error al cargar unidades:", err);
                });
        } else {
            dibujarUnidades(rutaIds, tipoFiltro);
        }
    }

    function dibujarRuta(ruta) {

        // ==========================================
        // PRIORIDAD 1 → Coordenadas reales + waypoints
        // ==========================================
        if (
            ruta.origen_lat !== null && ruta.origen_lng !== null &&
            ruta.destino_lat !== null && ruta.destino_lng !== null
        ) {

            const directionsRenderer = new google.maps.DirectionsRenderer({
                map: map,
                suppressMarkers: true,
                polylineOptions: {
                    strokeColor: ruta.color || "#2563eb",
                    strokeOpacity: 0.9,
                    strokeWeight: 4,
                },
            });

            directionsService.route(
            {
                origin: { lat: ruta.origen_lat, lng: ruta.origen_lng },
                destination: { lat: ruta.destino_lat, lng: ruta.destino_lng },
                travelMode: google.maps.TravelMode.DRIVING,

                // 🔥🔥🔥 AQUI EL CAMBIO QUE SOLUCIONA EL PROBLEMA 🔥🔥🔥
                waypoints: ruta.puntos?.slice(1, -1).map(p => ({
                    location: new google.maps.LatLng(p.lat, p.lng),
                    stopover: false
                })) || [],
                optimizeWaypoints: false
            },
            (result, status) => {
                if (status === "OK") {
                    directionsRenderer.setDirections(result);
                    rutasPolylines.push(directionsRenderer);

                    // Guardar path completo para la simulación
                    const overviewPath = result.routes[0].overview_path;
                    rutasPaths[ruta.id] = overviewPath.map(ll => ({
                        lat: ll.lat(),
                        lng: ll.lng()
                    }));
                } else {
                    console.warn("Google Directions falló para ruta:", ruta.nombre, status);
                }
            });

            return;
        }

        // ==========================================
        // PRIORIDAD 2 → Polyline desde puntos
        // ==========================================
        if (ruta.puntos && ruta.puntos.length > 0) {
            const path = ruta.puntos.map(p => ({ lat: p.lat, lng: p.lng }));

            const poly = new google.maps.Polyline({
                path,
                geodesic: true,
                strokeColor: ruta.color || "#2563eb",
                strokeOpacity: 0.9,
                strokeWeight: 4,
                map
            });

            rutasPolylines.push(poly);
            rutasPaths[ruta.id] = path;

            const bounds = new google.maps.LatLngBounds();
            path.forEach(pt => bounds.extend(pt));
            map.fitBounds(bounds);

            return;
        }

        console.warn(`Ruta "${ruta.nombre}" no tiene datos suficientes.`);
    }

    /**
     * Pinta en el mapa los marcadores de transporte/basura según el filtro.
     */
    function dibujarUnidades(rutaIds, tipoFiltro) {
        if (!unidadesData) return;

        const transportes = unidadesData.transportes || [];
        const basura = unidadesData.basura || [];

        // Transporte: filtramos por ruta (ahora 'ruta' es el ID numérico)
        if (tipoFiltro === "todos" || tipoFiltro === "transporte") {
            transportes
                .filter(
                    (t) =>
                        t.latitud &&
                        t.longitud &&
                        t.ruta &&                 // tenga ruta
                        rutaIds.includes(t.ruta)  // pertenezca a las seleccionadas
                )
                .forEach((t) => {
                    const marker = new google.maps.Marker({
                        position: { lat: t.latitud, lng: t.longitud },
                        map: map,
                        title: t.nombre || t.numero_economico || "Unidad transporte",
                        icon: {
                            url: "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
                        },
                    });

                    // Asociar el id de ruta al marcador
                    marker._rutaId = t.ruta;

                    marker.addListener("click", () => {
                        mostrarInfoUnidad(t, "transporte", marker);
                    });

                    transporteMarkers.push(marker);


                    marker.addListener("click", () => {
                        mostrarInfoUnidad(t, "transporte", marker);
                    });

                    transporteMarkers.push(marker);
                });
        }

        // Basura: mostramos todas las activas (no dependen de la ruta)
        if (tipoFiltro === "todos" || tipoFiltro === "basura") {
            basura
                .filter((b) => b.latitud && b.longitud)
                .forEach((b) => {
                    const marker = new google.maps.Marker({
                        position: { lat: b.latitud, lng: b.longitud },
                        map: map,
                        title: b.nombre || b.codigo_unidad || "Unidad de basura",
                        icon: {
                            url: "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
                        },
                    });

                    marker.addListener("click", () => {
                        mostrarInfoUnidad(b, "basura", marker);
                    });

                    basuraMarkers.push(marker);
                });
        }

        actualizarPanelEstadisticas(transporteMarkers.length, basuraMarkers.length);
        iniciarSimulacionRutas();

    }

    /**
     * Limpia todos los marcadores (excepto el usuario).
     */
    function limpiarMarkers() {
        transporteMarkers.forEach((m) => m.setMap(null));
        basuraMarkers.forEach((m) => m.setMap(null));
        transporteMarkers = [];
        basuraMarkers = [];
    }

    /**
     * Limpia las polylines/renderers de rutas dibujadas.
     */
    function limpiarPolylines() {
        rutasPolylines.forEach((r) => r.setMap(null));
        rutasPolylines = [];
    }

    /**
     * Muestra la info del vehículo tanto en un InfoWindow
     * como en el panel lateral.
     */
    function mostrarInfoUnidad(datos, tipo, marker) {
        let contenido = "";

        if (tipo === "transporte") {
            contenido = `
                <div style="min-width:220px">
                    <strong>${datos.nombre || "Unidad de transporte"}</strong><br>
                    No. económico: ${datos.numero_economico || "-"}<br>
                    Ruta: ${datos.ruta_nombre || datos.ruta || "-"}<br>
                    Estado: ${datos.estado || "-"}
                </div>
            `;
        } else {
            contenido = `
                <div style="min-width:220px">
                    <strong>${datos.nombre || "Unidad de basura"}</strong><br>
                    Código: ${datos.codigo_unidad || "-"}<br>
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
        if (panel) {
            if (tipo === "transporte") {
                panel.innerHTML = `
                    <h3 class="font-semibold text-lg mb-3">Información de la unidad</h3>
                    <p class="text-sm text-gray-700 mb-1">
                        <strong>Tipo:</strong> Transporte público
                    </p>
                    <p class="text-sm text-gray-700 mb-1">
                        <strong>Nombre:</strong> ${datos.nombre || "-"}
                    </p>
                    <p class="text-sm text-gray-700 mb-1">
                        <strong>No. económico:</strong> ${datos.numero_economico || "-"}
                    </p>
                    <p class="text-sm text-gray-700 mb-1">
                        <strong>Ruta:</strong> ${datos.ruta_nombre || datos.ruta || "-"}
                    </p>
                    <p class="text-sm text-gray-700 mb-3">
                        <strong>Estado:</strong> ${datos.estado || "-"}
                    </p>
                    <hr class="my-3">
                    <h4 class="font-semibold text-sm mb-2">Estadísticas en vivo</h4>
                    <div class="space-y-1 text-sm">
                        <div class="flex justify-between">
                            <span>Transporte activo</span>
                            <span id="stat-transporte" class="font-bold text-green-600">${transporteMarkers.length}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Recolección activa</span>
                            <span id="stat-basura" class="font-bold text-yellow-600">${basuraMarkers.length}</span>
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
                        <strong>Código:</strong> ${datos.codigo_unidad || "-"}
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
                            <span id="stat-transporte" class="font-bold text-green-600">${transporteMarkers.length}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Recolección activa</span>
                            <span id="stat-basura" class="font-bold text-yellow-600">${basuraMarkers.length}</span>
                        </div>
                    </div>
                `;
            }
        }
    }

    /**
     * Actualiza el panel lateral cuando solo queremos mostrar conteos.
     */
    function actualizarPanelEstadisticas(numTransporte, numBasura) {
        const panel = document.getElementById("panel-detalles");
        if (!panel) return;

        panel.innerHTML = `
            <h3 class="font-semibold text-lg mb-3">Información</h3>
            <p class="text-sm text-gray-500 mb-6">
                Selecciona un vehículo en el mapa para ver sus detalles.
            </p>
            <h4 class="font-semibold text-sm mb-2">Estadísticas en vivo</h4>
            <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                    <span>Transporte activo</span>
                    <span id="stat-transporte" class="font-bold text-green-600">${numTransporte}</span>
                </div>
                <div class="flex justify-between">
                    <span>Recolección activa</span>
                    <span id="stat-basura" class="font-bold text-yellow-600">${numBasura}</span>
                </div>
            </div>
        `;
    }

    // -----------------------------------------------
    // ACTUALIZACIÓN AUTOMÁTICA DE UBICACIONES
    // -----------------------------------------------

    function actualizarUnidades() {
        const apiUrl = document.getElementById("map").dataset.apiUnidadesUrl;

        fetch(apiUrl)
            .then(res => res.json())
            .then(data => {
                unidadesData = data;
                animarMarcadores();
            })
            .catch(err => console.error("Error actualizando unidades:", err));
    }

    function animarMarcadores() {
        const transportes = unidadesData.transportes || [];

        transportes.forEach((u, index) => {
            const marker = transporteMarkers[index];
            if (!marker) return;

            const nuevaPos = new google.maps.LatLng(u.latitud, u.longitud);
            moverAnimado(marker, nuevaPos);
        });
    }

    function moverAnimado(marker, destino) {
    const inicio = marker.getPosition();

    // Antes:
    // const pasos = 30;        // más pasos = más suave
    // const duracion = 1000;   // 1 segundo

    // NUEVOS VALORES:
    const pasos = 80;        // más pasos = más suave
    const duracion = 4000;   // 4 segundos
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

function iniciarSimulacionRutas() {
    // Cancelar simulación anterior si existía
    if (simInterval) {
        clearInterval(simInterval);
        simInterval = null;
    }

    // Inicializar posición/progreso de cada transporte
    transporteMarkers.forEach(marker => {
        const rutaId = marker._rutaId;
        const path = rutasPaths[rutaId];

        if (!path || path.length < 2) {
            return;
        }

        // Empezar en un punto aleatorio del path para que no vayan todos pegados
        const startIndex = Math.floor(Math.random() * (path.length - 1));
        marker._routeIndex = startIndex;
        marker._t = Math.random(); // progreso dentro del segmento [0, 1]

        const start = path[startIndex];
        marker.setPosition(new google.maps.LatLng(start.lat, start.lng));
    });

    // Bucle de animación
    const frameMs = 200;     // tiempo entre frames
    const speed = 0.0008;      // avance por frame (más pequeño = más lento)

    simInterval = setInterval(() => {
        transporteMarkers.forEach(marker => {
            const rutaId = marker._rutaId;
            const path = rutasPaths[rutaId];

            if (!path || path.length < 2) return;

            let i = marker._routeIndex ?? 0;
            let t = marker._t ?? 0;

            const start = path[i];
            const end = path[i + 1];

            // Interpolamos entre start y end
            const lat = start.lat + (end.lat - start.lat) * t;
            const lng = start.lng + (end.lng - start.lng) * t;
            marker.setPosition(new google.maps.LatLng(lat, lng));

            // Avanzamos dentro del segmento
            t += speed;

            // Si terminamos el segmento, pasamos al siguiente
            if (t >= 1) {
                t = 0;
                i++;

                // Si llegamos al final del path, volvemos al inicio (loop)
                if (i >= path.length - 1) {
                    i = 0;
                }
            }

            marker._routeIndex = i;
            marker._t = t;
        });
    }, frameMs);
}
document.getElementById("form-queja").addEventListener("submit", async function(e) {
    e.preventDefault();

    const data = new FormData(this);

    let respuesta = await fetch("{% url 'enviar_queja' %}", {
        method: "POST",
        headers: {
            "X-CSRFToken": "{{ csrf_token }}",
        },
        body: data
    });

    let json = await respuesta.json();

    if (json.ok) {
        openQueja = false;
        openGracias = true;
    }
});

// ----------------- ACTUALIZAR UNIDADES (fetch) -----------------
function actualizarUnidades() {
    const apiUrl = document.getElementById("map").dataset.apiUnidadesUrl;
    if (!apiUrl) {
        console.warn("No se encontró api_unidades URL en el mapa.");
        return;
    }

    fetch(apiUrl)
        .then(res => {
            if (!res.ok) throw new Error("Respuesta no OK");
            return res.json();
        })
        .then(data => {
            // Esperamos estructura: { transportes: [...], basura: [...] }
            unidadesData = data; // mantener compatibilidad
            procesarUnidadesDesdeApi(data);
        })
        .catch(err => console.error("Error al obtener ubicaciones:", err));
}

/**
 * Crea o actualiza marcadores a partir del JSON de la API.
 * La API debe devolver para cada unidad al menos:
 * { id, identificador, latitud, longitud, ruta: <idRuta>, tipo: 'transporte'|'basura', nombre?, numero_economico? }
 */
function procesarUnidadesDesdeApi(data) {
    const transportes = data.transportes || [];
    const basuras = data.basura || [];

    // Procesar transportes
    transportes.forEach(u => {
        if (!u.id || !u.latitud || !u.longitud) return;

        const pos = new google.maps.LatLng(u.latitud, u.longitud);

        if (unidadMarkers[u.id]) {
            // Ya existe: animamos a la nueva posición
            moverAnimado(unidadMarkers[u.id], pos);
            unidadMarkers[u.id]._rutaId = u.ruta || unidadMarkers[u.id]._rutaId;
            unidadMarkers[u.id]._datos = u;
        } else {
            // Crear nuevo marcador
            const marker = new google.maps.Marker({
                position: pos,
                map: map,
                title: u.nombre || u.identificador || "Unidad transporte",
                icon: {
                    url: "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
                },
            });

            marker._unidadId = u.id;
            marker._rutaId = u.ruta || null;
            marker._datos = u;

            marker.addListener("click", () => {
                mostrarInfoUnidad(u, "transporte", marker);
            });

            unidadMarkers[u.id] = marker;
            transporteMarkers.push(marker);
        }
    });

    // Procesar basuras (similar)
    basuras.forEach(b => {
        if (!b.id || !b.latitud || !b.longitud) return;

        const pos = new google.maps.LatLng(b.latitud, b.longitud);

        if (unidadMarkers[b.id]) {
            moverAnimado(unidadMarkers[b.id], pos);
            unidadMarkers[b.id]._datos = b;
        } else {
            const marker = new google.maps.Marker({
                position: pos,
                map: map,
                title: b.nombre || b.codigo_unidad || "Unidad de basura",
                icon: {
                    url: "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
                },
            });

            marker._unidadId = b.id;
            marker._datos = b;

            marker.addListener("click", () => {
                mostrarInfoUnidad(b, "basura", marker);
            });

            unidadMarkers[b.id] = marker;
            basuraMarkers.push(marker);
        }
    });

    // Eliminar marcadores que ya no vienen en la API (opcional)
    // construimos sets de ids actuales
    const currentIds = new Set([
        ...(transportes.map(t => t.id || [])),
        ...(basuras.map(b => b.id || []))
    ]);

    Object.keys(unidadMarkers).forEach(key => {
        const id = parseInt(key, 10);
        if (!currentIds.has(id)) {
            unidadMarkers[id].setMap(null);
            delete unidadMarkers[id];
        }
    });

    actualizarPanelEstadisticas(transporteMarkers.length, basuraMarkers.length);
    // Si usas simulación por rutasPaths, la función iniciarSimulacionRutas() seguirá funcionando.
}

// ----------------- INICIAR / PARAR ACTUALIZACIONES PERIODICAS -----------------
function startAutoUpdate() {
    if (updateTimer) clearInterval(updateTimer);
    updateTimer = setInterval(actualizarUnidades, updateIntervalMs);
    // Hacemos una primera carga inmediata:
    actualizarUnidades();
}

function stopAutoUpdate() {
    if (updateTimer) {
        clearInterval(updateTimer);
        updateTimer = null;
    }
}

// ----------------- ENLACE CON BOTÓN ACTUALIZAR -----------------
// Llama a esto desde initMap (o ya lo puedes colocar dentro initMap donde defines el botón)
const btnActualizar = document.getElementById("btn-actualizar");
if (btnActualizar) {
    btnActualizar.addEventListener("click", () => {
        // Forzamos una actualización inmediata (y reiniciamos el timer)
        actualizarUnidades();
        if (!updateTimer) startAutoUpdate();
    });
}

// Iniciar actualización automática al finalizar initMap
// Añade al final de initMap():
// startAutoUpdate();