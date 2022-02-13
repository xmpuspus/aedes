import pandas as pd
import folium

import ee

import geopandas as gpd

def authenticate():
    """
    Authenticate connection to the server
    Please see documentation for auth: https://developers.google.com/earth-engine/guides/python_install-conda#mac_6
    """
    
    ee.Authenticate()

def initialize():
    """
    Initialize connection to server
    """
    ee.Initialize()

def meanNDVICollection(img, aoi)->float:
    """
    NDVI = (NIR – Red) / (NIR + Red)
    Vegetation index for observe greenery.
    NDVI = -1 to 0 represent Water bodies
    NDVI = -0.1 to 0.1 represent Barren rocks, sand, or snow
    NDVI = 0.2 to 0.5 represent Shrubs and grasslands or senescing crops
    NDVI = 0.6 to 1.0 represent Dense vegetation or tropical rainforest
    """
    
    nir = img.select('SR_B5')
    red = img.select('SR_B4')
    
    ndviImage = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
    
    # Compute the mean of NDVI over the 'region'
    ndviValue = ndviImage.reduceRegion(**{
    'geometry': aoi.getInfo(),
    'reducer': ee.Reducer.mean(),
    'scale': 1000
    }).get('NDVI');  

    return ndviValue.getInfo()

def meanNDBICollection(img, aoi)->float:
    """
    Index for measuring built-up areas (buildings ,etc).
    NDBI values range from -1 to 1.
    Negative value of NDBI represent water bodies where as higher value represent build-up areas 
   
    """
    
    b5 = img.select('SR_B5')
    b6 = img.select('SR_B6')
    
    ndbiImage = b6.subtract(b5).divide(b6.add(b5)).rename('NDBI')
    
    # Compute the mean of NDBI over the 'region'
    ndbiValue = ndbiImage.reduceRegion(**{
    'geometry': aoi.getInfo(),
    'reducer': ee.Reducer.mean(),
    'scale': 1000
    }).get('NDBI');  

    return ndbiValue.getInfo()

def meanNDWICollection(img, aoi)->float:
    """
    Normalize Difference Water Index (NDWI) is use for the water bodies analysis.
    MNDWI = (Green – SWIR) / (Green + SWIR)
    Landsat 8 data, NDWI = (Band 3 – Band 6) / (Band 3 + Band 6)
    Normalize Difference Water Index (NDWI) value lies between -1 to 1. 
    Generally, water bodies NDWI value is greater than 0.5.
    """
    
    b3 = img.select('SR_B3')
    b6 = img.select('SR_B6')
    
    ndwiImage = b3.subtract(b6).divide(b3.add(b6)).rename('NDWI')
    
    # Compute the mean of NDWI over the 'region'
    ndwiValue = ndwiImage.reduceRegion(**{
    'geometry': aoi.getInfo(),
    'reducer': ee.Reducer.mean(),
    'scale': 1000
    }).get('NDWI'); 

    return ndwiValue.getInfo()

def meanNDMICollection(img, aoi)->float:
    """
    Normalized Difference Moisture Index (NDMI) is used to determine vegetation water content. 
    It is calculated as a ratio between the NIR and SWIR values in traditional fashion.
    In Landsat 8, NDMI = (Band 5 – Band 6) / (Band 5 + Band 6).
    """
    
    b5 = img.select('SR_B5')
    b6 = img.select('SR_B6')
    
    ndmiImage = b5.subtract(b6).divide(b5.add(b6)).rename('NDMI')
    
    # Compute the mean of NDMI over the 'region'
    ndmiValue = ndmiImage.reduceRegion(**{
    'geometry': aoi.getInfo(),
    'reducer': ee.Reducer.mean(),
    'scale': 1000
    }).get('NDMI'); 
    
    return ndmiValue.getInfo()

