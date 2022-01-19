import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="aedes", # Replace with your own username
    packages=['aedes'],
    version="0.0.7",
    author="Xavier Puspus",
    author_email="xavier.puspus@cirrolytix.com",
    description="A package for PROJECT AEDES",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xmpuspus/aedes",
    install_requires=['earthengine_api==0.1.292',
                      'ee==0.4',
                      'folium==0.12.1.post1',
                      'geopandas==0.10.2',
                      'geopy==2.1.0',
                      'matplotlib==3.3.2',
                      'pandana==0.6.1',
                      'pandas==1.0.3',
                      'scikit_learn==1.0.2'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.5',
)