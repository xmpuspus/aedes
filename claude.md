# AEDES - Disease Risk Assessment Platform

## Project Overview

AEDES is a Python package for disease hotspot detection and risk assessment (particularly dengue) using geospatial data, remote sensing, and machine learning. The project combines satellite imagery analysis, OpenStreetMap data, social listening, and automated ML to identify high-risk areas for disease outbreaks.

**Author:** Xavier Puspus
**Affiliation:** Cirrolytix Research Services
**Repository:** https://github.com/xmpuspus/aedes

## Core Technologies

- **Google Earth Engine** - Satellite imagery and remote sensing data (LANDSAT, MODIS, SENTINEL)
- **OpenStreetMap** - Geospatial network analysis and amenities data
- **Python Data Stack** - pandas, numpy, scikit-learn
- **TPOT** - Tree-based Pipeline Optimization for AutoML
- **Streamlit** - Web application for visualization
- **Folium** - Interactive map visualizations

## Project Structure

```
aedes/
├── aedes/                          # Main package directory
│   ├── remote_sensing_utils.py     # Google Earth Engine integration, satellite data
│   ├── osm_utils.py                # OpenStreetMap network analysis
│   ├── automl_utils.py             # ML clustering and classification (TPOT)
│   └── social_listening_utils.py   # Google search trends data
├── app.py                          # Streamlit web application
├── demo.ipynb                      # Jupyter notebook demonstrations
├── best_aedes_model.py             # Example ML pipeline output
├── setup.py                        # Package installation configuration
├── requirements.txt                # Python dependencies
├── models/                         # Saved ML models
└── images/                         # Documentation images
```

## Key Components

### 1. Remote Sensing (remote_sensing_utils.py)

**Purpose:** Extract environmental and meteorological data from satellite imagery

**Key Functions:**
- `authenticate()` - Google Earth Engine authentication
- `initialize()` - Initialize GEE access
- `generate_random_ee_points(aoi, sample_points)` - Generate random points in AOI
- `df_to_ee_points(df)` - Convert dataframe to Earth Engine points
- `get_satellite_measures_from_points(points, aoi, date_from, date_to)` - Extract:
  - NDVI (Normalized Difference Vegetation Index)
  - NDWI (Normalized Difference Water Index)
  - NDBI (Normalized Difference Built-up Index)
  - Aerosol Index (air quality)
  - Surface temperature
  - Precipitation rate
  - Relative humidity
- `visualize_on_map(df)` - Create interactive Folium maps

**Data Sources:**
- Sentinel-2 for NDVI, NDWI, NDBI
- Sentinel-5P for Aerosol Index
- MODIS for surface temperature, precipitation, humidity

### 2. OpenStreetMap Analysis (osm_utils.py)

**Purpose:** Network analysis and amenities proximity calculations

**Key Functions:**
- `initialize_OSM_network(aoi_geojson)` - Create OSM network from AOI
- `get_OSM_network_data(network, satellite_df, aoi_geojson, amenities, k_nearest, max_distance, show_viz)` - Query amenities and calculate:
  - Count of facilities within radius
  - Distance to k-nearest facilities
  - Network-based routing analysis
- `reverse_geocode_points(df)` - Reverse geocoding using Nominatim

**Common Amenities:**
- Healthcare: 'clinic', 'hospital', 'doctors'
- Education: 'school', 'university'
- Infrastructure: 'water_point', 'waste_disposal'

### 3. AutoML Utilities (automl_utils.py)

**Purpose:** Automated machine learning for clustering and classification

**Key Functions:**
- `perform_clustering(df, features, n_clusters)` - KMeans clustering for risk zones
- `perform_classification(X_train, y_train)` - TPOT-based classifier optimization
- `perform_regression(X_train, y_train)` - TPOT-based regression

**Outputs:**
- Trained model (saved as pickle)
- Python script of best pipeline
- Feature importance dataframe and plot

### 4. Social Listening (social_listening_utils.py)

**Purpose:** Google search trends data collection

**Key Functions:**
- `get_search_trends(iso_geotag)` - Pull dengue-related search trends
  - Uses ISO 3166 location codes (e.g., "PH-00" for Philippines)
  - Returns trends for top 5 dengue-related searches

## INFORM Risk Framework

AEDES implements the INFORM risk model for disaster risk assessment:

**Risk Components:**
1. **Hazard & Exposure** - Environmental factors (NDVI, temperature, precipitation)
2. **Vulnerability** - Socioeconomic factors (population density, built-up areas)
3. **Lack of Coping Capacity** - Healthcare facility access