def meanfAPARCollection(img, aoi)->float:
    """
    The MCD15A3H V6 level 4, Combined Fraction of Photosynthetically Active Radiation (FPAR), 
    and Leaf Area Index (LAI) product is a 4-day composite data set with 500 meter pixel size. 
    The algorithm chooses the "best" pixel available from all the acquisitions of both MODIS sensors located on
    NASA's Terra and Aqua satellites from within the 4-day period.
    
    Range: min value is 0, max value is 100 with scale factor of 0.01.
    """
    
    fapar = img.select('Fpar')
    
    faparImage = fapar.rename('fapar')
    
    # Compute the mean of of precipitation over the 'region'
    faparValue = faparImage.reduceRegion(**{
    'geometry': aoi.getInfo(),
    'reducer': ee.Reducer.mean(),
    'scale': 1000
    }).get('fapar'); 

    try:
        return faparValue.getInfo() * 0.001
    except:
        return 0

def meanAirQualityCollection(img, aoi)->float:
    """
    Aerosol Index is a qualitative index indicating the presence of elevated layers of aerosols 
    with significant absorption. The main aerosol types that cause signals detected in the AI are desert dust, 
    biomass burning and volcanic ash plumes. 
    An advantage of the AI is that it can be derived for clear as well as (partly) cloudy ground pixels.
    """
    
    aerosol = img.select('SR_QA_AEROSOL')
    
    aerosolImage = aerosol.rename('aerosol')
    
    # Compute the mean of aerosol (air quality index) over the 'region'
    aerosolValue = aerosolImage.reduceRegion(**{
    'geometry': aoi.getInfo(),
    'reducer': ee.Reducer.mean(),
    'scale': 1000
    }).get('aerosol'); 

    return aerosolValue.getInfo()

def meanSurfaceTemperatureCollection(img, aoi)->float:
    """
    Provides daily land surface temperature (LST) and emissivity values in a 1200 x 1200 kilometer grid.
    Digital numbers range from 7500 to 65535 with a scale factor of 0.02 (converts to Kelvin)
    """
    
    surftemp = img.select('LST_Day_1km')
    
    surftempImage = surftemp.rename('surface_temperature')
    
    surftempValue = surftempImage.reduceRegion(**{
    'geometry': aoi.getInfo(),
    'reducer': ee.Reducer.mean(),
    'scale': 1000
    }).get('surface_temperature');  # result of reduceRegion is always a dictionary, so get the element we want

    try:
        return surftempValue.getInfo() * 0.02 - 273.15 # converting LST Digital Number to Deg Celsius
    except:
        return None


def meanPrecipitationCollection(img, aoi)->float:
    """
    Global Land Data Assimilation System (GLDAS) ingests satellite and ground-based observational data products. 
    Using advanced land surface modeling and data assimilation techniques, 
    it generates optimal fields of land surface states and fluxes.
    """
    
    precip = img.select('Rainf_f_tavg')
    
    precipImage = precip.rename('precipitation')
    
    # Compute the mean of of precipitation over the 'region'
    precipValue = precipImage.reduceRegion(**{
    'geometry': aoi.getInfo(),
    'reducer': ee.Reducer.mean(),
    'scale': 1000
    }).get('precipitation'); 

    return precipValue.getInfo()

def meanRelHumidityCollection(img, aoi)->float:
    """
    Global Land Data Assimilation System (GLDAS) ingests satellite and ground-based observational data products. 
    Using advanced land surface modeling and data assimilation techniques, 
    it generates optimal fields of land surface states and fluxes.
    Ranges from 0 to 100 (with estimation errors)
    """
    
    relative_humidity = img.expression(
      '0.263 * p * q * (exp(17.67 * (T - T0) / (T - 29.65))) ** -1', {
        'T': img.select('Tair_f_inst'),
        'T0': 273.16,
        'p': img.select('Psurf_f_inst'),
        'q': img.select('Qair_f_inst')
      }
    ).float().rename('relative_humidity')
    
    # Compute the mean of relative humidity over the 'region'
    relative_humidityValue = relative_humidity.reduceRegion(**{
    'geometry': aoi.getInfo(),
    'reducer': ee.Reducer.mean(),
    'scale': 1000
    }).get('relative_humidity'); 

    return relative_humidityValue.getInfo()


