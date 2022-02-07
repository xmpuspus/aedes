import pandas as pd

import streamlit as st
import re

import aedes
from aedes.remote_sensing_utils import df_to_ee_points, generate_random_ee_points
from aedes.remote_sensing_utils import visualize_on_map, get_satellite_measures_from_points
from aedes.automl_utils import perform_clustering
from aedes.osm_utils import initialize_OSM_network, get_OSM_network_data, reverse_geocode_points, reverse_geocode_center_of_geojson

from streamlit_folium import folium_static

aedes.remote_sensing_utils.initialize()

st.title('AEDES: Predictive Geospatial Hostpot Detection')
st.write("""This web application demonstrates the use of satellite, weather and OpenStreetMap data to identify potential hotspots for vector-borne diseases. This web application only needs geojson input of an area of interest and then it automatically collects and models the data needed for hotspot detection at a longlat level.""")

st.subheader('Input Bounding Box Coordinates')

aoi_str = st.text_area("Input geojson of area of interest here", 
                             value=[[[120.98976275,14.58936896],
                                       [121.13383232,14.58936896],
                                       [121.13383232,14.77641364],
                                       [120.98976275,14.77641364],
                                       [120.98976275,14.58936896]]])

list_parsed = [float(re.findall("\d+\.\d+", num)[0]) for num in aoi_str.split(",")]

aoi_geojson = [[[list_parsed[0], list_parsed[1]],
              [list_parsed[2], list_parsed[3]],
              [list_parsed[4], list_parsed[5]],
              [list_parsed[6], list_parsed[7]],
              [list_parsed[8], list_parsed[9]]]]

st.subheader('Bounding Box Center')

st.write(f"Detect hotspots around {reverse_geocode_center_of_geojson(aoi_geojson)}...")

points = generate_random_ee_points(aoi_geojson, sample_points=20)

satellite_df = get_satellite_measures_from_points(points, aoi_geojson)

clustering_model = perform_clustering(satellite_df, n_clusters=3)
satellite_df['labels'] = pd.Series(clustering_model.labels_)

rev_geocode_df = reverse_geocode_points(satellite_df)

st.subheader('Detected Hotspots')

mapper = visualize_on_map(satellite_df, ignore_labels=[1])

folium_static(mapper)

st.subheader('Risky Locations')

indentified_risky_places_df = rev_geocode_df[rev_geocode_df['labels'].isin([0, 2])]

try:
    risk_df = indentified_risky_places_df[[i for i in rev_geocode_df.columns if 'address' in i]].fillna('').value_counts().reset_index().drop(0, axis=1)
    st.dataframe(risk_df)
except:
    st.write('OpenStreetMap returned no available data for each longitude-latitude pair.')
    
st.subheader('Top Villages at Risk')

try:
    risk_village_df = indentified_risky_places_df['address.village'].value_counts().reset_index().drop('address.village', axis=1).rename(columns={'index':'top_villages'})
    st.dataframe(risk_village_df)
except:
    st.write('OpenStreetMap returned no available data for suburbs.')  
    
st.subheader('Top Suburbs at Risk')

try:
    risk_suburb_df = indentified_risky_places_df['address.suburb'].value_counts().reset_index().drop('address.suburb', axis=1).rename(columns={'index':'top_suburbs'})
    st.dataframe(risk_suburb_df)
except:
    st.write('OpenStreetMap returned no available data for suburbs.')    

st.subheader('Top Cities at Risk')

try:
    risk_cities_df = indentified_risky_places_df['address.city'].value_counts().reset_index().drop('address.city', axis=1).rename(columns={'index':'top_cities'})
    st.dataframe(risk_cities_df)
except:
    st.write('OpenStreetMap returned no available data for cities.')

st.subheader('Top Postcodes at Risk')

try:
    risk_postcode_df = indentified_risky_places_df['address.postcode'].value_counts().reset_index().drop('address.postcode', axis=1).rename(columns={'index':'top_postcodes'})
    st.dataframe(risk_postcode_df)
except:
    st.write('OpenStreetMap returned no available data for postcodes.')

st.subheader('Top Regions at Risk')

try:
    risk_region_df = indentified_risky_places_df['address.region'].value_counts().reset_index().drop('address.region', axis=1).rename(columns={'index':'top_regions'})
    st.dataframe(risk_region_df)
except:
    st.write('OpenStreetMap returned no available data for region.')
