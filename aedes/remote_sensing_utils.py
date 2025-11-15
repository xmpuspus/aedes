"""
Remote Sensing Utilities Module
Provides functions for satellite data retrieval and analysis using Google Earth Engine.
"""

import logging
from typing import Optional, Union, List, Tuple, Dict, Any
import pandas as pd
import folium
import ee
import geopandas as gpd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def authenticate() -> None:
    """
    Authenticate connection to Google Earth Engine.

    Raises:
        Exception: If authentication fails

    See: https://developers.google.com/earth-engine/guides/python_install-conda
    """
    try:
        logger.info("Authenticating with Google Earth Engine...")
        ee.Authenticate()
        logger.info("✓ Authentication successful")
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise


def initialize() -> None:
    """
    Initialize connection to Google Earth Engine server.

    Raises:
        Exception: If initialization fails
    """
    try:
        logger.info("Initializing Google Earth Engine...")
        ee.Initialize()
        logger.info("✓ Initialization successful")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise


def validate_aoi(aoi: Any) -> bool:
    """
    Validate Area of Interest geometry.

    Args:
        aoi: Earth Engine geometry or GeoJSON

    Returns:
        bool: True if valid

    Raises:
        ValueError: If AOI is invalid
    """
    try:
        if aoi is None:
            raise ValueError("AOI cannot be None")

        # Try to get info to validate it's a proper EE object
        if hasattr(aoi, 'getInfo'):
            aoi.getInfo()

        return True
    except Exception as e:
        logger.error(f"Invalid AOI: {e}")
        raise ValueError(f"Invalid AOI geometry: {e}")


def validate_ndvi_range(value: Optional[float]) -> Optional[float]:
    """Validate NDVI value is in valid range [-1, 1]."""
    if value is None:
        return None
    if not isinstance(value, (int, float)):
        logger.warning(f"NDVI value is not numeric: {value}")
        return None
    if value < -1 or value > 1:
        logger.warning(f"NDVI value {value} outside valid range [-1, 1]")
        return None
    return float(value)


def meanNDVICollection(img: ee.Image, aoi: ee.Geometry) -> Optional[float]:
    """
    Calculate mean NDVI (Normalized Difference Vegetation Index) for an area.

    NDVI = (NIR – Red) / (NIR + Red)

    Interpretation:
        -1 to 0:    Water bodies
        -0.1 to 0.1: Barren rocks, sand, or snow
        0.2 to 0.5:  Shrubs, grasslands, or senescing crops
        0.6 to 1.0:  Dense vegetation or tropical rainforest

    Args:
        img: Landsat 8 Earth Engine image
        aoi: Area of interest geometry

    Returns:
        Mean NDVI value or None if calculation fails
    """
    try:
        validate_aoi(aoi)

        nir = img.select('SR_B5')
        red = img.select('SR_B4')

        ndviImage = nir.subtract(red).divide(nir.add(red)).rename('NDVI')

        ndviValue = ndviImage.reduceRegion(**{
            'geometry': aoi.getInfo(),
            'reducer': ee.Reducer.mean(),
            'scale': 1000,
            'maxPixels': 1e9
        }).get('NDVI')

        result = ndviValue.getInfo()
        return validate_ndvi_range(result)

    except Exception as e:
        logger.error(f"NDVI calculation failed: {e}")
        return None


def meanNDBICollection(img: ee.Image, aoi: ee.Geometry) -> Optional[float]:
    """
    Calculate mean NDBI (Normalized Difference Built-up Index).

    Index for measuring built-up areas (buildings, etc).

    Range: -1 to 1
        Negative values: Water bodies
        Higher values: Built-up areas

    Args:
        img: Landsat 8 Earth Engine image
        aoi: Area of interest geometry

    Returns:
        Mean NDBI value or None if calculation fails
    """
    try:
        validate_aoi(aoi)

        b5 = img.select('SR_B5')
        b6 = img.select('SR_B6')

        ndbiImage = b6.subtract(b5).divide(b6.add(b5)).rename('NDBI')

        ndbiValue = ndbiImage.reduceRegion(**{
            'geometry': aoi.getInfo(),
            'reducer': ee.Reducer.mean(),
            'scale': 1000,
            'maxPixels': 1e9
        }).get('NDBI')

        result = ndbiValue.getInfo()
        return validate_ndvi_range(result)  # Same range as NDVI

    except Exception as e:
        logger.error(f"NDBI calculation failed: {e}")
        return None


