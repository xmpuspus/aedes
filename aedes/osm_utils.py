import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import string
import random

import pandana
from pandana.loaders import osm

import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from shapely.geometry import box

import warnings
warnings.filterwarnings('ignore')

def initialize_OSM_network(aoi_geojson)->pandana.network.Network:
    """
    takes in a geojson and outputs an OSM network preprocessed by Pandana.
    """
    
    # Set AOI CSV from geojson
    aoi_csv = aoi_geojson[0][0][1], aoi_geojson[0][3][0], aoi_geojson[0][2][1], aoi_geojson[0][1][0]

    # Get network from geocsv
    network = osm.pdna_network_from_bbox(*aoi_csv)
    
    return network

def node_query(aoi_csv, amenity):
    """
    Perform OSM's node_query function with try catch, using input geocsv and the specific amenity to query.
    """
    
    try:
        query = osm.node_query(*aoi_csv, tags=f'"amenity"="{amenity}"')
        return query
    except:
        pass

def get_OSM_network_data(network, df, aoi_geojson, poi_amenities, num_pois, maxdist, show_viz=False):
    """
    Input
        network: Pandana network
        df: a dataframe of longitude and latitude
        aoi_gejson: geojson of bounding box
        poi_amenities: List of amenities
                     : Choose available amenities in this documentation: https://wiki.openstreetmap.org/wiki/Map_features#Amenity
        num_pois: integer, number of points of interest to map and perform contraction hierarchies
        maxdist: in meters, maximum distance to perform contraction hierarchies
        show_viz: boolean, shows viz of map containing information from contraction hierarchy operations
    Returns
        final_df: same dataframe with concatenated data from points of interest
        amenities_df: dataframe on amenities from POIs
        count_distance_df: dataframe of counts and distances of input df longlat to amenities POIs
    """
    
    # Set AOI CSV from geojson
    aoi_csv = aoi_geojson[0][0][1], aoi_geojson[0][3][0], aoi_geojson[0][2][1], aoi_geojson[0][1][0]
    
    # get network ID per longlat pair of sampled points
    df['OSM_network_id'] = network.get_node_ids(df['longitude'], df['latitude'])

    # Set category string
    category = f'all_{"_".join(poi_amenities)}'

    # query node details for each ammenity
    amenities_dict = {poi_amenities[i]:node_query(aoi_csv, poi_amenities[i]) for i in range(len(poi_amenities))}
#     amenities_dict = {poi_amenities[i]:osm.node_query(*aoi_csv, tags=f'"amenity"="{poi_amenities[i]}"') for i in range(len(poi_amenities))}

    # Combine list of POIs into dataframe
    amenities_df = pd.concat(list(amenities_dict.values()))
    amenities_df = amenities_df[['lat', 'lon', 'amenity', 'name',]+[i for i in amenities_df.columns if 'addr' in i]]

    # Set POIs in network
    network.set_pois(category = category,
                         maxdist = maxdist,
                         maxitems = num_pois,
                         x_col = amenities_df.lon, 
                         y_col = amenities_df.lat)

    # Calculate distances
    results = network.nearest_pois(distance = maxdist,
                                   category = category,
                                   num_pois = num_pois,
                                  # include_poi_ids = True
                                  )

    # Get distance of n nearest POIs
    distance_df = results.reset_index().rename(columns={'id':'OSM_network_id'}).merge(df[['OSM_network_id']])
    distance_df.columns = ['OSM_network_id'] + [f'nearest_{"_".join(poi_amenities)}_{i}' for i in range(1, num_pois+1)]

    # Count of healthcare establishments around each node
    amenities_nodes = network.get_node_ids(amenities_df.lon, amenities_df.lat)

    # Set amenities nodes on the network
    network.set(amenities_nodes, 
                name = category)

    # Count accessibility score for number of POIs within distance of each node
    accessibility = network.aggregate(distance = maxdist,
                                      type = 'count',
                                      name = category)

    # Count number of nearest POIs
    count_df = accessibility.reset_index().rename(columns={'id':'OSM_network_id'}).merge(df[['OSM_network_id']])
    count_df.columns = ['OSM_network_id', f'count_{"_".join(poi_amenities)}_within_{maxdist/1000.}km']

    # Merge count and distance
    count_distance_df = distance_df.merge(count_df)

    # Merge with final_df 
    final_df = df.merge(count_distance_df)

    if show_viz==True:
        fig, ax = plt.subplots(figsize=(10,8))

        plt.title(f'Distribution of {"_".join(poi_amenities)} Points of Interest ({maxdist/1000.}km radius)')
        plt.scatter(network.nodes_df.x, network.nodes_df.y, 
                    c=accessibility, s=1, cmap='Blues', 
                    norm=matplotlib.colors.LogNorm())
        cb = plt.colorbar()
        plt.show()
        
    return final_df, amenities_df, count_distance_df

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def reverse_geocode(lat, long, user_agent_string='geogeopypy')->pd.DataFrame:
    """
    Takes in latlong and outputs a dataframe containing geocode details.
    """
    
    locator = Nominatim(user_agent=user_agent_string)
    coordinates = f"{lat}, {long}"
    
    rgeocode = RateLimiter(locator.reverse, min_delay_seconds=0.001)
    loc_details = rgeocode(coordinates).raw
    loc_details_df = pd.json_normalize(loc_details)
    return loc_details_df

def reverse_geocode_points(df, latitude='latitude', longitude='longitude')->pd.DataFrame:
    """
    Takes in a dataframe with longitude and latitude, perfoms reverse geocode and outputs the same df
    with concatenated geocode information.
    """
    
    # set ID
    id_str = id_generator()
    
    # reverse geocode points 
    series = df[[latitude, longitude]].apply(lambda x: reverse_geocode(x[0], x[1], user_agent_string=id_str), axis=1)
    points_rgeocode_df = pd.concat(series.tolist())

    # concatenate to original df
    points_with_rgeo_df = pd.concat([df, points_rgeocode_df.reset_index()], axis=1)
    
    return points_with_rgeo_df

def reverse_geocode_center_of_geojson(aoi_geojson)->str:
    """
    Takes in a geojson and outputs an address.
    """
    
    # set ID
    id_str = id_generator()
    
    # Initialize geolocator
    geolocator = Nominatim(user_agent=id_str)
    
    # Set bounds as polygon
    bounds = aoi_geojson[0][0][1], aoi_geojson[0][3][0], aoi_geojson[0][2][1], aoi_geojson[0][1][0]
    polygon = box(*bounds)
    
    # reverse geocode aoi_csv 
    reverse_geocode = geolocator.reverse(", ".join([str(i) for i in [polygon.centroid.x, polygon.centroid.y]]))
    
    return reverse_geocode.address
