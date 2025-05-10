# Route Finder Web App

This is a simple Python web application that allows you to find and display a route between two places using free map services (OpenStreetMap and OSRM).

## Features
- Interactive map (OpenStreetMap via Leaflet.js)
- Enter start and end coordinates to find a route
- Route is calculated using OSRM (Open Source Routing Machine)
- No API keys required

## Setup

1. **Clone the repository**

2. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application**

    ```bash
    python app.py
    ```

4. **Open your browser**

    Go to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Usage
- Enter the start and end coordinates in the format: `lat,lon` (e.g., `40.7128,-74.0060`)
- Click **Get Route**
- The route will be displayed on the map

## File Structure
- `app.py` — Flask backend
- `templates/index.html` — Main web page
- `static/main.js` — JavaScript for map and route logic
- `requirements.txt` — Python dependencies

## Notes
- This app uses the public OSRM demo server and OpenStreetMap tiles. For production or heavy use, consider running your own OSRM server.
- Only coordinates are supported for input (no address search).

## License
MIT 

## DEBUG DATA
Start (Times Square): 40.7580,-73.9855
End (Central Park, near the Metropolitan Museum of Art): 40.7812,-73.9665