def meanNDWICollection(img: ee.Image, aoi: ee.Geometry) -> Optional[float]:
    """
    Calculate mean NDWI (Normalized Difference Water Index).

    Used for water bodies analysis.
    MNDWI = (Green – SWIR) / (Green + SWIR)

    For Landsat 8: NDWI = (Band 3 – Band 6) / (Band 3 + Band 6)

    Range: -1 to 1
        > 0.5: Water bodies

    Args:
        img: Landsat 8 Earth Engine image
        aoi: Area of interest geometry

    Returns:
        Mean NDWI value or None if calculation fails
    """
    try:
        validate_aoi(aoi)

        b3 = img.select('SR_B3')
        b6 = img.select('SR_B6')

        ndwiImage = b3.subtract(b6).divide(b3.add(b6)).rename('NDWI')

        ndwiValue = ndwiImage.reduceRegion(**{
            'geometry': aoi.getInfo(),
            'reducer': ee.Reducer.mean(),
            'scale': 1000,
            'maxPixels': 1e9
        }).get('NDWI')

        result = ndwiValue.getInfo()
        return validate_ndvi_range(result)

    except Exception as e:
        logger.error(f"NDWI calculation failed: {e}")
        return None


def meanNDMICollection(img: ee.Image, aoi: ee.Geometry) -> Optional[float]:
    """
    Calculate mean NDMI (Normalized Difference Moisture Index).

    Used to determine vegetation water content.
    Calculated as ratio between NIR and SWIR.

    For Landsat 8: NDMI = (Band 5 – Band 6) / (Band 5 + Band 6)

    Args:
        img: Landsat 8 Earth Engine image
        aoi: Area of interest geometry

    Returns:
        Mean NDMI value or None if calculation fails
    """
    try:
        validate_aoi(aoi)

        b5 = img.select('SR_B5')
        b6 = img.select('SR_B6')

        ndmiImage = b5.subtract(b6).divide(b5.add(b6)).rename('NDMI')

        ndmiValue = ndmiImage.reduceRegion(**{
            'geometry': aoi.getInfo(),
            'reducer': ee.Reducer.mean(),
            'scale': 1000,
            'maxPixels': 1e9
        }).get('NDMI')

        result = ndmiValue.getInfo()
        return validate_ndvi_range(result)

    except Exception as e:
        logger.error(f"NDMI calculation failed: {e}")
        return None


def meanfAPARCollection(img: ee.Image, aoi: ee.Geometry) -> Optional[float]:
    """
    Calculate mean fAPAR (Fraction of Absorbed Photosynthetically Active Radiation).

    The MCD15A3H V6 level 4 product is a 4-day composite with 500m pixel size.

    Range: 0 to 100 with scale factor of 0.01

    Args:
        img: MODIS Earth Engine image
        aoi: Area of interest geometry

    Returns:
        Mean fAPAR value (scaled) or None if calculation fails
    """
    try:
        validate_aoi(aoi)

        fapar = img.select('Fpar')
        faparImage = fapar.rename('fapar')

        faparValue = faparImage.reduceRegion(**{
            'geometry': aoi.getInfo(),
            'reducer': ee.Reducer.mean(),
            'scale': 1000,
            'maxPixels': 1e9
        }).get('fapar')

        result = faparValue.getInfo()
        if result is not None:
            return float(result) * 0.001
        return 0.0

    except Exception as e:
        logger.error(f"fAPAR calculation failed: {e}")
        return 0.0


