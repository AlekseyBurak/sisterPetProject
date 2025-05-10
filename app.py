import logging
from flask import Flask, render_template, request, jsonify
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

app = Flask(__name__)


@app.route('/')
def index():
    logging.info("Serving index page")
    return render_template('index.html')


@app.route('/route', methods=['POST'])
def route():
    data = request.json
    logging.info(f"Received /route request: {data}")
    start = data.get('start')  # [lon, lat]
    end = data.get('end')      # [lon, lat]
    if not start or not end:
        logging.error("Missing coordinates in /route request")
        return jsonify({'error': 'Missing coordinates'}), 400
    osrm_url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{start[0]},{start[1]};{end[0]},{end[1]}"
        f"?overview=full&geometries=geojson"
    )
    logging.info(f"Requesting OSRM route: {osrm_url}")
    resp = requests.get(osrm_url)
    if resp.status_code != 200:
        logging.error(f"OSRM request failed: {resp.status_code} {resp.text}")
        return jsonify({'error': 'OSRM request failed'}), 500
    logging.info("OSRM route request successful")
    return jsonify(resp.json())


@app.route('/sightseeing', methods=['POST'])
def sightseeing():
    data = request.json
    logging.info(f"Received /sightseeing request: {data}")
    geometry = data.get('geometry')  # GeoJSON LineString
    if not geometry or geometry.get('type') != 'LineString':
        logging.error("Missing or invalid geometry in /sightseeing request")
        return jsonify({'error': 'Missing or invalid geometry'}), 400
    coords = geometry['coordinates']
    types = data.get('types', [])
    if not types:
        logging.info("No sightseeing types selected; returning empty feature collection.")
        return jsonify({'type': 'FeatureCollection', 'features': []})
    # Sample every 20th point (or all if less than 20)
    sample_points = coords[::20] if len(coords) > 20 else coords
    overpass_query = '[out:json][timeout:25];\n('
    for lon, lat in sample_points:
        for t in types:
            if '=' in t:
                key, value = t.split('=', 1)
                if value == '*':
                    overpass_query += f'node["{key}"](around:50,{lat},{lon});'
                    overpass_query += f'way["{key}"](around:50,{lat},{lon});'
                    overpass_query += f'relation["{key}"](around:50,{lat},{lon});'
                else:
                    overpass_query += f'node["{key}"="{value}"](around:50,{lat},{lon});'
                    overpass_query += f'way["{key}"="{value}"](around:50,{lat},{lon});'
                    overpass_query += f'relation["{key}"="{value}"](around:50,{lat},{lon});'
    overpass_query += ');\nout center tags;'
    logging.info("Requesting Overpass API for sightseeing POIs")
    resp = requests.post(
        'https://overpass-api.de/api/interpreter',
        data={'data': overpass_query},
        headers={'Accept': 'application/json'}
    )
    if resp.status_code != 200:
        logging.error(
            f"Overpass request failed: {resp.status_code} {resp.text}"
        )
        return jsonify({'error': 'Overpass request failed'}), 500
    pois = resp.json().get('elements', [])
    logging.info(f"Found {len(pois)} POIs along the route")
    # Remove duplicates by OSM id/type
    seen = set()
    features = []
    for el in pois:
        el_id = (el['type'], el['id'])
        if el_id in seen:
            continue
        seen.add(el_id)
        if el['type'] == 'node':
            lon, lat = el['lon'], el['lat']
        elif 'center' in el:
            lon, lat = el['center']['lon'], el['center']['lat']
        else:
            continue
        features.append({
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
            'properties': {
                'name': el['tags'].get('name', 'Unknown'),
                'type': el['type'],
                'tags': el.get('tags', {})
            }
        })
    logging.info(
        f"Returning {len(features)} sightseeing features as GeoJSON"
    )
    return jsonify({'type': 'FeatureCollection', 'features': features})


@app.errorhandler(500)
def handle_500_error(e):
    logging.exception("Internal server error: %s", e)
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logging.info("Starting Flask app")
    app.run(debug=True) 