**Workflow:**
1. Extract features aligned with INFORM dimensions
2. Perform clustering (5 clusters by default)
3. Analyze cluster characteristics
4. Re-label clusters by risk level (1=lowest, 5=highest)
5. Visualize risk maps

## Development Workflow

### Installation

```bash
# Install package
pip install aedes

# Or install from source
pip install -r requirements.txt
pip install -e .
```

### Authentication Setup

**Google Earth Engine:**
```python
import aedes
aedes.remote_sensing_utils.authenticate()
aedes.remote_sensing_utils.initialize()
```

Sign up for GEE access: https://earthengine.google.com/signup/

### Typical Analysis Pipeline

1. **Define Area of Interest (AOI)**
   - Use https://boundingbox.klokantech.com/ for bounding box GeoJSON
   - Format: `[[[lon1,lat1], [lon2,lat2], [lon3,lat3], [lon4,lat4], [lon1,lat1]]]`

2. **Extract Satellite Data**
   ```python
   from aedes.remote_sensing_utils import *
   points = generate_random_ee_points(AOI, sample_points=50)
   df = get_satellite_measures_from_points(points, AOI, date_from='2017-07-01', date_to='2017-09-30')
   ```

3. **Reverse Geocode**
   ```python
   from aedes.osm_utils import reverse_geocode_points
   df = reverse_geocode_points(df)
   ```

4. **Add OSM Network Data**
   ```python
   from aedes.osm_utils import initialize_OSM_network, get_OSM_network_data
   network = initialize_OSM_network(AOI)
   final_df, amenities_df, count_distance_df = get_OSM_network_data(
       network, df, AOI, ['clinic', 'hospital', 'doctors'], 5, 5000, show_viz=True
   )
   ```

5. **Perform Risk Clustering**
   ```python
   from aedes.automl_utils import perform_clustering
   model = perform_clustering(final_df, n_clusters=5)
   final_df['labels'] = model.labels_
   ```

6. **Visualize Results**
   ```python
   vizo = visualize_on_map(final_df)
   ```

### Running Web Application

```bash
# Install streamlit
pip install streamlit

# Run app
streamlit run app.py
```

## Common Data Structures

### Satellite Data DataFrame Columns
- `longitude`, `latitude` - Coordinates
- `ndvi` - Vegetation index (-1 to 1)
- `ndwi` - Water index (-1 to 1)
- `ndbi` - Built-up index (-1 to 1)
- `aerosol_index` - Air quality measure
- `surface_temp` - Surface temperature (°C)
- `precipitation` - Precipitation rate
- `relative_humidity` - Humidity (%)
- `date` - Observation date

### OSM Network Data Columns
- `nearest_{amenity}_1` to `nearest_{amenity}_k` - Distances to k-nearest facilities
- `count_{amenity}_within_{radius}km` - Count within radius

## Code Style and Conventions

- **Naming:** Use snake_case for functions and variables
- **Docstrings:** Follow NumPy/SciPy documentation style
- **Data:** Primary data structure is pandas DataFrame
- **Coordinates:** Use WGS84 (EPSG:4326) - longitude, latitude order
- **Dates:** Use 'YYYY-MM-DD' format strings

## External Dependencies

**Required API Keys/Access:**
- Google Earth Engine account (for satellite data)
- Internet connection (for OSM and Nominatim)

**Rate Limits:**
- Nominatim: 1 request/second for reverse geocoding
- GEE: Subject to Google Earth Engine quotas

## Known Limitations

1. **GEE Authentication:** Requires manual browser-based authentication on first use
2. **Processing Time:** Large AOIs or many sample points can take significant time
3. **Data Availability:** Satellite data availability varies by location and date
4. **OSM Coverage:** Quality of OSM data varies by region

## Troubleshooting

**GEE Authentication Issues:**
- Ensure you've signed up at https://earthengine.google.com/signup/
- Re-run `authenticate()` if credentials expire

**Missing Satellite Data:**
- Check date range - some satellites have limited historical data
- Verify AOI coordinates are valid WGS84

**OSM Network Errors:**
- Ensure AOI is not too large (can cause memory issues)
- Check that amenity tags are valid OSM tags

## Testing

Currently no automated test suite. Testing is done through:
- Jupyter notebook examples in `demo.ipynb`
- Streamlit web application in `app.py`

## Model Artifacts

- ML models saved as `.pkl` files using `joblib`
- Best pipeline exported as Python script (see `best_aedes_model.py`)
- Feature importances saved as CSV and PNG

## Future Development

Potential enhancements:
- Add automated testing suite
- Support for additional satellite data sources
- Real-time data updates
- Integration with disease surveillance systems
- API endpoint for web services
