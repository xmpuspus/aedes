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
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.5',
)