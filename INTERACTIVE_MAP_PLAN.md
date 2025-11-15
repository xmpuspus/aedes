# Interactive Satellite Data Viewer - Comprehensive Implementation Plan

**Project Goal:** Draw a box on a map and immediately retrieve satellite data (NDVI, NDWI, temperature, etc.)

**Timeline:** 4-6 weeks for MVP, 8-12 weeks for production version

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Phase 1: Basic Prototype](#phase-1-basic-prototype)
4. [Phase 2: Enhanced Features](#phase-2-enhanced-features)
5. [Phase 3: Production Deployment](#phase-3-production-deployment)
6. [Detailed Implementation Steps](#detailed-implementation-steps)
7. [Code Examples](#code-examples)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Guide](#deployment-guide)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │    Interactive Map (Leaflet/OpenLayers)                │ │
│  │    - Draw bounding box                                 │ │
│  │    - Display results                                   │ │
│  └────────────────┬───────────────────────────────────────┘ │
└───────────────────┼──────────────────────────────────────────┘
                    │
                    │ AJAX/WebSocket
                    │
┌───────────────────▼──────────────────────────────────────────┐
│                    Backend API Server                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FastAPI / Flask                                       │ │
│  │  - Receive bounding box coordinates                    │ │
│  │  - Validate inputs                                     │ │
│  │  - Queue processing job                                │ │
│  │  - Return results                                      │ │
│  └────────────────┬───────────────────────────────────────┘ │
└───────────────────┼──────────────────────────────────────────┘
                    │
                    │
┌───────────────────▼──────────────────────────────────────────┐
│              Processing Layer (Celery/RQ)                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Task Queue Worker                                     │ │
│  │  - Fetch satellite data from GEE                       │ │
│  │  - Calculate indices (NDVI, NDWI, etc.)                │ │
│  │  - Process and aggregate data                          │ │
│  └────────────────┬───────────────────────────────────────┘ │
└───────────────────┼──────────────────────────────────────────┘
                    │
                    │
┌───────────────────▼──────────────────────────────────────────┐
│                 External Services                            │
│  ┌──────────────────┐  ┌─────────────────┐                  │
│  │ Google Earth     │  │ Redis Cache     │                  │
│  │ Engine           │  │ (for results)   │                  │
│  └──────────────────┘  └─────────────────┘                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Option A: Lightweight Stack (Fastest to Implement)
**Recommended for MVP**

**Frontend:**
- **Leaflet.js** - Interactive maps (smaller, simpler than OpenLayers)
- **Leaflet.draw** - Drawing tools for bounding boxes
- **Vanilla JavaScript** or **Alpine.js** - Minimal framework
- **Tailwind CSS** - Styling

**Backend:**
- **Flask** - Simple Python web framework
- **Flask-CORS** - Handle cross-origin requests
- **AEDES package** - Your existing satellite data functions

**Data Processing:**
- **Google Earth Engine Python API** - Satellite data
- **In-process** (synchronous for MVP)

**Deployment:**
- **Single server** - DigitalOcean, Heroku, or local

**Pros:**
- Fastest to build (1-2 weeks)
- Simple architecture
- Easy to debug
- Low cost

**Cons:**
- Limited scalability
- Blocking requests (slow for large areas)

---

### Option B: Production Stack (Better for Scale)
**Recommended for production**

**Frontend:**
- **React** or **Next.js** - Modern UI framework
- **Mapbox GL JS** or **Deck.gl** - Advanced visualization
- **TypeScript** - Type safety
- **TailwindCSS** - Styling

**Backend:**
- **FastAPI** - Modern, async Python framework
- **Pydantic** - Data validation
- **SQLAlchemy** - Database ORM

**Data Processing:**
- **Celery** - Distributed task queue
- **Redis** - Message broker and cache
- **Google Earth Engine** - Satellite data

**Database:**
- **PostgreSQL + PostGIS** - Store results, geometries
- **Redis** - Cache and session storage

**Deployment:**
- **Docker** - Containerization
- **Kubernetes** or **Docker Compose** - Orchestration
- **Cloud platform** - AWS/GCP/Azure

**Pros:**
- Highly scalable
- Non-blocking (async)
- Can handle multiple users
- Professional architecture

**Cons:**
- More complex (4-6 weeks)
- Higher cost
- Steeper learning curve

---

## Phase 1: Basic Prototype (Week 1-2)

**Goal:** Working MVP where you can draw a box and see satellite data

### Week 1: Setup & Backend

#### Day 1-2: Project Setup
```bash
# Create project structure
mkdir aedes-map-viewer
cd aedes-map-viewer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask flask-cors earthengine-api pandas geopandas

# Initialize project
mkdir -p {backend,frontend,static,templates}
```

#### Day 3-4: Backend API

**File: `backend/app.py`**
```python
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import ee
import sys
sys.path.append('../aedes')
from aedes.remote_sensing_utils import (
    initialize,
    get_satellite_measures_from_points,
    generate_random_ee_points
)

app = Flask(__name__,
            static_folder='../frontend/static',
            template_folder='../frontend/templates')
CORS(app)

# Initialize Google Earth Engine
try:
    initialize()
    print("✓ GEE initialized")
except:
    print("⚠ GEE initialization failed - run authenticate() first")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/satellite-data', methods=['POST'])
def get_satellite_data():
    """
    Endpoint to receive bounding box and return satellite data.

    Expected payload:
    {
        "bbox": [[lon1, lat1], [lon2, lat2], [lon3, lat3], [lon4, lat4], [lon1, lat1]],
        "date_from": "2024-01-01",
        "date_to": "2024-03-31",
        "sample_points": 20
    }
    """
    try:
        data = request.json

        # Validate input
        if not data or 'bbox' not in data:
            return jsonify({'error': 'Missing bounding box'}), 400

        bbox = data['bbox']
        date_from = data.get('date_from', '2024-01-01')
        date_to = data.get('date_to', '2024-03-31')
        sample_points = data.get('sample_points', 20)

        # Convert bbox to GEE-compatible format
        aoi_geojson = [bbox]

        # Generate random points in the area
        points = generate_random_ee_points(aoi_geojson, sample_points)

        # Get satellite data
        satellite_df = get_satellite_measures_from_points(
            points,
            aoi_geojson,
            date_from=date_from,
            date_to=date_to
        )

        # Convert to JSON-serializable format
        result = {
            'success': True,
            'data': satellite_df.to_dict('records'),
            'summary': {
                'points_analyzed': len(satellite_df),
                'date_range': f"{date_from} to {date_to}",
                'avg_ndvi': float(satellite_df['ndvi'].mean()) if 'ndvi' in satellite_df else None,
                'avg_temp': float(satellite_df['surface_temperature'].mean()) if 'surface_temperature' in satellite_df else None
            }
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

#### Day 5: Test Backend
```bash
# Start backend server
python backend/app.py

# Test health endpoint
curl http://localhost:5000/api/health

# Test satellite data endpoint
curl -X POST http://localhost:5000/api/satellite-data \
  -H "Content-Type: application/json" \
  -d '{
    "bbox": [[120.9897, 14.5893], [121.1338, 14.5893], [121.1338, 14.7764], [120.9897, 14.7764], [120.9897, 14.5893]],
    "date_from": "2024-01-01",
    "date_to": "2024-03-31",
    "sample_points": 5
  }'
```

---

### Week 2: Frontend

#### Day 1-3: Interactive Map

**File: `frontend/templates/index.html`**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AEDES Satellite Data Viewer</title>

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

    <!-- Leaflet Draw CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <style>
        #map {
            height: 100vh;
            width: 100%;
        }
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <!-- Control Panel -->
    <div class="absolute top-4 left-4 z-[1000] bg-white rounded-lg shadow-lg p-4 max-w-md">
        <h1 class="text-xl font-bold mb-4">🛰️ AEDES Satellite Viewer</h1>

        <div class="space-y-3">
            <!-- Date Range -->
            <div>
                <label class="block text-sm font-medium mb-1">Date From:</label>
                <input type="date" id="dateFrom" value="2024-01-01"
                       class="w-full px-3 py-2 border rounded">
            </div>

            <div>
                <label class="block text-sm font-medium mb-1">Date To:</label>
                <input type="date" id="dateTo" value="2024-03-31"
                       class="w-full px-3 py-2 border rounded">
            </div>

            <!-- Sample Points -->
            <div>
                <label class="block text-sm font-medium mb-1">Sample Points:</label>
                <input type="number" id="samplePoints" value="20" min="1" max="100"
                       class="w-full px-3 py-2 border rounded">
            </div>

            <!-- Instructions -->
            <div class="bg-blue-50 p-3 rounded text-sm">
                <p class="font-medium">Instructions:</p>
                <ol class="list-decimal ml-4 mt-1">
                    <li>Click the rectangle tool on the map</li>
                    <li>Draw a box on the area of interest</li>
                    <li>Wait for satellite data to load</li>
                </ol>
            </div>

            <!-- Status -->
            <div id="status" class="hidden">
                <div class="flex items-center space-x-2">
                    <div class="loading-spinner"></div>
                    <span>Fetching satellite data...</span>
                </div>
            </div>

            <!-- Results -->
            <div id="results" class="hidden bg-green-50 p-3 rounded">
                <h3 class="font-medium mb-2">Results:</h3>
                <div id="resultContent"></div>
            </div>

            <!-- Error -->
            <div id="error" class="hidden bg-red-50 p-3 rounded text-red-700">
                <p id="errorMessage"></p>
            </div>
        </div>
    </div>

    <!-- Map -->
    <div id="map"></div>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <!-- Leaflet Draw JS -->
    <script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>

    <script>
        // Initialize map centered on Philippines
        const map = L.map('map').setView([14.5995, 120.9842], 6);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        // Initialize draw control
        const drawnItems = new L.FeatureGroup();
        map.addLayer(drawnItems);

        const drawControl = new L.Control.Draw({
            draw: {
                polygon: false,
                polyline: false,
                circle: false,
                marker: false,
                circlemarker: false,
                rectangle: {
                    shapeOptions: {
                        color: '#3498db',
                        weight: 2,
                        fillOpacity: 0.2
                    }
                }
            },
            edit: {
                featureGroup: drawnItems,
                remove: true
            }
        });
        map.addControl(drawControl);

        // Handle rectangle drawn
        map.on('draw:created', function(e) {
            const layer = e.layer;
            drawnItems.addLayer(layer);

            // Get bounding box coordinates
            const bounds = layer.getBounds();
            const bbox = [
                [bounds.getWest(), bounds.getSouth()],
                [bounds.getEast(), bounds.getSouth()],
                [bounds.getEast(), bounds.getNorth()],
                [bounds.getWest(), bounds.getNorth()],
                [bounds.getWest(), bounds.getSouth()]
            ];

            // Fetch satellite data
            fetchSatelliteData(bbox);
        });

        // Fetch satellite data function
        async function fetchSatelliteData(bbox) {
            const statusDiv = document.getElementById('status');
            const resultsDiv = document.getElementById('results');
            const errorDiv = document.getElementById('error');

            // Show loading
            statusDiv.classList.remove('hidden');
            resultsDiv.classList.add('hidden');
            errorDiv.classList.add('hidden');

            // Get form values
            const dateFrom = document.getElementById('dateFrom').value;
            const dateTo = document.getElementById('dateTo').value;
            const samplePoints = parseInt(document.getElementById('samplePoints').value);

            try {
                const response = await fetch('http://localhost:5000/api/satellite-data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        bbox: bbox,
                        date_from: dateFrom,
                        date_to: dateTo,
                        sample_points: samplePoints
                    })
                });

                const result = await response.json();

                if (result.success) {
                    displayResults(result);
                    visualizeDataOnMap(result.data);
                } else {
                    showError(result.error);
                }

            } catch (error) {
                showError('Failed to fetch data: ' + error.message);
            } finally {
                statusDiv.classList.add('hidden');
            }
        }

        // Display results
        function displayResults(result) {
            const resultsDiv = document.getElementById('results');
            const resultContent = document.getElementById('resultContent');

            const html = `
                <p><strong>Points Analyzed:</strong> ${result.summary.points_analyzed}</p>
                <p><strong>Date Range:</strong> ${result.summary.date_range}</p>
                <p><strong>Avg NDVI:</strong> ${result.summary.avg_ndvi ? result.summary.avg_ndvi.toFixed(3) : 'N/A'}</p>
                <p><strong>Avg Temperature:</strong> ${result.summary.avg_temp ? result.summary.avg_temp.toFixed(1) + '°C' : 'N/A'}</p>
            `;

            resultContent.innerHTML = html;
            resultsDiv.classList.remove('hidden');
        }

        // Visualize data points on map
        function visualizeDataOnMap(data) {
            // Clear previous markers
            map.eachLayer(layer => {
                if (layer instanceof L.CircleMarker) {
                    map.removeLayer(layer);
                }
            });

            // Add markers for each point
            data.forEach(point => {
                if (point.latitude && point.longitude) {
                    const ndvi = point.ndvi || 0;
                    const color = getNDVIColor(ndvi);

                    L.circleMarker([point.latitude, point.longitude], {
                        radius: 6,
                        fillColor: color,
                        color: '#000',
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    })
                    .bindPopup(`
                        <strong>NDVI:</strong> ${ndvi.toFixed(3)}<br>
                        <strong>Temp:</strong> ${point.surface_temperature ? point.surface_temperature.toFixed(1) + '°C' : 'N/A'}<br>
                        <strong>NDWI:</strong> ${point.ndwi ? point.ndwi.toFixed(3) : 'N/A'}
                    `)
                    .addTo(map);
                }
            });
        }

        // Get color based on NDVI value
        function getNDVIColor(ndvi) {
            if (ndvi < 0) return '#0000ff';      // Water - Blue
            if (ndvi < 0.1) return '#d2b48c';    // Barren - Tan
            if (ndvi < 0.3) return '#ffff00';    // Sparse vegetation - Yellow
            if (ndvi < 0.6) return '#90ee90';    // Moderate vegetation - Light green
            return '#006400';                     // Dense vegetation - Dark green
        }

        // Show error
        function showError(message) {
            const errorDiv = document.getElementById('error');
            const errorMessage = document.getElementById('errorMessage');

            errorMessage.textContent = message;
            errorDiv.classList.remove('hidden');
        }
    </script>
</body>
</html>
```

#### Day 4-5: Testing & Refinement

**Testing Checklist:**
```
□ Draw rectangle on map
□ Backend receives correct coordinates
□ Satellite data fetched successfully
□ Results displayed on map
□ Colors show vegetation levels
□ Popup shows detailed data
□ Error handling works
□ Multiple rectangles can be drawn
□ Date picker works
□ Sample points slider works
```

---

## Phase 2: Enhanced Features (Week 3-4)

### Week 3: Advanced Visualization

#### Feature 1: Multiple Data Layers

**Add layer toggle:**
```javascript
// Layer control
const baseMaps = {
    "OpenStreetMap": osmLayer,
    "Satellite": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}')
};

const overlays = {
    "NDVI": ndviLayer,
    "Temperature": tempLayer,
    "Water Index": ndwiLayer
};

L.control.layers(baseMaps, overlays).addTo(map);
```

#### Feature 2: Heatmap Visualization

**Install plugin:**
```html
<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
```

**Add heatmap:**
```javascript
function createHeatmap(data, metric) {
    const heatData = data.map(point => [
        point.latitude,
        point.longitude,
        point[metric] || 0
    ]);

    return L.heatLayer(heatData, {
        radius: 25,
        blur: 15,
        maxZoom: 17
    }).addTo(map);
}
```

#### Feature 3: Time Series Chart

**Add Chart.js:**
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

**Endpoint for time series:**
```python
@app.route('/api/time-series', methods=['POST'])
def get_time_series():
    """Get NDVI time series for an area"""
    data = request.json
    bbox = data['bbox']

    # Fetch monthly NDVI for past year
    result = []
    for month in range(12):
        # Calculate date range
        # Fetch data
        # Aggregate
        result.append({'month': month, 'ndvi': avg_ndvi})

    return jsonify(result)
```

---

### Week 4: Performance & UX

#### Feature 4: Caching

**Install Redis:**
```bash
pip install redis
```

**Add caching:**
```python
import redis
import hashlib
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/api/satellite-data', methods=['POST'])
def get_satellite_data():
    data = request.json

    # Create cache key
    cache_key = hashlib.md5(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()

    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return jsonify(json.loads(cached))

    # Fetch data
    result = fetch_satellite_data(data)

    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(result))

    return jsonify(result)
```

#### Feature 5: Async Processing

**Install Celery:**
```bash
pip install celery
```

**Create task:**
```python
# tasks.py
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def fetch_satellite_data_async(bbox, date_from, date_to):
    # Long-running task
    result = get_satellite_measures_from_points(...)
    return result

# app.py
@app.route('/api/satellite-data', methods=['POST'])
def get_satellite_data():
    data = request.json

    # Start async task
    task = fetch_satellite_data_async.delay(
        data['bbox'],
        data['date_from'],
        data['date_to']
    )

    return jsonify({
        'task_id': task.id,
        'status': 'processing'
    })

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = fetch_satellite_data_async.AsyncResult(task_id)

    if task.ready():
        return jsonify({
            'status': 'complete',
            'result': task.result
        })
    else:
        return jsonify({
            'status': 'processing'
        })
```

**Frontend polling:**
```javascript
async function fetchSatelliteData(bbox) {
    // Start task
    const response = await fetch('/api/satellite-data', {...});
    const { task_id } = await response.json();

    // Poll for results
    const interval = setInterval(async () => {
        const status = await fetch(`/api/task/${task_id}`);
        const data = await status.json();

        if (data.status === 'complete') {
            clearInterval(interval);
            displayResults(data.result);
        }
    }, 2000); // Check every 2 seconds
}
```

#### Feature 6: Export Functionality

**Add export button:**
```html
<button onclick="exportData()" class="bg-blue-500 text-white px-4 py-2 rounded">
    Export CSV
</button>
```

**Export function:**
```javascript
function exportData(data) {
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'satellite_data.csv';
    a.click();
}

function convertToCSV(data) {
    const headers = Object.keys(data[0]);
    const rows = data.map(row =>
        headers.map(h => row[h]).join(',')
    );
    return [headers.join(','), ...rows].join('\n');
}
```

---

## Phase 3: Production Deployment (Week 5-6)

### Week 5: Production Optimization

#### Step 1: Containerization

**File: `Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
```

**File: `docker-compose.yml`**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    volumes:
      - .:/app

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A tasks worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    volumes:
      - .:/app

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
```

#### Step 2: Add Database

**PostgreSQL for storing results:**
```python
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry

db = SQLAlchemy(app)

class SatelliteQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bbox = db.Column(Geometry('POLYGON'))
    date_from = db.Column(db.Date)
    date_to = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    result_data = db.Column(db.JSON)

# Save query
query = SatelliteQuery(
    bbox=f'POLYGON(({bbox_str}))',
    date_from=date_from,
    date_to=date_to,
    result_data=result
)
db.session.add(query)
db.session.commit()
```

#### Step 3: Add Authentication (Optional)

**Simple token-based auth:**
```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.environ.get('API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/satellite-data', methods=['POST'])
@require_api_key
def get_satellite_data():
    # ...
```

---

### Week 6: Deployment & Monitoring

#### Deploy to DigitalOcean

**1. Create Droplet:**
```bash
# SSH into droplet
ssh root@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose

# Clone repository
git clone https://github.com/yourusername/aedes-map-viewer
cd aedes-map-viewer

# Set environment variables
cp .env.example .env
nano .env  # Edit with your values

# Start services
docker-compose up -d
```

**2. Setup HTTPS with Let's Encrypt:**
```bash
# Install Certbot
apt install certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d yourdomain.com
```

**3. Add monitoring:**
```bash
# Install monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d
```

**File: `docker-compose.monitoring.yml`**
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## Advanced Features (Optional)

### Feature 7: Real-time Collaboration

**WebSocket for live updates:**
```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('draw_rectangle')
def handle_rectangle(data):
    # Broadcast to all users
    emit('rectangle_drawn', data, broadcast=True)
```

### Feature 8: AI-Powered Insights

**Add GPT analysis:**
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route('/api/analyze', methods=['POST'])
def analyze_area():
    data = request.json
    satellite_data = data['satellite_data']

    prompt = f"""
    Analyze this satellite data for disease risk:

    Average NDVI: {satellite_data['avg_ndvi']}
    Average Temperature: {satellite_data['avg_temp']}°C
    Average Precipitation: {satellite_data['avg_precip']}

    Provide a risk assessment and recommendations.
    """

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return jsonify({
        'analysis': message.content[0].text
    })
```

### Feature 9: Mobile App

**React Native version:**
```javascript
import MapView, { PROVIDER_GOOGLE } from 'react-native-maps';
import { DrawableMap } from 'react-native-drawable-map';

export default function App() {
  return (
    <DrawableMap
      provider={PROVIDER_GOOGLE}
      onShapeComplete={(shape) => {
        fetchSatelliteData(shape.coordinates);
      }}
    />
  );
}
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_api.py
import pytest
from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_satellite_data_endpoint(client):
    payload = {
        'bbox': [[120.9, 14.5], [121.1, 14.5], [121.1, 14.7], [120.9, 14.7], [120.9, 14.5]],
        'date_from': '2024-01-01',
        'date_to': '2024-03-31',
        'sample_points': 5
    }
    response = client.post('/api/satellite-data', json=payload)
    assert response.status_code == 200
    assert 'success' in response.json
```

### Integration Tests

```python
def test_end_to_end_flow():
    # 1. Draw rectangle
    # 2. Submit to API
    # 3. Verify data returned
    # 4. Check visualization
    pass
```

### Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
locust -f locustfile.py --host=http://localhost:5000
```

---

## Performance Optimization

### 1. Batch Processing

```python
# Process multiple points in parallel
from concurrent.futures import ThreadPoolExecutor

def process_points_parallel(points):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_single_point, points))
    return results
```

### 2. CDN for Static Assets

```html
<!-- Use CDN for libraries -->
<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.js"></script>
```

### 3. Lazy Loading

```javascript
// Load data only when needed
map.on('moveend', () => {
    if (map.getZoom() > 12) {
        loadDetailedData();
    }
});
```

### 4. Progressive Loading

```javascript
// Load data in chunks
async function loadDataProgressively(bbox) {
    const chunks = splitIntoChunks(bbox, 4); // 4x4 grid

    for (const chunk of chunks) {
        const data = await fetchData(chunk);
        displayData(data);
    }
}
```

---

## Cost Estimation

### MVP (Phase 1)
- **Hosting:** $0-10/month (local or Heroku free tier)
- **Google Earth Engine:** Free (personal use)
- **Total:** $0-10/month

### Production (Phase 3)
- **Server:** $20-50/month (DigitalOcean droplet)
- **Database:** $15/month (Managed PostgreSQL)
- **Redis:** $10/month (Managed Redis)
- **Domain:** $12/year
- **SSL:** Free (Let's Encrypt)
- **CDN:** $0-20/month (Cloudflare)
- **Google Earth Engine:** Free up to limits, then pay-as-you-go
- **Total:** $45-95/month

---

## Security Checklist

- [ ] Input validation on all endpoints
- [ ] Rate limiting (100 requests/hour per IP)
- [ ] HTTPS enabled
- [ ] API key authentication
- [ ] CORS properly configured
- [ ] SQL injection prevention (use ORM)
- [ ] XSS prevention (sanitize inputs)
- [ ] Environment variables for secrets
- [ ] Regular security updates

---

## Timeline Summary

**Week 1:** Backend API setup
**Week 2:** Frontend map interface
**Week 3:** Advanced visualization
**Week 4:** Performance optimization
**Week 5:** Production setup
**Week 6:** Deployment & monitoring

**Total:** 6 weeks for full production system
**MVP:** 2 weeks for basic working version

---

## Next Steps

1. **Choose your approach:**
   - Quick MVP → Use Option A (Flask + Leaflet)
   - Production system → Use Option B (FastAPI + React)

2. **Set up development environment:**
   ```bash
   git clone https://github.com/xmpuspus/aedes
   cd aedes
   mkdir map-viewer
   cd map-viewer
   # Follow Day 1-2 setup
   ```

3. **Authenticate Google Earth Engine:**
   ```python
   import ee
   ee.Authenticate()
   ee.Initialize()
   ```

4. **Start building!**

---

## Troubleshooting Guide

### Issue: GEE Authentication Fails
**Solution:**
```bash
earthengine authenticate
# Follow browser prompts
```

### Issue: Slow Data Loading
**Solutions:**
- Reduce sample points
- Cache results
- Use async processing
- Batch requests

### Issue: Map Not Displaying
**Solutions:**
- Check console for errors
- Verify Leaflet CDN loaded
- Check coordinate format
- Ensure CORS enabled

---

## Resources

- **Leaflet Docs:** https://leafletjs.com/
- **Google Earth Engine:** https://developers.google.com/earth-engine
- **Flask Tutorial:** https://flask.palletsprojects.com/
- **FastAPI Tutorial:** https://fastapi.tiangolo.com/
- **Docker Tutorial:** https://docs.docker.com/get-started/

---

**Ready to start? Let me know which approach you want to take, and I can help you build it step by step!**