def df_to_ee_points(df, longitude='lon', latitude='lat'):
    """
    Converts a dataframe of long lat to Earth Engine-readable FeatureCollection object.
    """
    
    points = ee.FeatureCollection(df[[longitude, latitude]].apply(lambda x: ee.Geometry.Point(x[0], x[1]), axis=1).values.tolist())
    
    return points

def generate_random_ee_points(aoi_geojson, sample_points):
    """
    Given an area of interest geojson, create sample points within
    that bounding box returning an Earth Engine FeatureCollection object.
    """
    
    # setting the Area of Interest (AOI)
    AOI = ee.Geometry.Polygon(aoi_geojson)
    
    # Get more features of interest
    points = ee.FeatureCollection.randomPoints(AOI, sample_points)
    
    return points
    
def get_satellite_measures_from_points(points,
                           aoi_geojson, 
                           landsat_catalog='LANDSAT/LC08/C02/T1_L2',
                           modis_catalog = "MODIS/006/MOD11A1",
                           gldas_catalog = "NASA/GLDAS/V021/NOAH/G025/T3H",
                           date_from='2021-11-01', 
                           date_to='2021-12-31')->pd.DataFrame:
    """
    From a bounding box geojson, get normalized difference indices at different sample points.
    """
    # Landsat catalog (for normalized difference indices)
    landsat = ee.ImageCollection(landsat_catalog)
    
    # MODIS catalog (for surface temperature)
    modis = ee.ImageCollection(modis_catalog)
    
    # GLDAS catalog (for precipitation)
    gldas = ee.ImageCollection(gldas_catalog)
    
    # MODIS catalog (for fAPAR)
    modis_fpar = ee.ImageCollection("MODIS/006/MCD15A3H")
    
    # setting the Area of Interest (AOI)
    AOI = ee.Geometry.Polygon(aoi_geojson)

    # filter area and date
    landsat_AOI = landsat.filterBounds(AOI).filterDate(date_from, date_to)
    
    # Get satellite image with lowest cloud cover
    sat_image = ee.Image(landsat_AOI.sort('CLOUD_COVER').first())
    
    # filter area and date for MODIS
    modis_AOI = modis.filterBounds(AOI).filterDate(date_from, date_to)

    # Get satellite image for MODIS
    modis_sat_image = ee.Image(modis_AOI.median())
    
    # filter area and date for GLDAS
    gldas_AOI = gldas.filterBounds(AOI).filterDate(date_from, date_to)

    # Get satellite image for GLDAS
    gldas_sat_image = ee.Image(gldas_AOI.median())
    
    # filter area and date for MODIS FAPAR
    modis_fpar_AOI = modis_fpar.filterBounds(AOI).filterDate(date_from, date_to)

    # Get satellite image for MODIS FAPAR
    modis_fpar_sat_image = ee.Image(modis_fpar_AOI.median())
    
    # Function to get 1km patches of images from each point
    roi_with_buffer_fn = lambda geopoint: ee.Geometry.Point([geopoint.xy[0][0], geopoint.xy[1][0]]).buffer(1000)
    
    # Convert ee.geometry points to pandas dataframe and add 1km buffer around each point
    points_df = gpd.GeoDataFrame.from_features(points.getInfo()["features"])
    points_df['buffered_geometry'] = points_df['geometry'].apply(roi_with_buffer_fn)

    # Extract long lat
    points_df['longitude'] = points_df.geometry.apply(lambda g: g.x)
    points_df['latitude'] = points_df.geometry.apply(lambda g: g.y)

    # Get all normalized difference indices
    points_df['ndvi'] = points_df['buffered_geometry'].apply(lambda x: meanNDVICollection(sat_image, x))
    points_df['fapar'] = points_df['buffered_geometry'].apply(lambda x: meanfAPARCollection(modis_fpar_sat_image, x))
    points_df['ndbi'] = points_df['buffered_geometry'].apply(lambda x: meanNDBICollection(sat_image, x))
    points_df['ndwi'] = points_df['buffered_geometry'].apply(lambda x: meanNDWICollection(sat_image, x))
    points_df['ndmi'] = points_df['buffered_geometry'].apply(lambda x: meanNDMICollection(sat_image, x))
    points_df['aerosol'] = points_df['buffered_geometry'].apply(lambda x: meanAirQualityCollection(sat_image, x))
    points_df['surface_temperature'] = (points_df['buffered_geometry']
                                        .apply(lambda x: meanSurfaceTemperatureCollection(modis_sat_image, x)))
    points_df['precipitation_rate'] = (points_df['buffered_geometry']
                                        .apply(lambda x: meanPrecipitationCollection(gldas_sat_image, x)))
    points_df['relative_humidity'] = (points_df['buffered_geometry']
                                        .apply(lambda x: meanRelHumidityCollection(gldas_sat_image, x)))
    
    return points_df
    
