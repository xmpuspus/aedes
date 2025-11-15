"""
AEDES - Disease Risk Assessment Platform
A Python package for disease hotspot detection and risk assessment using
geospatial data, remote sensing, and machine learning.

Author: Xavier Puspus
Affiliation: Cirrolytix Research Services
"""

__version__ = "0.0.17"
__author__ = "Xavier Puspus"
__email__ = "xavier.puspus@cirrolytix.com"

# Import main modules to make them available at package level
try:
    from . import remote_sensing_utils
    from . import osm_utils
    from . import automl_utils
    from . import social_listening_utils
except ImportError as e:
    import warnings
    warnings.warn(f"Some AEDES modules could not be imported: {e}")

__all__ = [
    "remote_sensing_utils",
    "osm_utils",
    "automl_utils",
    "social_listening_utils"
]
