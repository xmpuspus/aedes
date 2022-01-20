import pandas as pd

import streamlit as st
import re

import aedes
from aedes.remote_sensing_utils import get_satellite_measures_from_AOI, reverse_geocode_points, reverse_geocode_points
from aedes.remote_sensing_utils import perform_clustering, visualize_on_map

from aedes.osm_utils import initialize_OSM_network, get_OSM_network_data

from streamlit_folium import folium_static

aedes.remote_sensing_utils.initialize()

st.title('AEDES: Predictive Geospatial Hostpot Detection')
st.write("""This web application demonstrates the use of satellite, weather and OpenStreetMap data to identify potential hotspots for vector-borne diseases. This web application only needs geojson input of an area of interest and then it automatically collects and models the data needed for hotspot detection at a longlat level.""")

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

satellite_df = get_satellite_measures_from_AOI(aoi_geojson, 25)

satellite_df['labels'] = perform_clustering(satellite_df, n_clusters=3)

rev_geocode_df = reverse_geocode_points(satellite_df)

mapper = visualize_on_map(satellite_df, ignore_labels=[1])

folium_static(mapper)

st.subheader('Suburbs/Locations in Risky Areas')

risk_df = pd.Series(rev_geocode_df[['address.suburb','address.city']]
                    .dropna()
                    .apply(lambda x: str(x[0] )+ ", " + str(x[1]), axis=1)
                    .value_counts()
                    .index).rename('Locations at Risk')

st.dataframe(risk_df)
