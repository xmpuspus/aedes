import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

import pandana
from pandana.loaders import osm

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
    amenities_dict = {poi_amenities[i]:osm.node_query(*aoi_csv, tags=f'"amenity"="{poi_amenities[i]}"') for i in range(len(poi_amenities))}

    # Combine list of POIs into dataframe
    amenities_df = pd.concat(list(amenities_dict.values()))[['lat', 'lon', 'amenity', 'addr:city', 'addr:street', 'name', 'addr:province',
                                              'addr:town', 'addr:housenumber', 'addr:municipality']]

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
