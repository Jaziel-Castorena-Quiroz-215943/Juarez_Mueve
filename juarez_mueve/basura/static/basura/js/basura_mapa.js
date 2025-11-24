let map, markers = {};

function initMap() {
  // Centro aproximado Juárez
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 31.6904, lng: -106.4245 },
    zoom: 12,
    streetViewControl: false,
  });

  cargarPosiciones();
  setupButtons();

  // 🔥 Actualizar cada 5 segundos
  setInterval(cargarPosiciones, 5000);
}

function setupButtons() {
  document.getElementById('btn-actualizar').addEventListener('click', cargarPosiciones);
  document.getElementById('btn-todos').addEventListener('click', () => cargarPosiciones());
  document.getElementById('btn-activos').addEventListener('click', () => cargarPosiciones(true));
  document.getElementById('btn-buscar').addEventListener('click', buscarUnidad);
}

function buscarUnidad() {
  const q = document.getElementById('input-buscar').value.toLowerCase().trim();
  for (const id in markers) {
    const m = markers[id];
    const text = (m.metadata.codigo + ' ' + (m.metadata.zona || '')).toLowerCase();
    m.setVisible(!q || text.includes(q));
  }
}

function cargarPosiciones(onlyActivos = false) {
  const url = "/basura/api/posiciones/";

  fetch(url)
    .then(resp => resp.json())
    .then(json => {
      const unidades = json.unidades || [];

      // estadísticas
      document.getElementById('stat-total').textContent = unidades.length;
      const activos = unidades.filter(u => u.estado === "ACTIVO").length;
      document.getElementById('stat-activos').textContent = activos;

      unidades.forEach(u => {
        if (!u.lat || !u.lng) return;
        if (onlyActivos && u.estado !== "ACTIVO") return;

        const pos = { lat: parseFloat(u.lat), lng: parseFloat(u.lng) };

        if (!markers[u.id]) {
          // crear nuevo marcador
          const marker = new google.maps.Marker({
            position: pos,
            map,
            title: u.codigo,
            icon: {
              url: u.estado === "ACTIVO"
                ? "https://maps.gstatic.com/mapfiles/ms2/micons/truck.png"
                : "https://maps.gstatic.com/mapfiles/ms2/micons/truck_gray.png",
              scaledSize: new google.maps.Size(32, 32)
            }
          });

          marker.metadata = {
            id: u.id,
            codigo: u.codigo,
            zona: u.zona,
            estado: u.estado
          };

          marker.addListener('click', () => mostrarInfoUnidad(marker.metadata, marker));

          markers[u.id] = marker;
        } else {
          // actualizar sólo la posición
          markers[u.id].setPosition(pos);
        }
      });
    });
}

function mostrarInfoUnidad(u, marker) {
  const info = document.getElementById('info-unidad');
  info.innerHTML = `
      <div class="space-y-2">
        <div><strong>ID:</strong> ${u.id}</div>
        <div><strong>Unidad:</strong> ${u.codigo}</div>
        <div><strong>Zona:</strong> ${u.zona}</div>
        <div><strong>Estado:</strong> ${u.estado}</div>
        <div class="mt-2">
          <button id="seguir-${u.id}" class="px-3 py-1 bg-blue-500 text-white rounded">Centrar</button>
        </div>
      </div>
    `;

  document.getElementById(`seguir-${u.id}`).addEventListener('click', () => {
    map.setCenter(marker.getPosition());
    map.setZoom(15);
  });
}
