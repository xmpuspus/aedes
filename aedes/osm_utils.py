"""
OpenStreetMap Utilities Module
Provides functions for OSM network analysis and reverse geocoding.
"""

import logging
from typing import Optional, List, Tuple, Dict, Any
import string
import random
import re

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

import pandana
from pandana.loaders import osm

import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from shapely.geometry import box

import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_geojson(aoi_geojson: List[List[List[float]]]) -> bool:
    """
    Validate GeoJSON format and coordinates.

    Args:
        aoi_geojson: GeoJSON polygon coordinates

    Returns:
        bool: True if valid

    Raises:
        ValueError: If GeoJSON is invalid
    """
    try:
        if not aoi_geojson or not isinstance(aoi_geojson, list):
            raise ValueError("GeoJSON must be a non-empty list")

        if len(aoi_geojson) < 1 or len(aoi_geojson[0]) < 1:
            raise ValueError("GeoJSON structure is invalid")

        # Validate coordinates
        for ring in aoi_geojson:
            for point in ring:
                if len(point) != 2:
                    raise ValueError(f"Invalid coordinate: {point}")
                lon, lat = point
                if not (-180 <= lon <= 180):
                    raise ValueError(f"Invalid longitude: {lon}")
                if not (-90 <= lat <= 90):
                    raise ValueError(f"Invalid latitude: {lat}")

        return True

    except Exception as e:
        logger.error(f"GeoJSON validation failed: {e}")
        raise ValueError(f"Invalid GeoJSON: {e}")


def initialize_OSM_network(aoi_geojson: List[List[List[float]]]) -> Optional[pandana.network.Network]:
    """
    Create an OSM network from a GeoJSON bounding box.

    Args:
        aoi_geojson: GeoJSON polygon coordinates [[lon, lat], ...]

    Returns:
        Pandana Network object or None if creation fails

    Raises:
        ValueError: If GeoJSON is invalid
        Exception: If network initialization fails
    """
    try:
        logger.info("Initializing OSM network...")

        # Validate input
        validate_geojson(aoi_geojson)

        # Convert GeoJSON to bbox format (lat_min, lon_min, lat_max, lon_max)
        # aoi_geojson[0][0] = [lon, lat] bottomleft
        # aoi_geojson[0][1] = [lon, lat] bottomright
        # aoi_geojson[0][2] = [lon, lat] topright
        # aoi_geojson[0][3] = [lon, lat] topleft

        lat_min = aoi_geojson[0][0][1]  # Bottom left lat
        lon_min = aoi_geojson[0][3][0]  # Top left lon
        lat_max = aoi_geojson[0][2][1]  # Top right lat
        lon_max = aoi_geojson[0][1][0]  # Bottom right lon

        aoi_csv = (lat_min, lon_min, lat_max, lon_max)

        logger.info(f"Fetching OSM network for bbox: {aoi_csv}")

        # Get network from OSM
        network = osm.pdna_network_from_bbox(*aoi_csv)

        logger.info(f"✓ OSM network created with {len(network.nodes_df)} nodes")
        return network

    except Exception as e:
        logger.error(f"Failed to initialize OSM network: {e}")
        raise


def node_query(aoi_csv: Tuple[float, float, float, float],
               amenity: str) -> Optional[pd.DataFrame]:
    """
    Query OSM nodes for a specific amenity type.

    Args:
        aoi_csv: Bounding box as (lat_min, lon_min, lat_max, lon_max)
        amenity: Amenity type (e.g., 'hospital', 'clinic', 'school')

    Returns:
        DataFrame of amenity nodes or None if query fails
    """
    try:
        # Sanitize amenity string
        if not re.match(r'^[a-zA-Z_]+$', amenity):
            logger.warning(f"Invalid amenity name: {amenity}")
            return None

        query = osm.node_query(*aoi_csv, tags=f'"amenity"="{amenity}"')
        logger.info(f"✓ Found {len(query)} {amenity} amenities")
        return query

    except Exception as e:
        logger.warning(f"Query failed for amenity '{amenity}': {e}")
        return None