def meanAirQualityCollection(img: ee.Image, aoi: ee.Geometry) -> Optional[float]:
    """
    Calculate mean Aerosol Index (air quality indicator).

    Aerosol Index indicates presence of elevated layers of aerosols with
    significant absorption. Main types: desert dust, biomass burning, volcanic ash.

    Advantage: Can be derived for clear as well as cloudy ground pixels.

    Args:
        img: Landsat 8 Earth Engine image
        aoi: Area of interest geometry

    Returns:
        Mean aerosol value or None if calculation fails
    """
    try:
        validate_aoi(aoi)

        aerosol = img.select('SR_QA_AEROSOL')
        aerosolImage = aerosol.rename('aerosol')

        aerosolValue = aerosolImage.reduceRegion(**{
            'geometry': aoi.getInfo(),
            'reducer': ee.Reducer.mean(),
            'scale': 1000,
            'maxPixels': 1e9
        }).get('aerosol')

        result = aerosolValue.getInfo()
        return float(result) if result is not None else None

    except Exception as e:
        logger.error(f"Air quality calculation failed: {e}")
        return None


def meanSurfaceTemperatureCollection(img: ee.Image, aoi: ee.Geometry) -> Optional[float]:
    """
    Calculate mean land surface temperature (LST).

    Provides daily LST and emissivity in a 1200 x 1200 km grid.
    Digital numbers: 7500 to 65535 with scale factor of 0.02 (converts to Kelvin)

    Args:
        img: MODIS Earth Engine image
        aoi: Area of interest geometry

    Returns:
        Mean surface temperature in Celsius or None if calculation fails
    """
    try:
        validate_aoi(aoi)

        surftemp = img.select('LST_Day_1km')
        surftempImage = surftemp.rename('surface_temperature')

        surftempValue = surftempImage.reduceRegion(**{
            'geometry': aoi.getInfo(),
            'reducer': ee.Reducer.mean(),
            'scale': 1000,
            'maxPixels': 1e9
        }).get('surface_temperature')

        result = surftempValue.getInfo()
        if result is not None:
            # Convert LST Digital Number to Degrees Celsius
            celsius = float(result) * 0.02 - 273.15
            return round(celsius, 2)
        return None

    except Exception as e:
        logger.error(f"Surface temperature calculation failed: {e}")
        return None


def meanPrecipitationCollection(img: ee.Image, aoi: ee.Geometry) -> Optional[float]:
    """
    Calculate mean precipitation rate.

    Uses GLDAS (Global Land Data Assimilation System) which ingests
    satellite and ground-based observational data products.

    Args:
        img: GLDAS Earth Engine image
        aoi: Area of interest geometry

    Returns:
        Mean precipitation rate or None if calculation fails
    """
    try:
        validate_aoi(aoi)

        precip = img.select('Rainf_f_tavg')
        precipImage = precip.rename('precipitation')

        precipValue = precipImage.reduceRegion(**{
            'geometry': aoi.getInfo(),
            'reducer': ee.Reducer.mean(),
            'scale': 1000,
            'maxPixels': 1e9
        }).get('precipitation')

        result = precipValue.getInfo()
        return float(result) if result is not None else None

    except Exception as e:
        logger.error(f"Precipitation calculation failed: {e}")
        return None


def meanRelHumidityCollection(img: ee.Image, aoi: ee.Geometry) -> Optional[float]:
    """
    Calculate mean relative humidity.

    Uses GLDAS data with advanced land surface modeling.

    Range: 0 to 100 (with estimation errors)

    Args:
        img: GLDAS Earth Engine image
        aoi: Area of interest geometry

    Returns:
        Mean relative humidity percentage or None if calculation fails
    """
    try:
        validate_aoi(aoi)

        relative_humidity = img.expression(
            '0.263 * p * q * (exp(17.67 * (T - T0) / (T - 29.65))) ** -1',
            {
                'T': img.select('Tair_f_inst'),
                'T0': 273.16,
                'p': img.select('Psurf_f_inst'),
                'q': img.select('Qair_f_inst')
            }
        ).float().rename('relative_humidity')

        relative_humidityValue = relative_humidity.reduceRegion(**{
            'geometry': aoi.getInfo(),
            'reducer': ee.Reducer.mean(),
            'scale': 1000,
            'maxPixels': 1e9
        }).get('relative_humidity')

        result = relative_humidityValue.getInfo()
        if result is not None:
            # Clamp to valid range
            return max(0.0, min(100.0, float(result)))
        return None

    except Exception as e:
        logger.error(f"Relative humidity calculation failed: {e}")
        return None


