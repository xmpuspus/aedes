"""
AEDES Interactive Map Viewer - Backend API
Provides endpoints for satellite data retrieval based on user-drawn bounding boxes.
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path to import aedes
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import ee
    from aedes.remote_sensing_utils import (
        initialize,
        get_satellite_measures_from_points,
        generate_random_ee_points
    )
    GEE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import Earth Engine or AEDES: {e}")
    GEE_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__,
            static_folder='../frontend/static',
            template_folder='../frontend/templates')
CORS(app)

# Initialize Google Earth Engine
if GEE_AVAILABLE:
    try:
        initialize()
        logger.info("✓ Google Earth Engine initialized successfully")
    except Exception as e:
        logger.warning(f"⚠ GEE initialization failed: {e}")
        logger.info("Run 'earthengine authenticate' in terminal to set up credentials")
        GEE_AVAILABLE = False


def validate_bbox(bbox: List[List[float]]) -> bool:
    """Validate bounding box coordinates."""
    try:
        if not bbox or len(bbox) < 4:
            return False

        for point in bbox:
            if len(point) != 2:
                return False
            lon, lat = point
            if not (-180 <= lon <= 180):
                return False
            if not (-90 <= lat <= 90):
                return False

        return True
    except:
        return False


def validate_date(date_str: str) -> bool:
    """Validate date string format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except:
        return False


@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'gee_available': GEE_AVAILABLE,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/satellite-data', methods=['POST'])
def get_satellite_data():
    """
    Main endpoint to receive bounding box and return satellite data.

    Expected payload:
    {
        "bbox": [[lon1, lat1], [lon2, lat2], [lon3, lat3], [lon4, lat4], [lon1, lat1]],
        "date_from": "2024-01-01",
        "date_to": "2024-03-31",
        "sample_points": 20
    }

    Returns:
    {
        "success": true,
        "data": [...],
        "summary": {...}
    }
    """
    try:
        # Check if GEE is available
        if not GEE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Google Earth Engine is not available. Please authenticate first.'
            }), 503

        # Get request data
        data = request.json

        # Validate required fields
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        if 'bbox' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing bounding box (bbox)'
            }), 400

        # Extract and validate parameters
        bbox = data['bbox']
        date_from = data.get('date_from', '2024-01-01')
        date_to = data.get('date_to', '2024-03-31')
        sample_points = data.get('sample_points', 20)

        # Validate bbox
        if not validate_bbox(bbox):
            return jsonify({
                'success': False,
                'error': 'Invalid bounding box coordinates'
            }), 400

        # Validate dates
        if not validate_date(date_from) or not validate_date(date_to):
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400

        # Validate sample points
        if not isinstance(sample_points, int) or sample_points < 1 or sample_points > 100:
            return jsonify({
                'success': False,
                'error': 'Sample points must be between 1 and 100'
            }), 400

        logger.info(f"Processing request: {len(bbox)} points, {date_from} to {date_to}, {sample_points} samples")

        # Convert bbox to GEE-compatible format
        aoi_geojson = [bbox]

        # Generate random points in the area
        logger.info("Generating random points...")
        points = generate_random_ee_points(aoi_geojson, sample_points)

        # Get satellite data
        logger.info("Fetching satellite data from Google Earth Engine...")
        satellite_df = get_satellite_measures_from_points(
            points,
            aoi_geojson,
            date_from=date_from,
            date_to=date_to
        )

        # Check if we got data
        if satellite_df.empty:
            return jsonify({
                'success': False,
                'error': 'No data available for this area and time range'
            }), 404

        # Convert to JSON-serializable format
        # Drop geometry columns for JSON serialization
        columns_to_keep = [
            'longitude', 'latitude', 'ndvi', 'ndwi', 'ndbi', 'ndmi',
            'fapar', 'aerosol', 'surface_temperature',
            'precipitation_rate', 'relative_humidity'
        ]

        # Only keep columns that exist
        available_columns = [col for col in columns_to_keep if col in satellite_df.columns]
        data_df = satellite_df[available_columns]

        # Calculate summary statistics
        summary = {
            'points_analyzed': len(data_df),
            'date_range': f"{date_from} to {date_to}",
            'bbox': bbox
        }

        # Add statistics for each metric
        for col in ['ndvi', 'ndwi', 'ndbi', 'surface_temperature', 'precipitation_rate', 'relative_humidity']:
            if col in data_df.columns:
                values = data_df[col].dropna()
                if len(values) > 0:
                    summary[f'avg_{col}'] = float(values.mean())
                    summary[f'min_{col}'] = float(values.min())
                    summary[f'max_{col}'] = float(values.max())

        # Convert DataFrame to list of dicts
        data_records = data_df.to_dict('records')

        # Convert NaN to None for JSON serialization
        import math
        for record in data_records:
            for key, value in record.items():
                if isinstance(value, float) and math.isnan(value):
                    record[key] = None

        result = {
            'success': True,
            'data': data_records,
            'summary': summary
        }

        logger.info(f"✓ Successfully processed {len(data_records)} points")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/quick-test', methods=['GET'])
def quick_test():
    """
    Quick test endpoint with pre-defined coordinates (Quezon City, Philippines).
    Useful for testing without drawing on the map.
    """
    try:
        if not GEE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Google Earth Engine is not available'
            }), 503

        # Quezon City bounding box
        bbox = [
            [120.98976275, 14.58936896],
            [121.13383232, 14.58936896],
            [121.13383232, 14.77641364],
            [120.98976275, 14.77641364],
            [120.98976275, 14.58936896]
        ]

        # Use recent dates
        date_from = '2024-01-01'
        date_to = '2024-03-31'
        sample_points = 5

        # Process using the same logic as main endpoint
        aoi_geojson = [bbox]
        points = generate_random_ee_points(aoi_geojson, sample_points)
        satellite_df = get_satellite_measures_from_points(
            points,
            aoi_geojson,
            date_from=date_from,
            date_to=date_to
        )

        columns_to_keep = ['longitude', 'latitude', 'ndvi', 'ndwi', 'ndbi', 'surface_temperature']
        available_columns = [col for col in columns_to_keep if col in satellite_df.columns]
        data_df = satellite_df[available_columns]

        result = {
            'success': True,
            'data': data_df.to_dict('records'),
            'message': 'Quick test completed successfully',
            'location': 'Quezon City, Philippines'
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Quick test error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🛰️  AEDES Interactive Map Viewer - Backend Server")
    print("="*60)
    print(f"Google Earth Engine: {'✓ Available' if GEE_AVAILABLE else '✗ Not Available'}")
    print("\nEndpoints:")
    print("  GET  /                     - Main application")
    print("  GET  /api/health           - Health check")
    print("  POST /api/satellite-data   - Get satellite data")
    print("  GET  /api/quick-test       - Quick test endpoint")
    print("\nStarting server on http://localhost:5000")
    print("="*60 + "\n")

    app.run(debug=True, port=5000, host='0.0.0.0')