def scale_factor(image):
  # scale factor for the MODIS MOD13Q1 product

  return image.multiply(0.0001).copyProperties(image, ['system:time_start'])


def get_time_series_ndvi_evi(geojson, date_from='2018-01-01', date_to='2021-12-31')->pd.DataFrame:
    """
    From geojson, start and end date, get time-seris NDVI and EVI
    """
    
    # Get AOI
    AOI = ee.Geometry.Polygon(geojson)
    
    # EVI and NDVI from MODIS NNASA
    catalog_to_use = 'MODIS/006/MOD13Q1' 
    
    # Define data range 
    date_range = ee.DateRange(date_from, date_to)
    
    # Get modis satellite image collection
    modis = ee.ImageCollection(catalog_to_use).filterDate(date_range)
    
    # select EVI, NDVI
    evi = modis.select('EVI')
    ndvi = modis.select('NDVI')
    
    # Mapping function to multiply by the scale factor
    scaled_evi = evi.map(scale_factor)
    scaled_ndvi = ndvi.map(scale_factor)
    
    # NDVI time series
    AOI_ndvi = chart.Image.series(**{'imageCollection': scaled_ndvi,
                                       'region': AOI,
                                       'reducer': ee.Reducer.mean(),
                                       'scale': 1000,
                                       'xProperty': 'system:time_start'})

    # EVI time series
    AOI_evi = chart.Image.series(**{'imageCollection': scaled_evi,
                                       'region': AOI,
                                       'reducer': ee.Reducer.mean(),
                                       'scale': 1000,
                                       'xProperty': 'system:time_start'})
    
    # concatenate NDVI and EVI indices
    vegetation_df = AOI_ndvi.dataframe
    vegetation_df['EVI'] = AOI_evi.dataframe['EVI']
    
    return vegetation_df

def visualize_on_map(points_df, ignore_labels=None, is_dark=True):
    """
    Visualize the clusters on the map using Folium
    Themese for TileLayer: https://deparkes.co.uk/2016/06/10/folium-map-tiles/
    """
    
    # Plot clusters
    viz_map = folium.Map(location=[points_df['latitude'].iloc[0],points_df['longitude'].iloc[0]], zoom_start=10)
    
    # Set to dark theme if toggled
    if is_dark:
        folium.TileLayer('cartodbdark_matter').add_to(viz_map)
    
    # if ignore_labels has input, remove them from unique labels
    if ignore_labels==None:
        unique_labels = list(range(1, points_df['labels'].max()+1))
    else:
        unique_labels = list(range(1, points_df['labels'].max()+1))
        unique_labels = [label for label in unique_labels if label not in ignore_labels]
    
    # set colors
    # colors = ['lightred', 'orange', 'red', 'darkred', 'lightblue', 'blue', 'darkblue',
    #           'green', 'purple',  'beige',  'darkgreen', 'cadetblue', 
    #           'darkpurple', 'white', 'pink', 'lightgreen', 
    #           'gray', 'black', 'lightgray']
    colors = ['white', 'pink', 'lightred', 'red', 'darkred', 'darkpurple', 'purple',
              'darkblue', 'blue', 'lightblue']
    
    for j in range(len(unique_labels)):
        for i in points_df[points_df['labels']==unique_labels[j]].index:
            folium.Marker(
            location = [points_df['latitude'].iloc[i], points_df['longitude'].iloc[i]],
            popup = points_df.iloc[i]['labels'],
            icon = folium.Icon(color=colors[j])
            ).add_to(viz_map)

    return viz_map