def df_to_ee_points(df: pd.DataFrame,
                    longitude: str = 'lon',
                    latitude: str = 'lat') -> ee.FeatureCollection:
    """
    Convert DataFrame with coordinates to Earth Engine FeatureCollection.

    Args:
        df: DataFrame containing longitude and latitude columns
        longitude: Name of longitude column
        latitude: Name of latitude column

    Returns:
        Earth Engine FeatureCollection

    Raises:
        ValueError: If required columns are missing or coordinates are invalid
    """
    try:
        if longitude not in df.columns:
            raise ValueError(f"Column '{longitude}' not found in DataFrame")
        if latitude not in df.columns:
            raise ValueError(f"Column '{latitude}' not found in DataFrame")

        # Validate coordinates
        if not df[longitude].between(-180, 180).all():
            raise ValueError("Longitude values must be between -180 and 180")
        if not df[latitude].between(-90, 90).all():
            raise ValueError("Latitude values must be between -90 and 90")

        points = ee.FeatureCollection(
            df[[longitude, latitude]].apply(
                lambda x: ee.Geometry.Point(x[0], x[1]),
                axis=1
            ).values.tolist()
        )

        logger.info(f"✓ Converted {len(df)} points to EE FeatureCollection")
        return points

    except Exception as e:
        logger.error(f"Failed to convert DataFrame to EE points: {e}")
        raise


def generate_random_ee_points(aoi_geojson: List[List[List[float]]],
                              sample_points: int) -> ee.FeatureCollection:
    """
    Generate random points within an Area of Interest.

    Args:
        aoi_geojson: GeoJSON polygon coordinates
        sample_points: Number of random points to generate

    Returns:
        Earth Engine FeatureCollection of random points

    Raises:
        ValueError: If inputs are invalid
    """
    try:
        if sample_points <= 0:
            raise ValueError("sample_points must be positive")
        if sample_points > 5000:
            logger.warning(f"Generating {sample_points} points may be slow")

        AOI = ee.Geometry.Polygon(aoi_geojson)
        validate_aoi(AOI)

        points = ee.FeatureCollection.randomPoints(AOI, sample_points)

        logger.info(f"✓ Generated {sample_points} random points")
        return points

    except Exception as e:
        logger.error(f"Failed to generate random points: {e}")
        raise


def validate_date_range(date_from: str, date_to: str) -> Tuple[str, str]:
    """
    Validate and parse date range.

    Args:
        date_from: Start date in YYYY-MM-DD format
        date_to: End date in YYYY-MM-DD format

    Returns:
        Tuple of validated dates

    Raises:
        ValueError: If dates are invalid
    """
    try:
        # Basic validation
        from datetime import datetime

        d_from = datetime.strptime(date_from, '%Y-%m-%d')
        d_to = datetime.strptime(date_to, '%Y-%m-%d')

        if d_from > d_to:
            raise ValueError("date_from must be before date_to")

        # Check if dates are too far in the past
        if d_from.year < 2013:  # Landsat 8 launch year
            logger.warning(f"Date {date_from} is before Landsat 8 launch (2013)")

        return date_from, date_to

    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise


