# 🛰️ AEDES Interactive Satellite Data Viewer

An interactive web application that allows you to draw a bounding box on a map and immediately retrieve satellite data (NDVI, temperature, precipitation, etc.) using Google Earth Engine.

![AEDES Map Viewer](https://img.shields.io/badge/status-production-green)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

### 🗺️ Interactive Mapping
- **Draw bounding boxes** directly on OpenStreetMap
- **Switch between** street map and satellite imagery
- **Zoom and pan** to any location worldwide
- **Real-time visualization** of satellite data points

### 📊 Satellite Data Analysis
- **NDVI** - Vegetation index (dense vegetation to water bodies)
- **NDWI** - Water index (water body detection)
- **NDBI** - Built-up index (urban areas)
- **Surface Temperature** - Land surface temperature (°C)
- **Precipitation** - Precipitation rate
- **Relative Humidity** - Humidity percentage
- **Aerosol Index** - Air quality indicator

### 📈 Data Visualization
- **Color-coded markers** showing vegetation levels
- **Interactive popups** with detailed metrics
- **Distribution charts** using Chart.js
- **Summary statistics** panel
- **Export to CSV** functionality

### ⚡ Performance
- **Configurable sample points** (5-50 points)
- **Custom date ranges** for analysis
- **Quick test button** for demonstration
- **Real-time loading indicators**

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Google Earth Engine account** - [Sign up here](https://earthengine.google.com/signup/)
3. **Git** for cloning the repository

### Installation

```bash
# 1. Navigate to the map-viewer directory
cd map-viewer

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install parent AEDES package (from parent directory)
cd ..
pip install -e .
cd map-viewer

# 5. Authenticate with Google Earth Engine
earthengine authenticate
# Follow the browser prompts to authenticate

# 6. Start the server
python backend/app.py
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

## 📖 How to Use

### Method 1: Draw on Map (Recommended)

1. **Click** the square/rectangle tool in the map toolbar (top-left)
2. **Draw** a rectangle over your area of interest
3. **Wait** for the satellite data to load (usually 30-60 seconds)
4. **Explore** the results in the right panel
5. **Click** on colored markers to see detailed data
6. **Export** your data to CSV if needed

### Method 2: Quick Test

1. Click the **"🚀 Quick Test (Quezon City)"** button
2. Instantly see sample data from Quezon City, Philippines
3. Great for testing or demonstration

## 🎨 Understanding the Visualization

### NDVI Color Legend

| Color | NDVI Range | Meaning |
|-------|-----------|---------|
| 🔵 Blue | < 0 | Water bodies |
| 🟤 Tan | 0 - 0.1 | Barren land, rocks, sand |
| 🟡 Yellow | 0.1 - 0.3 | Sparse vegetation, grasslands |
| 🟢 Light Green | 0.3 - 0.6 | Moderate vegetation |
| 🌲 Dark Green | > 0.6 | Dense vegetation, forests |

### Results Panel

- **Summary Stats** - Key metrics at a glance
- **Detailed Metrics** - Min/max values for all indicators
- **Distribution Chart** - Visual breakdown of NDVI categories
- **Export Button** - Download data as CSV

## 🔧 Configuration

### Date Range
- **Start Date** - Beginning of analysis period
- **End Date** - End of analysis period
- Default: Last 3 months

### Sample Points
- **Range**: 5-50 points
- **Default**: 20 points
- More points = better accuracy but slower processing

## 🏗️ Architecture

```
Frontend (Leaflet.js)
    ↓
Backend API (Flask)
    ↓
AEDES Package (Python)
    ↓
Google Earth Engine
```

### API Endpoints

#### `GET /`
Main application page

#### `POST /api/satellite-data`
Fetch satellite data for a bounding box

**Request:**
```json
{
  "bbox": [[lon1, lat1], [lon2, lat2], [lon3, lat3], [lon4, lat4], [lon1, lat1]],
  "date_from": "2024-01-01",
  "date_to": "2024-03-31",
  "sample_points": 20
}
```

**Response:**
```json
{
  "success": true,
  "data": [...],
  "summary": {
    "points_analyzed": 20,
    "avg_ndvi": 0.45,
    "avg_surface_temperature": 28.5,
    ...
  }
}
```

#### `GET /api/health`
Health check endpoint

#### `GET /api/quick-test`
Quick test with pre-defined coordinates

## 🐛 Troubleshooting

### "Google Earth Engine is not available"

**Solution:**
```bash
# Authenticate with Google Earth Engine
earthengine authenticate

# Then restart the server
python backend/app.py
```

### "Module 'aedes' not found"

**Solution:**
```bash
# Install AEDES package from parent directory
cd ..
pip install -e .
cd map-viewer
```

### Map not loading

**Solution:**
- Check browser console for errors (F12)
- Ensure you're accessing `http://localhost:5000` not `file://`
- Check that Flask server is running

### Slow data loading

**Solution:**
- Reduce sample points (try 10 instead of 20)
- Use smaller bounding boxes
- Check your internet connection
- Google Earth Engine may be experiencing delays

### CORS errors

**Solution:**
- Flask-CORS is already configured
- If still seeing errors, check that you're accessing via `localhost` not `127.0.0.1`

## 📊 Sample Use Cases

### 1. Agricultural Monitoring
Draw boxes over farmlands to monitor:
- Crop health (NDVI)
- Water availability (NDWI)
- Temperature stress

### 2. Urban Heat Island Detection
Analyze urban areas for:
- Built-up density (NDBI)
- Surface temperature
- Vegetation coverage

### 3. Disease Risk Assessment
Identify potential disease hotspots by analyzing:
- Standing water (low NDVI, high NDWI)
- Temperature patterns
- Precipitation levels
- Vegetation density

### 4. Environmental Monitoring
Track environmental changes:
- Deforestation (decreasing NDVI)
- Water body changes (NDWI trends)
- Urban expansion (increasing NDBI)

## 🔒 Security Notes

- The application runs locally by default
- Google Earth Engine authentication is required
- No data is stored on the server (stateless)
- All processing happens in your session

## 🚀 Production Deployment

For production deployment, see the [INTERACTIVE_MAP_PLAN.md](../INTERACTIVE_MAP_PLAN.md) document which includes:

- Docker containerization
- Redis caching
- Async processing with Celery
- PostgreSQL database integration
- HTTPS setup
- Monitoring with Prometheus/Grafana

## 📝 Project Structure

```
map-viewer/
├── backend/
│   └── app.py              # Flask API server
├── frontend/
│   ├── templates/
│   │   └── index.html      # Main application page
│   └── static/             # Static assets (if any)
├── config/                 # Configuration files
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🤝 Contributing

This is part of the AEDES project. Contributions are welcome!

## 📄 License

MIT License - see parent AEDES project

## 🙏 Acknowledgments

- **Google Earth Engine** - Satellite data platform
- **Leaflet.js** - Interactive mapping library
- **OpenStreetMap** - Map tiles
- **AEDES Project** - Core satellite data processing

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. See the [INTERACTIVE_MAP_PLAN.md](../INTERACTIVE_MAP_PLAN.md) for detailed implementation guide
3. Review Google Earth Engine [documentation](https://developers.google.com/earth-engine)

## 🎯 Next Steps

After getting the basic app running:

1. **Explore different areas** - Try different locations worldwide
2. **Experiment with date ranges** - See seasonal changes
3. **Adjust sample points** - Find the right balance of speed vs accuracy
4. **Export data** - Download CSV for further analysis
5. **Compare time periods** - Run analyses for different dates

---

**Built with ❤️ using AEDES**

*Version 1.0.0*
