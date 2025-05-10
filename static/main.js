let map = L.map('map').setView([40.7128, -74.0060], 13); // Default to NYC
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let routeLayer = null;
let poiLayer = null;

document.getElementById('routeBtn').onclick = async function() {
    const startInput = document.getElementById('start').value.trim();
    const endInput = document.getElementById('end').value.trim();
    const errorSpan = document.getElementById('error');
    errorSpan.textContent = '';

    // Parse input
    try {
        var [startLat, startLon] = startInput.split(',').map(Number);
        var [endLat, endLon] = endInput.split(',').map(Number);
        if ([startLat, startLon, endLat, endLon].some(isNaN)) throw 'Invalid';
    } catch {
        errorSpan.textContent = 'Invalid coordinates! Use format: lat,lon';
        return;
    }

    // Send to backend
    const res = await fetch('/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            start: [startLon, startLat], // OSRM expects [lon,lat]
            end: [endLon, endLat]
        })
    });
    if (!res.ok) {
        errorSpan.textContent = 'Failed to get route.';
        return;
    }
    const data = await res.json();
    if (!data.routes || !data.routes[0]) {
        errorSpan.textContent = 'No route found.';
        return;
    }
    const coords = data.routes[0].geometry.coordinates.map(([lon, lat]) => [lat, lon]);

    // Remove old route and POIs
    if (routeLayer) map.removeLayer(routeLayer);
    if (poiLayer) map.removeLayer(poiLayer);
    routeLayer = L.polyline(coords, { color: 'blue', weight: 5 }).addTo(map);
    map.fitBounds(routeLayer.getBounds());

    // Collect selected sightseeing types
    const typeCheckboxes = document.querySelectorAll('.sight-type:checked');
    const selectedTypes = Array.from(typeCheckboxes).map(cb => cb.value);

    // Fetch sightseeing POIs along the route
    const poiRes = await fetch('/sightseeing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            geometry: {
                type: 'LineString',
                coordinates: data.routes[0].geometry.coordinates
            },
            types: selectedTypes
        })
    });
    if (poiRes.ok) {
        const poiData = await poiRes.json();
        poiLayer = L.geoJSON(poiData, {
            pointToLayer: function(feature, latlng) {
                return L.marker(latlng);
            },
            onEachFeature: function(feature, layer) {
                layer.bindPopup(feature.properties.name);
            }
        }).addTo(map);
    }
}; 