def get_satellite_measures_from_points(
    points: ee.FeatureCollection,
    aoi_geojson: List[List[List[float]]],
    landsat_catalog: str = 'LANDSAT/LC08/C02/T1_L2',
    modis_catalog: str = "MODIS/006/MOD11A1",
    gldas_catalog: str = "NASA/GLDAS/V021/NOAH/G025/T3H",
    date_from: str = '2021-11-01',
    date_to: str = '2021-12-31'
) -> pd.DataFrame:
    """
    Extract satellite measures (NDVI, NDWI, NDBI, weather data) for sample points.

    Args:
        points: Earth Engine FeatureCollection of points
        aoi_geojson: Area of interest GeoJSON
        landsat_catalog: Landsat collection ID
        modis_catalog: MODIS collection ID
        gldas_catalog: GLDAS collection ID
        date_from: Start date (YYYY-MM-DD)
        date_to: End date (YYYY-MM-DD)

    Returns:
        DataFrame with satellite measurements for each point

    Raises:
        ValueError: If inputs are invalid
        Exception: If data retrieval fails
    """
    try:
        logger.info(f"Fetching satellite data from {date_from} to {date_to}...")

        # Validate dates
        date_from, date_to = validate_date_range(date_from, date_to)

        # Initialize catalogs
        landsat = ee.ImageCollection(landsat_catalog)
        modis = ee.ImageCollection(modis_catalog)
        gldas = ee.ImageCollection(gldas_catalog)
        modis_fpar = ee.ImageCollection("MODIS/006/MCD15A3H")

        # Set AOI
        AOI = ee.Geometry.Polygon(aoi_geojson)
        validate_aoi(AOI)

        # Filter Landsat data
        landsat_AOI = landsat.filterBounds(AOI).filterDate(date_from, date_to)
        sat_image = ee.Image(landsat_AOI.sort('CLOUD_COVER').first())

        # Filter MODIS data
        modis_AOI = modis.filterBounds(AOI).filterDate(date_from, date_to)
        modis_sat_image = ee.Image(modis_AOI.median())

        # Filter GLDAS data
        gldas_AOI = gldas.filterBounds(AOI).filterDate(date_from, date_to)
        gldas_sat_image = ee.Image(gldas_AOI.median())

        # Filter MODIS FAPAR data
        modis_fpar_AOI = modis_fpar.filterBounds(AOI).filterDate(date_from, date_to)
        modis_fpar_sat_image = ee.Image(modis_fpar_AOI.median())

        # Function to get 1km buffer patches
        def roi_with_buffer_fn(geopoint):
            return ee.Geometry.Point([geopoint.xy[0][0], geopoint.xy[1][0]]).buffer(1000)

        # Convert EE points to pandas DataFrame
        logger.info("Converting points to GeoDataFrame...")
        points_df = gpd.GeoDataFrame.from_features(points.getInfo()["features"])

        if points_df.empty:
            raise ValueError("No points found in the specified area")

        points_df['buffered_geometry'] = points_df['geometry'].apply(roi_with_buffer_fn)

        # Extract coordinates
        points_df['longitude'] = points_df.geometry.apply(lambda g: g.x)
        points_df['latitude'] = points_df.geometry.apply(lambda g: g.y)

        # Calculate indices with progress logging
        logger.info("Calculating NDVI...")
        points_df['ndvi'] = points_df['buffered_geometry'].apply(
            lambda x: meanNDVICollection(sat_image, x)
        )

        logger.info("Calculating fAPAR...")
        points_df['fapar'] = points_df['buffered_geometry'].apply(
            lambda x: meanfAPARCollection(modis_fpar_sat_image, x)
        )

        logger.info("Calculating NDBI...")
        points_df['ndbi'] = points_df['buffered_geometry'].apply(
            lambda x: meanNDBICollection(sat_image, x)
        )

        logger.info("Calculating NDWI...")
        points_df['ndwi'] = points_df['buffered_geometry'].apply(
            lambda x: meanNDWICollection(sat_image, x)
        )

        logger.info("Calculating NDMI...")
        points_df['ndmi'] = points_df['buffered_geometry'].apply(
            lambda x: meanNDMICollection(sat_image, x)
        )

        logger.info("Calculating aerosol index...")
        points_df['aerosol'] = points_df['buffered_geometry'].apply(
            lambda x: meanAirQualityCollection(sat_image, x)
        )

        logger.info("Calculating surface temperature...")
        points_df['surface_temperature'] = points_df['buffered_geometry'].apply(
            lambda x: meanSurfaceTemperatureCollection(modis_sat_image, x)
        )

        logger.info("Calculating precipitation rate...")
        points_df['precipitation_rate'] = points_df['buffered_geometry'].apply(
            lambda x: meanPrecipitationCollection(gldas_sat_image, x)
        )

        logger.info("Calculating relative humidity...")
        points_df['relative_humidity'] = points_df['buffered_geometry'].apply(
            lambda x: meanRelHumidityCollection(gldas_sat_image, x)
        )

        logger.info(f"✓ Successfully extracted data for {len(points_df)} points")

        return points_df

    except Exception as e:
        logger.error(f"Failed to extract satellite measures: {e}")
        raise


