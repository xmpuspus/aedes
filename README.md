# AEDES

This repository contains codes that demonstrate the use of Project AEDES for data collection on remote sensing using LANDSAT, MODIS and SENTINEL.  

Author: Xavier Puspus  
Affiliation: [Cirrolytix Research Services](cirrolytix.com)

### Installation


Install using:

```console
foo@bar:~$ pip install aedes
```

Import the package using:

```
import aedes
from aedes.remote_sensing_utils import get_satellite_measures_from_AOI, reverse_geocode_points, reverse_geocode_points
from aedes.remote_sensing_utils import perform_clustering, visualize_on_map
```
### Authentication and Initialization
This packages uses Google Earth Engine (sign-up for access [here](https://earthengine.google.com/signup/)) to query remote sensing data. To authenticate, simply use:

```
aedes.remote_sensing_utils.authenticate()
```

This script will open a google authenticator that uses your email (provided you've signed up earlier) to authenticate your script to query remote sensing data. After authentication, initialize access using:

```
aedes.remote_sensing_utils.initialize()
```

### Area of Interest

First, find the bounding box geojson of an Area of Interest (AOI) of your choice using this [link](https://boundingbox.klokantech.com/).

![Bounding box example of Quezon City, Philippines](bbox.png)

### Get Normalized Difference Indices

Use the one-liner code `get_satellite_measures_from_AOI` to extract NDVI, NDWI, NDBI, Aerosol Index (Air Quality) and Surface Temperature for your preset number of points of interest `sample_points` within a specified date duration `date_from` to `date_to`.

```
%%time
QC_AOI = [[[120.98976275,14.58936896],
           [121.13383232,14.58936896],
           [121.13383232,14.77641364],
           [120.98976275,14.77641364],
           [120.98976275,14.58936896]]] # Quezon city

qc_df = get_satellite_measures_from_AOI(QC_AOI, 
                                              sample_points=200, 
                                              date_from='2017-07-01', 
                                              date_to='2017-09-30')
```

### Reverse Geocoding

This package also provides an easy-to-use one-liner reverse geocoder that uses [Nominatim](https://nominatim.org/)

```
%%time
rev_geocode_qc_df = reverse_geocode_points(qc_df)
rev_geocode_qc_df.head()
```

### Geospatial Clustering

This packages uses KMeans as the unsupervised learning technique of choice to perform clustering on the geospatial data enriched with normalized indices, air quality and surface temperatures with your chosen number of clusters.

```
rev_geocode_qc_df['labels'] = perform_clustering(rev_geocode_qc_df, 
                                     n_clusters=3)
```

### Visualize on a Map

This packages also provides the capability of visualizing all the points of interest with their proper labels using one line of code.

```
vizo = visualize_on_map(rev_geocode_qc_df)
vizo
```

![Hotspot detection example of Quezon City, Philippines](sample_hotspots.png)
