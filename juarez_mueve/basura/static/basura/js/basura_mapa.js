      let map, markers = {}, polylines = [];

      function initMap() {
        // centro aproximado Juárez
        map = new google.maps.Map(document.getElementById("map"), {
          center: { lat: 31.6904, lng: -106.4245 },
          zoom: 12,
          streetViewControl: false,
        });
        cargarUnidadesBasura();
        setupButtons();
      }

      function setupButtons(){
        document.getElementById('btn-actualizar').addEventListener('click', cargarUnidadesBasura);
        document.getElementById('btn-todos').addEventListener('click', () => cargarUnidadesBasura());
        document.getElementById('btn-activos').addEventListener('click', () => cargarUnidadesBasura(true));
        document.getElementById('btn-buscar').addEventListener('click', buscarUnidad);
      }

      function buscarUnidad(){
        const q = document.getElementById('input-buscar').value.toLowerCase().trim();
        for (const id in markers){
          const m = markers[id];
          const text = (m.metadata.identificador + ' ' + (m.metadata.zona || '')).toLowerCase();
          m.setVisible(!q || text.includes(q));
        }
      }

      function clearMarkers(){
        for(const k in markers){ markers[k].setMap(null); }
        markers = {};
        for(const pl of polylines){ pl.setMap(null); }
        polylines = [];
      }

      async function cargarUnidadesBasura(onlyActivos=false){
        clearMarkers();
        const url = document.getElementById('map').dataset.apiUnidadesUrl || "{% url 'api_unidades_basura' %}";
        const resp = await fetch(url);
        if (!resp.ok) return console.error('Error al recuperar unidades');
        const json = await resp.json();
        const unidades = json.unidades || [];
        document.getElementById('stat-total').textContent = unidades.length;
        const activos = unidades.filter(u => u.activo).length;
        document.getElementById('stat-activos').textContent = activos;

        unidades.forEach(u => {
          if ((onlyActivos && !u.activo)) return;
          if (u.lat == null || u.lng == null) return; // sin coordenadas
          const pos = { lat: parseFloat(u.lat), lng: parseFloat(u.lng) };
          const icon = {
            path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
            scale: 5,
            strokeColor: u.activo ? "#16A34A" : "#9CA3AF",
            fillColor: u.activo ? "#16A34A" : "#9CA3AF",
            fillOpacity: 1
          };
          const marker = new google.maps.Marker({
            position: pos,
            map,
            title: u.identificador,
            icon,
          });
          marker.metadata = u;
          marker.addListener('click', () => mostrarInfoUnidad(u, marker));
          markers[u.id] = marker;
        });

        // Si guardas rutas (array de coordenadas) en la respuesta, las puedes dibujar así:
        // Ejemplo esperado en JSON: { rutas: [ { unidad_id: 1, coords: [ {lat:.., lng:..}, ... ] }, ... ] }
        if (json.rutas){
          json.rutas.forEach(r => {
            const path = r.coords.map(c => ({ lat: parseFloat(c.lat), lng: parseFloat(c.lng) }));
            const pl = new google.maps.Polyline({ path, map, strokeColor: '#F59E0B', strokeWeight: 3 });
            polylines.push(pl);
          });
        }
      }

      function mostrarInfoUnidad(u, marker){
        const info = document.getElementById('info-unidad');
        info.innerHTML = `
          <div class="space-y-2">
            <div><strong>ID:</strong> ${u.id}</div>
            <div><strong>Unidad:</strong> ${u.identificador}</div>
            <div><strong>Zona:</strong> ${u.zona}</div>
            <div><strong>Activo:</strong> ${u.activo ? 'Sí' : 'No'}</div>
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