def scale_factor(image: ee.Image) -> ee.Image:
    """
    Apply scale factor for MODIS MOD13Q1 product.

    Args:
        image: MODIS image

    Returns:
        Scaled image
    """
    return image.multiply(0.0001).copyProperties(image, ['system:time_start'])


def get_time_series_ndvi_evi(geojson: List[List[List[float]]],
                              date_from: str = '2018-01-01',
                              date_to: str = '2021-12-31') -> pd.DataFrame:
    """
    Get time-series NDVI and EVI from MODIS data.

    Args:
        geojson: GeoJSON polygon coordinates
        date_from: Start date
        date_to: End date

    Returns:
        DataFrame with NDVI and EVI time series

    Raises:
        Exception: If data retrieval fails
    """
    try:
        logger.info(f"Fetching NDVI/EVI time series from {date_from} to {date_to}...")

        # Validate dates
        date_from, date_to = validate_date_range(date_from, date_to)

        AOI = ee.Geometry.Polygon(geojson)
        validate_aoi(AOI)

        catalog_to_use = 'MODIS/006/MOD13Q1'
        date_range = ee.DateRange(date_from, date_to)

        modis = ee.ImageCollection(catalog_to_use).filterDate(date_range)

        evi = modis.select('EVI')
        ndvi = modis.select('NDVI')

        scaled_evi = evi.map(scale_factor)
        scaled_ndvi = ndvi.map(scale_factor)

        # Note: chart module not available in standard ee package
        # This function needs additional dependencies or refactoring
        logger.warning("Time series charting requires additional setup")

        # Placeholder return
        return pd.DataFrame()

    except Exception as e:
        logger.error(f"Failed to get time series: {e}")
        raise


def visualize_on_map(points_df: pd.DataFrame,
                     ignore_labels: Optional[List[int]] = None,
                     is_dark: bool = True) -> folium.Map:
    """
    Visualize risk clusters on an interactive map.

    Args:
        points_df: DataFrame with latitude, longitude, and labels columns
        ignore_labels: List of label values to exclude from visualization
        is_dark: Use dark theme if True

    Returns:
        Folium map object

    Raises:
        ValueError: If required columns are missing
    """
    try:
        # Validate required columns
        required_cols = ['latitude', 'longitude', 'labels']
        missing_cols = [col for col in required_cols if col not in points_df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        if points_df.empty:
            raise ValueError("DataFrame is empty")

        # Create base map
        center_lat = points_df['latitude'].iloc[0]
        center_lon = points_df['longitude'].iloc[0]
        viz_map = folium.Map(location=[center_lat, center_lon], zoom_start=10)

        # Set dark theme if requested
        if is_dark:
            folium.TileLayer('cartodbdark_matter').add_to(viz_map)

        # Determine labels to display
        if ignore_labels is None:
            unique_labels = list(range(1, int(points_df['labels'].max()) + 1))
        else:
            unique_labels = [
                label for label in range(1, int(points_df['labels'].max()) + 1)
                if label not in ignore_labels
            ]

        # Color scheme (white to dark red for increasing risk)
        colors = [
            'white', 'pink', 'lightred', 'red', 'darkred',
            'darkpurple', 'purple', 'darkblue', 'blue', 'lightblue'
        ]

        # Add markers for each label group
        for j, label in enumerate(unique_labels):
            label_points = points_df[points_df['labels'] == label]
            color = colors[j % len(colors)]

            for i in label_points.index:
                folium.Marker(
                    location=[label_points['latitude'].iloc[i], label_points['longitude'].iloc[i]],
                    popup=f"Risk Level: {label}",
                    icon=folium.Icon(color=color)
                ).add_to(viz_map)

        logger.info(f"✓ Created map with {len(points_df)} points")
        return viz_map

    except Exception as e:
        logger.error(f"Failed to create visualization: {e}")
        raise
