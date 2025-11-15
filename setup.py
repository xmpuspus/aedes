import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="aedes",
    packages=['aedes'],
    version="0.0.17",
    author="Xavier Puspus",
    author_email="xavier.puspus@cirrolytix.com",
    description="A python package for PROJECT AEDES - disease risk assessment using geospatial data and machine learning.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xmpuspus/aedes",
    install_requires=[
        'earthengine-api>=0.1.374',
        'folium>=0.14.0',
        'geopandas>=0.13.0',
        'geopy>=2.3.0',
        'matplotlib>=3.7.0',
        'pandas>=2.0.0',
        'scikit-learn>=1.3.0',
        'numpy>=1.24.0',
        'tpot>=0.12.0',
        'xgboost>=2.0.0',
        'pandana>=0.6.1',
        'osmnet>=0.1.6',
        'shapely>=2.0.0',
        'pytrends>=4.9.0',
        'streamlit>=1.28.0',
        'streamlit-folium>=0.15.0',
        'joblib>=1.3.0',
        'requests>=2.31.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.8.5',
)