def get_OSM_network_data(
    network: pandana.network.Network,
    df: pd.DataFrame,
    aoi_geojson: List[List[List[float]]],
    poi_amenities: List[str],
    num_pois: int,
    maxdist: float,
    show_viz: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Extract POI (Points of Interest) network data for sample points.

    Args:
        network: Pandana network object
        df: DataFrame with longitude and latitude columns
        aoi_geojson: Area of interest GeoJSON
        poi_amenities: List of amenities (e.g., ['clinic', 'hospital', 'doctors'])
        num_pois: Number of nearest POIs to find
        maxdist: Maximum distance in meters for search
        show_viz: Whether to display visualization

    Returns:
        Tuple of (final_df, amenities_df, count_distance_df)

    Raises:
        ValueError: If inputs are invalid
        Exception: If processing fails
    """
    try:
        logger.info(f"Processing OSM network data for {poi_amenities}...")

        # Validate inputs
        if 'longitude' not in df.columns or 'latitude' not in df.columns:
            raise ValueError("DataFrame must have 'longitude' and 'latitude' columns")

        if num_pois <= 0:
            raise ValueError("num_pois must be positive")

        if maxdist <= 0:
            raise ValueError("maxdist must be positive")

        validate_geojson(aoi_geojson)

        # Set AOI CSV from geojson
        lat_min = aoi_geojson[0][0][1]
        lon_min = aoi_geojson[0][3][0]
        lat_max = aoi_geojson[0][2][1]
        lon_max = aoi_geojson[0][1][0]
        aoi_csv = (lat_min, lon_min, lat_max, lon_max)

        # Get network ID per longlat pair of sampled points
        df = df.copy()  # Avoid modifying original
        df['OSM_network_id'] = network.get_node_ids(df['longitude'], df['latitude'])

        # Set category string
        category = f'all_{"_".join(poi_amenities)}'

        # Query node details for each amenity
        logger.info("Querying amenities...")
        amenities_dict = {}
        for amenity in poi_amenities:
            result = node_query(aoi_csv, amenity)
            if result is not None and not result.empty:
                amenities_dict[amenity] = result

        if not amenities_dict:
            logger.warning("No amenities found in the area")
            # Return empty dataframes
            empty_df = df.copy()
            return empty_df, pd.DataFrame(), pd.DataFrame()

        # Combine list of POIs into dataframe
        amenities_df = pd.concat(list(amenities_dict.values()))

        # Select relevant columns
        addr_cols = [col for col in amenities_df.columns if 'addr' in col]
        amenities_df = amenities_df[['lat', 'lon', 'amenity', 'name'] + addr_cols]

        logger.info(f"✓ Found {len(amenities_df)} total amenities")

        # Set POIs in network
        network.set_pois(
            category=category,
            maxdist=maxdist,
            maxitems=num_pois,
            x_col=amenities_df.lon,
            y_col=amenities_df.lat
        )

        # Calculate distances to nearest POIs
        logger.info("Calculating distances to nearest POIs...")
        results = network.nearest_pois(
            distance=maxdist,
            category=category,
            num_pois=num_pois
        )

        # Get distance of n nearest POIs
        distance_df = results.reset_index().rename(columns={'id': 'OSM_network_id'})
        distance_df = distance_df.merge(df[['OSM_network_id']], how='inner')
        distance_df.columns = ['OSM_network_id'] + [
            f'nearest_{"_".join(poi_amenities)}_{i}'
            for i in range(1, num_pois + 1)
        ]

        # Count of amenities around each node
        logger.info("Counting amenities within radius...")
        amenities_nodes = network.get_node_ids(amenities_df.lon, amenities_df.lat)

        # Set amenities nodes on the network
        network.set(amenities_nodes, name=category)

        # Count accessibility score
        accessibility = network.aggregate(
            distance=maxdist,
            type='count',
            name=category
        )

        # Count number of nearest POIs
        count_df = accessibility.reset_index().rename(columns={'id': 'OSM_network_id'})
        count_df = count_df.merge(df[['OSM_network_id']], how='inner')
        count_df.columns = [
            'OSM_network_id',
            f'count_{"_".join(poi_amenities)}_within_{maxdist / 1000.}km'
        ]

        # Merge count and distance
        count_distance_df = distance_df.merge(count_df)

        # Merge with final_df
        final_df = df.merge(count_distance_df)

        logger.info(f"✓ Network analysis complete for {len(final_df)} points")

        # Optional visualization
        if show_viz:
            try:
                fig, ax = plt.subplots(figsize=(10, 8))
                plt.title(f'Distribution of {"_".join(poi_amenities)} POIs ({maxdist / 1000.}km radius)')
                plt.scatter(
                    network.nodes_df.x,
                    network.nodes_df.y,
                    c=accessibility,
                    s=1,
                    cmap='Blues',
                    norm=matplotlib.colors.LogNorm()
                )
                plt.colorbar()
                plt.show()
            except Exception as e:
                logger.warning(f"Visualization failed: {e}")

        return final_df, amenities_df, count_distance_df

    except Exception as e:
        logger.error(f"Failed to get OSM network data: {e}")
        raise


def id_generator(size: int = 6, chars: str = string.ascii_uppercase + string.digits) -> str:
    """
    Generate a random ID string.

    Args:
        size: Length of ID
        chars: Characters to use

    Returns:
        Random ID string
    """
    return ''.join(random.choice(chars) for _ in range(size))


def sanitize_user_agent(user_agent: str) -> str:
    """
    Sanitize user agent string to prevent header injection.

    Args:
        user_agent: Raw user agent string

    Returns:
        Sanitized user agent string
    """
    # Remove any newlines or carriage returns
    sanitized = re.sub(r'[\r\n]', '', user_agent)
    # Limit length
    sanitized = sanitized[:100]
    # Only allow alphanumeric and basic punctuation
    sanitized = re.sub(r'[^a-zA-Z0-9\s\-_.]', '', sanitized)
    return sanitized if sanitized else 'aedes_client'


def reverse_geocode(
    lat: float,
    long: float,
    user_agent_string: str = 'geogeopypy'
) -> Optional[pd.DataFrame]:
    """
    Reverse geocode a lat/long coordinate.

    Args:
        lat: Latitude (-90 to 90)
        long: Longitude (-180 to 180)
        user_agent_string: User agent for API requests

    Returns:
        DataFrame with geocode details or None if geocoding fails

    Raises:
        ValueError: If coordinates are invalid
    """
    try:
        # Validate coordinates
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude: {lat}")
        if not (-180 <= long <= 180):
            raise ValueError(f"Invalid longitude: {long}")

        # Sanitize user agent
        user_agent = sanitize_user_agent(user_agent_string)

        locator = Nominatim(user_agent=user_agent, timeout=10)
        coordinates = f"{lat}, {long}"

        # Rate limited reverse geocode
        rgeocode = RateLimiter(locator.reverse, min_delay_seconds=1.0)  # Respect Nominatim rate limits
        location = rgeocode(coordinates)

        if location is None:
            logger.warning(f"No geocode result for {coordinates}")
            return None

        loc_details = location.raw
        loc_details_df = pd.json_normalize(loc_details)

        return loc_details_df

    except Exception as e:
        logger.error(f"Reverse geocode failed for ({lat}, {long}): {e}")
        return None


def reverse_geocode_points(
    df: pd.DataFrame,
    latitude: str = 'latitude',
    longitude: str = 'longitude'
) -> pd.DataFrame:
    """
    Reverse geocode all points in a DataFrame.

    Args:
        df: DataFrame with latitude and longitude columns
        latitude: Name of latitude column
        longitude: Name of longitude column

    Returns:
        DataFrame with concatenated geocode information

    Raises:
        ValueError: If required columns are missing
    """
    try:
        logger.info("Reverse geocoding points...")

        # Validate columns
        if latitude not in df.columns:
            raise ValueError(f"Column '{latitude}' not found in DataFrame")
        if longitude not in df.columns:
            raise ValueError(f"Column '{longitude}' not found in DataFrame")

        # Generate unique ID for this session
        id_str = id_generator()

        # Reverse geocode points
        geocode_results = []

        for idx, row in df.iterrows():
            result = reverse_geocode(
                row[latitude],
                row[longitude],
                user_agent_string=id_str
            )
            if result is not None:
                geocode_results.append(result)
            else:
                # Add empty result to maintain alignment
                geocode_results.append(pd.DataFrame())

            # Progress logging every 10 points
            if (idx + 1) % 10 == 0:
                logger.info(f"Geocoded {idx + 1}/{len(df)} points")

        # Concatenate results
        if geocode_results:
            points_rgeocode_df = pd.concat(geocode_results, ignore_index=True)

            # Concatenate to original df
            points_with_rgeo_df = pd.concat(
                [df.reset_index(drop=True), points_rgeocode_df],
                axis=1
            )

            logger.info(f"✓ Reverse geocoded {len(df)} points")
            return points_with_rgeo_df
        else:
            logger.warning("No geocode results obtained")
            return df

    except Exception as e:
        logger.error(f"Failed to reverse geocode points: {e}")
        raise


def reverse_geocode_center_of_geojson(aoi_geojson: List[List[List[float]]]) -> str:
    """
    Get address of the center of a GeoJSON area.

    Args:
        aoi_geojson: GeoJSON polygon coordinates

    Returns:
        Address string

    Raises:
        ValueError: If GeoJSON is invalid
    """
    try:
        logger.info("Reverse geocoding GeoJSON center...")

        # Validate GeoJSON
        validate_geojson(aoi_geojson)

        # Generate unique ID
        id_str = id_generator()

        # Initialize geolocator
        user_agent = sanitize_user_agent(id_str)
        geolocator = Nominatim(user_agent=user_agent, timeout=10)

        # Set bounds as polygon
        lat_min = aoi_geojson[0][0][1]
        lon_min = aoi_geojson[0][3][0]
        lat_max = aoi_geojson[0][2][1]
        lon_max = aoi_geojson[0][1][0]

        bounds = (lat_min, lon_min, lat_max, lon_max)
        polygon = box(*bounds)

        # Get centroid
        centroid_x = polygon.centroid.x
        centroid_y = polygon.centroid.y

        # Reverse geocode centroid
        reverse_geocode = geolocator.reverse(f"{centroid_y}, {centroid_x}")

        if reverse_geocode is None:
            logger.warning("Could not geocode center of GeoJSON")
            return f"Location at ({centroid_y:.4f}, {centroid_x:.4f})"

        logger.info(f"✓ Geocoded center: {reverse_geocode.address}")
        return reverse_geocode.address

    except Exception as e:
        logger.error(f"Failed to reverse geocode GeoJSON center: {e}")
        raise
