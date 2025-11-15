# AEDES Modernization Plan
## Comprehensive Roadmap for Modernizing Disease Risk Assessment Platform

**Document Version:** 1.0
**Date:** November 2025
**Prepared for:** AEDES Project

---

## Executive Summary

This document outlines a comprehensive modernization strategy for the AEDES disease risk assessment platform, incorporating cutting-edge technologies, datasets, and generative AI capabilities available in 2025. The plan transforms AEDES from a research-oriented Python package into a production-ready, scalable, AI-powered geospatial analytics platform.

### Key Modernization Pillars

1. **Cloud-Native Geospatial Architecture** - Scalable, distributed processing
2. **Advanced AI/ML Integration** - Deep learning, foundation models, and LLMs
3. **Real-Time Data Pipelines** - Streaming satellite and sensor data
4. **Modern MLOps & DevOps** - Automated deployment, monitoring, and retraining
5. **Generative AI Integration** - Natural language insights and automated analysis
6. **Enhanced Data Sources** - Multi-modal data fusion and new datasets

---

## 1. Satellite Data & Remote Sensing Modernization

### Current State
- **Technology:** Google Earth Engine (GEE) with manual authentication
- **Satellites:** Landsat 8, MODIS, GLDAS, Sentinel-2
- **Processing:** Sequential, single-threaded Python loops
- **Format:** Traditional raster formats via GEE API

### Modernization Strategy

#### 1.1 Expand Satellite Data Sources

**Add Modern Constellations:**
- **Sentinel-2 L2A** (10m resolution, near-real-time) - Already available in GEE but use Scene Classification Layer
- **Planet Labs** - Daily 3m resolution imagery (requires commercial license)
- **Maxar/WorldView** - Sub-meter imagery for urban areas
- **GOES-16/17** - 5-minute updates for weather monitoring
- **Sentinel-5P TROPOMI** - Enhanced air quality monitoring (NO2, SO2, CO)
- **NASA VIIRS** - Nighttime lights as urbanization proxy
- **Sentinel-1 SAR** - Weather-independent monitoring

**New Indices & Products:**
- **Enhanced Vegetation Index (EVI)** - Better in dense vegetation
- **Soil Adjusted Vegetation Index (SAVI)** - For sparse vegetation
- **Urban Heat Island Index** - Derived from thermal bands
- **Land Surface Water Index (LSWI)** - Improved water body detection
- **Built-up Index variations** - IBI, UI for urbanization

#### 1.2 Cloud-Native Geospatial Formats

**Migrate to:**
- **Cloud-Optimized GeoTIFF (COG)** - HTTP range requests, partial reads
- **Zarr** - Chunked, compressed N-dimensional arrays
- **Parquet/GeoParquet** - Columnar vector data
- **STAC (SpatioTemporal Asset Catalog)** - Standardized metadata

**Benefits:**
- 10-100x faster data access
- Reduced bandwidth and storage costs
- Enable distributed processing

**Implementation:**
```python
# Modern approach using stackstac + Xarray
import stackstac
import pystac_client
import xarray as xr

# Search STAC catalog
catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=bbox,
    datetime="2024-01-01/2024-12-31"
)

# Load as Xarray with dask for lazy loading
stack = stackstac.stack(search.items(), bounds=bbox)
ndvi = (stack.sel(band="nir") - stack.sel(band="red")) / \
       (stack.sel(band="nir") + stack.sel(band="red"))
```

#### 1.3 Processing Infrastructure

**Replace Sequential Processing with:**

**Option A: Dask + Xarray**
- Lazy evaluation and chunked processing
- Scales from laptop to cluster
- Native integration with cloud storage

```python
import dask.distributed
from dask_gateway import Gateway

# Connect to Dask cluster
gateway = Gateway()
cluster = gateway.new_cluster()
client = cluster.get_client()

# Process in parallel
result = ndvi.compute()  # Automatically parallelized
```

**Option B: Google Earth Engine Code Editor Migration**
- Use Python `ee` API with `eemont` and `geemap` libraries
- Server-side processing (no data download needed)
- Better for large-scale analysis

```python
import ee
import eemont
import geemap

# Authenticate once with service account
ee.Initialize(credentials=credentials)

# Time series analysis with eemont
s2 = (ee.ImageCollection('COPERNICUS/S2_SR')
      .filterBounds(aoi)
      .filterDate('2024-01-01', '2024-12-31')
      .maskClouds()  # eemont extension
      .scaleAndOffset()  # eemont extension
      .spectralIndices(['NDVI', 'NDWI', 'NDBI']))  # eemont extension
```

**Option C: Microsoft Planetary Computer**
- Free tier for research
- STAC catalog with global datasets
- Jupyter Hub for cloud processing

#### 1.4 Real-Time Satellite Monitoring

**Implement Event-Driven Architecture:**
- Subscribe to Sentinel Hub or Planet webhook notifications
- Trigger analysis when new imagery available
- Daily updates instead of historical analysis

**Technology Stack:**
- **Sentinel Hub** - Process API for on-demand processing
- **AWS SNS/SQS** - Event notification
- **Lambda/Cloud Functions** - Serverless processing

---

## 2. Machine Learning & AI Modernization

### Current State
- **AutoML:** TPOT (genetic algorithm, limited to sklearn)
- **Clustering:** Basic KMeans
- **Features:** Manual feature engineering
- **Deployment:** Pickle files, no versioning

### Modernization Strategy

#### 2.1 Modern AutoML Frameworks

**Replace TPOT with:**

**Option A: AutoGluon (Recommended)**
- State-of-art performance (Kaggle winning models)
- Supports tabular, time series, vision, text
- Automatic ensemble stacking
- GPU acceleration

```python
from autogluon.tabular import TabularPredictor

# Train with one line
predictor = TabularPredictor(label='risk_label', eval_metric='f1')
predictor.fit(
    train_data=df,
    time_limit=3600,  # 1 hour
    presets='best_quality',
    num_bag_folds=5,
    num_stack_levels=2
)

# Automatic feature engineering, model selection, and ensembling
predictions = predictor.predict(test_data)
leaderboard = predictor.leaderboard(df)  # Compare all models
```

**Option B: H2O AutoML**
- Distributed processing
- Explainable AI built-in
- AutoML + traditional ML

**Option C: FLAML (Microsoft)**
- Low computational cost
- Fast tuning
- Good for production

#### 2.2 Deep Learning for Spatiotemporal Prediction

**Integrate Deep Learning Models:**

**A. Convolutional LSTM for Time Series**
```python
import torch
import torch.nn as nn

class SpatioTemporalLSTM(nn.Module):
    """Predict disease risk from satellite time series"""
    def __init__(self, input_channels, hidden_dim, num_layers):
        super().__init__()
        self.conv_lstm = ConvLSTM(
            input_dim=input_channels,
            hidden_dim=hidden_dim,
            kernel_size=(3, 3),
            num_layers=num_layers
        )
        self.classifier = nn.Conv2d(hidden_dim, num_classes, 1)

    def forward(self, x):
        # x: (batch, time, channels, height, width)
        lstm_out, _ = self.conv_lstm(x)
        risk_map = self.classifier(lstm_out[:, -1])  # Last time step
        return risk_map
```

**B. Graph Neural Networks for Spatial Dependencies**
```python
import torch_geometric as pyg

class DiseaseRiskGNN(nn.Module):
    """Model spatial correlations between locations"""
    def __init__(self, num_features, hidden_dim):
        super().__init__()
        self.conv1 = pyg.nn.GCNConv(num_features, hidden_dim)
        self.conv2 = pyg.nn.GCNConv(hidden_dim, hidden_dim)
        self.classifier = nn.Linear(hidden_dim, 5)  # 5 risk levels

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        x = F.relu(self.conv2(x, edge_index))
        return self.classifier(x)
```

**C. Transformer Models for Multi-Modal Fusion**
```python
from transformers import AutoModel

class MultiModalRiskPredictor(nn.Module):
    """Combine satellite imagery, weather, and social data"""
    def __init__(self):
        super().__init__()
        self.image_encoder = timm.create_model('resnet50', pretrained=True)
        self.tabular_encoder = nn.Sequential(
            nn.Linear(num_tabular_features, 256),
            nn.ReLU(),
            nn.Linear(256, 128)
        )
        self.fusion = nn.MultiheadAttention(embed_dim=128, num_heads=8)
        self.classifier = nn.Linear(128, num_classes)
```

#### 2.3 Foundation Models for Geospatial AI

**Leverage Pre-trained Geospatial Models:**

**A. Prithvi (IBM/NASA Foundation Model)**
- Pre-trained on Harmonized Landsat-Sentinel (HLS) data
- Fine-tune for disease risk assessment

```python
from prithvi import PrithviModel

# Load pre-trained foundation model
model = PrithviModel.from_pretrained('ibm-nasa-geospatial/Prithvi-100M')

# Fine-tune on disease risk data
model.fine_tune(
    train_data=disease_risk_dataset,
    num_epochs=50,
    learning_rate=1e-4
)

# Extract embeddings for downstream tasks
embeddings = model.encode(satellite_imagery)
```

**B. SatMAE/SatCLIP**
- Self-supervised learning on satellite imagery
- Zero-shot classification capabilities

**C. Clay Foundation Model**
- Spatio-temporal modeling
- Multi-sensor fusion

#### 2.4 Advanced Clustering & Segmentation

**Replace KMeans with:**

**A. HDBSCAN**
- Hierarchical density-based clustering
- Automatic cluster number detection
- Better for irregular shapes

```python
import hdbscan

clusterer = hdbscan.HDBSCAN(
    min_cluster_size=10,
    min_samples=5,
    metric='haversine',  # Great circle distance
    cluster_selection_method='eom'
)
labels = clusterer.fit_predict(geospatial_features)
```

**B. Spatially Constrained Clustering**
```python
from sklearn.cluster import AgglomerativeClustering
from libpysal.weights import KNN

# Enforce spatial contiguity
w = KNN.from_dataframe(gdf, k=8)
model = AgglomerativeClustering(
    n_clusters=5,
    connectivity=w.sparse
)
```

**C. Deep Clustering**
```python
from torch_geometric.nn import DMoN

# Differentiable clustering with GNNs
cluster_model = DMoN(hidden_channels=64, num_clusters=5)
```

---

## 3. Generative AI Integration

### Current State
- No AI-powered insights
- Manual interpretation required
- Static reports

### Modernization Strategy

#### 3.1 Large Language Models for Analysis

**A. Automated Insight Generation**

```python
from anthropic import Anthropic
import json

class AIAnalyst:
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def generate_risk_report(self, risk_data, satellite_data, amenities_data):
        """Generate comprehensive risk assessment report"""

        prompt = f"""You are an epidemiologist analyzing disease risk data.

Satellite Data Summary:
- NDVI (vegetation): {satellite_data['ndvi'].describe().to_dict()}
- Surface Temperature: {satellite_data['surface_temperature'].describe().to_dict()}
- Precipitation: {satellite_data['precipitation_rate'].describe().to_dict()}

Risk Clusters Identified: {risk_data['labels'].value_counts().to_dict()}

Healthcare Facilities:
- Hospitals within 5km: {amenities_data['count_hospital_within_5km'].mean():.1f} (avg)

Generate a comprehensive risk assessment report including:
1. Key environmental risk factors
2. Areas of highest concern (with specific locations)
3. Actionable recommendations for public health officials
4. Resource allocation priorities
5. Temporal trends and seasonal considerations

Format the output as a structured markdown report."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

# Usage
analyst = AIAnalyst()
report = analyst.generate_risk_report(risk_df, satellite_df, amenities_df)
print(report)
```

**B. Natural Language Querying**

```python
class NLQueryEngine:
    """Ask questions in natural language about disease risk"""

    def query(self, question: str, context_data: dict):
        """
        Examples:
        - "Which areas have high dengue risk and low healthcare access?"
        - "What are the environmental conditions in cluster 3?"
        - "Compare risk levels between urban and rural areas"
        """

        # Convert data to structured format
        data_summary = self._prepare_context(context_data)

        prompt = f"""You are a geospatial data analyst. Use the following data to answer the question.

Data Available:
{json.dumps(data_summary, indent=2)}

Question: {question}

Provide a data-driven answer with specific metrics and locations."""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text
```

#### 3.2 Vision-Language Models for Satellite Imagery

**A. Automatic Imagery Description**

```python
from anthropic import Anthropic
import base64

class SatelliteImageAnalyzer:
    def analyze_satellite_image(self, image_path: str, location: str):
        """Describe what the satellite image reveals about disease risk"""

        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": f"""Analyze this satellite image of {location} for disease risk factors.

Identify:
1. Standing water bodies (mosquito breeding sites)
2. Vegetation density and type
3. Urban vs rural characteristics
4. Potential environmental risk factors
5. Changes that indicate increased disease risk

Provide specific observations with coordinates if possible."""
                    }
                ]
            }]
        )

        return message.content[0].text
```

**B. Change Detection Narratives**

```python
def generate_change_narrative(before_img, after_img, location):
    """Generate narrative explaining temporal changes"""

    # Multi-image analysis
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "data": before_img}},
                {"type": "text", "text": "BEFORE (6 months ago)"},
                {"type": "image", "source": {"type": "base64", "data": after_img}},
                {"type": "text", "text": f"AFTER (current)\n\nDescribe the environmental changes in {location} and their implications for disease risk."}
            ]
        }]
    )

    return message.content[0].text
```

#### 3.3 Code Generation for Custom Analyses

**A. Generate Analysis Scripts from Natural Language**

```python
class AnalysisCodeGenerator:
    def generate_analysis_code(self, request: str, available_data: dict):
        """
        Example: "Create a correlation matrix between NDVI and dengue cases,
                 then plot a time series for the top 5 risky areas"
        """

        prompt = f"""You are a Python data scientist. Generate code to perform this analysis:

Request: {request}

Available data:
- DataFrames: {list(available_data.keys())}
- Columns: {available_data}

Generate complete, runnable Python code using pandas, matplotlib, seaborn, and geopandas.
Include error handling and comments."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract code from response
        code = self._extract_code_blocks(message.content[0].text)
        return code

    def execute_safely(self, code: str, data_context: dict):
        """Execute generated code in sandboxed environment"""
        # Use restricted exec or container for safety
        exec_globals = {
            'pd': pd,
            'plt': plt,
            'sns': sns,
            **data_context
        }
        exec(code, exec_globals)
```

#### 3.4 Multimodal RAG for Domain Knowledge

**A. Retrieval-Augmented Generation for Epidemiology**

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import VoyageAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

class EpidemiologyRAG:
    def __init__(self):
        # Index scientific papers, WHO reports, CDC guidelines
        self.vectorstore = self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Index epidemiology research and guidelines"""
        documents = [
            # Load from:
            # - PubMed papers on dengue
            # - WHO dengue guidelines
            # - Historical outbreak data
            # - Climate-disease studies
        ]

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)

        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=VoyageAIEmbeddings()
        )
        return vectorstore

    def answer_with_citations(self, question: str, current_data: dict):
        """Answer questions using both literature and current analysis"""

        # Retrieve relevant papers
        docs = self.vectorstore.similarity_search(question, k=5)
        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = f"""You are an epidemiology expert. Answer the question using:

1. Scientific literature (provided below)
2. Current analysis data

Scientific Context:
{context}

Current Data:
{json.dumps(current_data, indent=2)}

Question: {question}

Provide an evidence-based answer with citations."""

        # Call Claude with extended context
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text
```

---

## 4. Enhanced Data Sources & Integration

### Current State
- Satellite data only
- Google Trends (limited)
- No real-time data
- No disease surveillance integration

### Modernization Strategy

#### 4.1 Climate & Weather Data

**Add Real-Time Weather APIs:**

```python
# OpenWeatherMap API - Real-time + 7-day forecast
import requests

class WeatherDataCollector:
    def get_current_weather(self, lat, lon):
        """Real-time weather for disease risk modeling"""
        response = requests.get(
            f"https://api.openweathermap.org/data/3.0/onecall",
            params={
                'lat': lat,
                'lon': lon,
                'appid': API_KEY,
                'exclude': 'minutely'
            }
        )

        data = response.json()
        return {
            'temperature': data['current']['temp'],
            'humidity': data['current']['humidity'],
            'precipitation': data['daily'][0]['rain'],
            'forecast_7day': data['daily'][:7]
        }

# NASA POWER API - Historical climate data
from nasapower import get_data

climate_data = get_data(
    lat=14.5,
    lon=121.0,
    start='2020-01-01',
    end='2024-12-31',
    parameters=['T2M', 'PRECTOTCORR', 'RH2M', 'ALLSKY_SFC_SW_DWN']
)
```

**Climate Model Projections:**
- **CMIP6 Data** - Future climate scenarios
- **CHIRPS** - Precipitation estimates
- **ERA5** - High-resolution reanalysis data

#### 4.2 Social Media & Digital Epidemiology

**A. Twitter/X Analysis for Disease Mentions**

```python
import tweepy
from textblob import TextBlob

class SocialListeningEngine:
    def collect_disease_mentions(self, location, radius_km, disease='dengue'):
        """Real-time social media monitoring"""

        # Twitter API v2
        tweets = self.client.search_recent_tweets(
            query=f"{disease} -is:retweet",
            geo=f"{location},{radius_km}km",
            max_results=100,
            tweet_fields=['created_at', 'geo', 'public_metrics']
        )

        # Sentiment analysis
        sentiments = []
        for tweet in tweets.data:
            analysis = TextBlob(tweet.text)
            sentiments.append({
                'text': tweet.text,
                'sentiment': analysis.sentiment.polarity,
                'created_at': tweet.created_at,
                'location': tweet.geo
            })

        return pd.DataFrame(sentiments)

    def detect_outbreak_signals(self, tweets_df):
        """Early warning from social media"""
        # Spike detection in mentions
        # Cluster geographic concentrations
        # Alert on anomalies
        pass
```

**B. Reddit/Community Forums Mining**

```python
import praw

reddit = praw.Reddit(client_id=..., client_secret=..., user_agent=...)

def mine_community_health_discussions(location):
    """Extract health concerns from community forums"""
    subreddit = reddit.subreddit('philippines')  # Location-specific

    posts = subreddit.search(
        f"dengue OR fever OR mosquito {location}",
        time_filter='month',
        limit=100
    )

    # NLP analysis on comments
    return analyze_health_concerns(posts)
```

#### 4.3 Mobile Phone Data

**A. Mobility Data (Aggregated & Anonymized)**

```python
# Integration with Google Community Mobility Reports
import pandas as pd

def get_mobility_trends(location, date_range):
    """Human mobility patterns affecting disease spread"""

    # Google COVID-19 Community Mobility Reports (updated for general use)
    mobility_df = pd.read_csv(
        'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv',
        parse_dates=['date']
    )

    location_data = mobility_df[
        (mobility_df['country_region'] == location) &
        (mobility_df['date'].between(date_range[0], date_range[1]))
    ]

    return location_data[[
        'retail_and_recreation_percent_change_from_baseline',
        'parks_percent_change_from_baseline',
        'residential_percent_change_from_baseline'
    ]]
```

**B. Safegraph/Cuebiq Data (Commercial)**
- Points of Interest visits
- Device density maps
- Movement patterns

#### 4.4 Disease Surveillance Integration

**A. WHO Disease Outbreak News API**

```python
def get_who_outbreak_data(disease, region):
    """Official disease outbreak reports"""

    # WHO DON RSS feed
    response = requests.get('https://www.who.int/rss-feeds/disease-outbreak-news')

    # Parse and filter
    outbreaks = parse_who_feed(response.content)

    return outbreaks[
        (outbreaks['disease'] == disease) &
        (outbreaks['region'] == region)
    ]
```

**B. ProMED-mail Integration**

```python
from bs4 import BeautifulSoup

def scrape_promed_alerts(disease='dengue'):
    """Early outbreak detection from ProMED"""
    url = f"https://promedmail.org/ajax/search.php?keyword={disease}"
    # Parse alerts and extract structured data
    return parse_promed_alerts(url)
```

**C. Local Health Department APIs**
- CDC Wonder API
- Philippines DOH Data
- Local surveillance systems

#### 4.5 Environmental & Infrastructure Data

**A. Water Infrastructure**

```python
from owslib.wfs import WebFeatureService

def get_water_infrastructure(bbox):
    """Water systems, drainage, sewage - breeding sites"""

    # OpenStreetMap Overpass API
    query = f"""
    [out:json];
    (
      way["natural"="water"]({bbox});
      way["waterway"]({bbox});
      way["man_made"="wastewater_plant"]({bbox});
    );
    out geom;
    """

    response = requests.post(
        'https://overpass-api.de/api/interpreter',
        data={'data': query}
    )

    return gpd.GeoDataFrame.from_features(response.json()['elements'])
```

**B. Air Quality Sensors**

```python
from pywaqi import WAQI

def get_air_quality_realtime(lat, lon):
    """Real-time AQI from sensor networks"""

    waqi = WAQI(api_key)
    station = waqi.get_coordinate_observation(lat, lon)

    return {
        'aqi': station['aqi'],
        'pm25': station['iaqi']['pm25']['v'],
        'pm10': station['iaqi']['pm10']['v'],
        'no2': station['iaqi']['no2']['v']
    }
```

#### 4.6 Socioeconomic Data

**A. Census & Demographics**

```python
import cenpy

def get_demographic_data(bbox):
    """Population density, age structure, income"""

    # US Census API (adapt for other countries)
    connection = cenpy.remote.APIConnection('ACSDT5Y2022')

    data = connection.query(
        cols=['B01001_001E', 'B19013_001E'],  # Population, Median Income
        geo_unit='tract',
        geo_filter={'state': '06', 'county': '*'}
    )

    return data
```

**B. WorldPop / Meta Population Density**

```python
import rasterio

def get_population_density(bbox):
    """High-resolution population data"""

    # Meta High Resolution Settlement Layer (HRSL)
    # WorldPop 100m resolution

    with rasterio.open('hdx_population_density.tif') as src:
        pop_density = src.read(1, window=bbox)

    return pop_density
```

---

## 5. Modern Architecture & Infrastructure

### Current State
- Monolithic Python package
- Local execution only
- No API layer
- Manual deployment

### Modernization Strategy

#### 5.1 Microservices Architecture

**Service Decomposition:**

```
aedes-platform/
├── services/
│   ├── satellite-ingestion/      # Fetch and process satellite data
│   ├── weather-service/          # Real-time weather integration
│   ├── ml-inference/             # Model serving
│   ├── social-listening/         # Social media monitoring
│   ├── risk-assessment/          # Core risk calculation
│   ├── reporting-service/        # AI-powered report generation
│   └── api-gateway/              # Unified API
├── infrastructure/
│   ├── terraform/                # IaC for cloud resources
│   ├── kubernetes/               # K8s manifests
│   └── docker/                   # Container definitions
└── frontend/
    ├── dashboard/                # React/Next.js dashboard
    └── mobile/                   # React Native app
```

#### 5.2 API Development (FastAPI)

**Modern REST API:**

```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import asyncio

app = FastAPI(
    title="AEDES Risk Assessment API",
    version="2.0.0",
    description="AI-powered disease risk assessment platform"
)

class RiskAssessmentRequest(BaseModel):
    aoi_geojson: list
    date_from: str
    date_to: str
    sample_points: int = 50
    include_forecast: bool = True

class RiskAssessmentResponse(BaseModel):
    risk_zones: list
    insights: str  # AI-generated
    confidence_score: float
    recommendations: list
    visualizations: dict

@app.post("/api/v2/assess-risk", response_model=RiskAssessmentResponse)
async def assess_disease_risk(
    request: RiskAssessmentRequest,
    background_tasks: BackgroundTasks
):
    """
    Comprehensive risk assessment endpoint

    - Fetches satellite data
    - Runs ML models
    - Generates AI insights
    - Returns actionable recommendations
    """

    # Async data collection
    satellite_task = asyncio.create_task(
        get_satellite_data(request.aoi_geojson, request.date_from, request.date_to)
    )
    weather_task = asyncio.create_task(
        get_weather_data(request.aoi_geojson)
    )
    social_task = asyncio.create_task(
        get_social_listening_data(request.aoi_geojson)
    )

    # Wait for all data
    satellite_data, weather_data, social_data = await asyncio.gather(
        satellite_task, weather_task, social_task
    )

    # ML inference
    risk_prediction = await ml_model.predict(
        satellite_data, weather_data, social_data
    )

    # AI-powered insights
    insights = await ai_analyst.generate_insights(
        risk_prediction, satellite_data, weather_data
    )

    # Background task: Save to database, send alerts
    background_tasks.add_task(
        save_assessment_results,
        risk_prediction,
        request.aoi_geojson
    )

    return RiskAssessmentResponse(
        risk_zones=risk_prediction['zones'],
        insights=insights,
        confidence_score=risk_prediction['confidence'],
        recommendations=generate_recommendations(risk_prediction)
    )

@app.get("/api/v2/realtime-monitoring/{location_id}")
async def realtime_monitoring(location_id: str):
    """WebSocket endpoint for live updates"""
    # Stream real-time weather, social media mentions, sensor data
    pass

@app.post("/api/v2/query")
async def natural_language_query(question: str, context: str):
    """Natural language querying with LLMs"""
    response = await nlquery_engine.query(question, context)
    return {"answer": response}
```

**GraphQL Alternative:**

```python
import strawberry
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class RiskZone:
    id: str
    coordinates: list[float]
    risk_level: int
    confidence: float
    factors: list[str]

@strawberry.type
class Query:
    @strawberry.field
    async def risk_zones(
        self,
        bbox: list[float],
        date_range: str
    ) -> list[RiskZone]:
        """Flexible querying of risk data"""
        return await fetch_risk_zones(bbox, date_range)

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")
```

#### 5.3 Containerization & Orchestration

**Docker Compose for Local Development:**

```yaml
version: '3.8'

services:
  api:
    build: ./services/api-gateway
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/aedes
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
      - ml-service

  ml-service:
    build: ./services/ml-inference
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - ./models:/models

  satellite-ingestion:
    build: ./services/satellite-ingestion
    environment:
      - GEE_SERVICE_ACCOUNT_JSON=/secrets/gee-key.json
      - AWS_S3_BUCKET=aedes-satellite-data
    volumes:
      - ./secrets:/secrets

  db:
    image: postgis/postgis:15-3.3
    environment:
      - POSTGRES_DB=aedes
      - POSTGRES_PASSWORD=password
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  timescaledb:
    image: timescale/timescaledb:latest-pg15
    environment:
      - POSTGRES_DB=timeseries
    # For time-series weather, satellite data

  vector-db:
    image: ankane/pgvector
    # For embeddings, RAG

volumes:
  pgdata:
```

**Kubernetes for Production:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aedes-ml-inference
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-inference
  template:
    metadata:
      labels:
        app: ml-inference
    spec:
      containers:
      - name: ml-service
        image: aedes/ml-inference:v2.0.0
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "16Gi"
          requests:
            memory: "8Gi"
        env:
        - name: MODEL_PATH
          value: "/models/risk-predictor-v2"
        volumeMounts:
        - name: model-storage
          mountPath: /models
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ml-inference-service
spec:
  selector:
    app: ml-inference
  ports:
  - port: 8080
    targetPort: 8080
  type: LoadBalancer
```

#### 5.4 Cloud Architecture

**AWS Architecture Example:**

```
┌─────────────────────────────────────────────────────────────┐
│                      CloudFront (CDN)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  API Gateway (REST/GraphQL)                  │
└────┬──────────┬──────────┬──────────┬──────────┬────────────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐
│ECS/Fargate │Lambda│ │SageMaker│ │Step Fn│ │ Bedrock    │
│Services │ │Funcs │ │Endpoints│ │Workflow│ │ (LLMs)     │
└────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘ └──────┬─────┘
     │          │          │          │            │
     ▼          ▼          ▼          ▼            ▼
┌────────────────────────────────────────────────────────────┐
│                     Data Layer                              │
│  RDS (Postgres)  │  S3 (Data Lake)  │  OpenSearch         │
│  DynamoDB        │  Timestream      │  ElastiCache        │
└────────────────────────────────────────────────────────────┘
     ▲          ▲          ▲
     │          │          │
┌────┴──────────┴──────────┴─────┐
│  Data Ingestion Pipeline       │
│  - EventBridge (Scheduling)    │
│  - Kinesis (Streaming)         │
│  - Glue (ETL)                  │
└────────────────────────────────┘
```

**Cost-Effective Setup:**

```python
# Serverless configuration
import json

serverless_config = {
    "service": "aedes-platform",
    "provider": {
        "name": "aws",
        "runtime": "python3.11",
        "region": "us-east-1",
        "environment": {
            "STAGE": "${opt:stage, 'dev'}"
        }
    },
    "functions": {
        "satellite_processor": {
            "handler": "handlers.satellite.process",
            "events": [
                {"schedule": "rate(1 day)"}  # Daily updates
            ],
            "memorySize": 3008,
            "timeout": 900
        },
        "risk_assessment": {
            "handler": "handlers.risk.assess",
            "events": [
                {"http": {"path": "/assess", "method": "post"}}
            ]
        },
        "ai_insights": {
            "handler": "handlers.ai.generate_insights",
            "environment": {
                "ANTHROPIC_API_KEY": "${env:ANTHROPIC_API_KEY}"
            }
        }
    }
}
```

#### 5.5 Database Modernization

**A. PostGIS for Geospatial Data**

```sql
-- Modern schema design
CREATE TABLE risk_assessments (
    id SERIAL PRIMARY KEY,
    location GEOGRAPHY(POINT, 4326),
    risk_level INTEGER CHECK (risk_level BETWEEN 1 AND 5),
    assessment_date TIMESTAMP WITH TIME ZONE,
    features JSONB,  -- Store all features as JSON
    prediction_metadata JSONB,

    -- Spatial index
    CONSTRAINT valid_coordinates CHECK (
        ST_X(location::geometry) BETWEEN -180 AND 180 AND
        ST_Y(location::geometry) BETWEEN -90 AND 90
    )
);

CREATE INDEX idx_risk_location ON risk_assessments USING GIST(location);
CREATE INDEX idx_risk_date ON risk_assessments USING BRIN(assessment_date);
CREATE INDEX idx_risk_features ON risk_assessments USING GIN(features);

-- Spatial queries
SELECT
    id,
    risk_level,
    ST_Distance(location, ST_MakePoint(121.0, 14.5)::geography) / 1000 as distance_km
FROM risk_assessments
WHERE ST_DWithin(
    location,
    ST_MakePoint(121.0, 14.5)::geography,
    50000  -- 50km radius
)
ORDER BY risk_level DESC;
```

**B. TimescaleDB for Time-Series**

```sql
-- Hypertable for satellite time series
CREATE TABLE satellite_observations (
    time TIMESTAMPTZ NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    ndvi FLOAT,
    ndwi FLOAT,
    surface_temp FLOAT,
    precipitation FLOAT
);

SELECT create_hypertable('satellite_observations', 'time');

-- Automatic aggregation
CREATE MATERIALIZED VIEW satellite_daily_avg
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    location,
    AVG(ndvi) as avg_ndvi,
    AVG(surface_temp) as avg_temp
FROM satellite_observations
GROUP BY bucket, location;

-- Query optimization
SELECT * FROM satellite_daily_avg
WHERE bucket >= NOW() - INTERVAL '30 days'
  AND ST_DWithin(location, ST_MakePoint(121.0, 14.5)::geography, 10000);
```

**C. Vector Database for RAG**

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Initialize Qdrant for embeddings
client = QdrantClient(url="http://localhost:6333")

# Create collection for research papers
client.create_collection(
    collection_name="epidemiology_research",
    vectors_config=VectorParams(
        size=1024,  # Voyage AI embedding dimension
        distance=Distance.COSINE
    )
)

# Store embeddings
client.upsert(
    collection_name="epidemiology_research",
    points=[
        PointStruct(
            id=i,
            vector=embedding,
            payload={
                "title": paper['title'],
                "abstract": paper['abstract'],
                "doi": paper['doi']
            }
        )
        for i, (embedding, paper) in enumerate(zip(embeddings, papers))
    ]
)

# Semantic search
results = client.search(
    collection_name="epidemiology_research",
    query_vector=question_embedding,
    limit=5
)
```

---

## 6. Frontend & Visualization Modernization

### Current State
- Basic Streamlit app
- Static Folium maps
- Limited interactivity

### Modernization Strategy

#### 6.1 Modern Web Dashboard

**Option A: Next.js + React + TypeScript**

```typescript
// app/dashboard/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { Map } from '@/components/Map';
import { RiskChart } from '@/components/RiskChart';
import { AIInsights } from '@/components/AIInsights';

export default function DashboardPage() {
  const [riskData, setRiskData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const analyzeRegion = async (geojson: any) => {
    setIsLoading(true);

    const response = await fetch('/api/assess-risk', {
      method: 'POST',
      body: JSON.stringify({
        aoi_geojson: geojson,
        date_from: '2024-01-01',
        date_to: '2024-12-31'
      })
    });

    const data = await response.json();
    setRiskData(data);
    setIsLoading(false);
  };

  return (
    <div className="grid grid-cols-12 gap-4 p-4">
      {/* Interactive Map */}
      <div className="col-span-8">
        <Map
          riskZones={riskData?.risk_zones}
          onRegionSelect={analyzeRegion}
        />
      </div>

      {/* AI Insights Panel */}
      <div className="col-span-4">
        <AIInsights
          insights={riskData?.insights}
          recommendations={riskData?.recommendations}
          loading={isLoading}
        />
      </div>

      {/* Charts */}
      <div className="col-span-12">
        <RiskChart data={riskData?.risk_zones} />
      </div>
    </div>
  );
}
```

**Advanced Mapping with Deck.gl:**

```typescript
// components/Map.tsx
import DeckGL from '@deck.gl/react';
import { HeatmapLayer, ScatterplotLayer, PolygonLayer } from '@deck.gl/layers';
import { Map as MapboxMap } from 'react-map-gl';

export function Map({ riskZones }) {
  const layers = [
    new HeatmapLayer({
      id: 'heatmap-layer',
      data: riskZones,
      getPosition: d => [d.longitude, d.latitude],
      getWeight: d => d.risk_level,
      radiusPixels: 60,
      intensity: 1,
      threshold: 0.05,
      colorRange: [
        [0, 255, 0, 25],      // Low risk - green
        [255, 255, 0, 85],    // Medium - yellow
        [255, 0, 0, 255]      // High risk - red
      ]
    }),

    new ScatterplotLayer({
      id: 'healthcare-layer',
      data: healthcareFacilities,
      getPosition: d => [d.longitude, d.latitude],
      getFillColor: [0, 128, 255],
      getRadius: 100,
      pickable: true,
      onHover: ({object}) => setTooltip(object)
    })
  ];

  return (
    <DeckGL
      initialViewState={{
        longitude: 121.0,
        latitude: 14.5,
        zoom: 11,
        pitch: 45
      }}
      controller={true}
      layers={layers}
    >
      <MapboxMap mapStyle="mapbox://styles/mapbox/dark-v11" />
    </DeckGL>
  );
}
```

**Option B: Gradio for Rapid Prototyping**

```python
import gradio as gr
import folium
from anthropic import Anthropic

def analyze_region(geojson_file, date_from, date_to):
    """All-in-one analysis with AI insights"""

    # Load geojson
    import json
    geojson = json.load(geojson_file)

    # Run analysis
    risk_data = assess_disease_risk(geojson, date_from, date_to)

    # Generate map
    m = create_risk_map(risk_data)
    map_html = m._repr_html_()

    # AI insights
    client = Anthropic()
    insights = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"Analyze this disease risk data and provide insights: {risk_data}"
        }]
    )

    # Charts
    fig = create_risk_charts(risk_data)

    return map_html, insights.content[0].text, fig

# Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🦟 AEDES: AI-Powered Disease Risk Assessment")

    with gr.Row():
        with gr.Column(scale=1):
            geojson_input = gr.File(label="Upload Area of Interest (GeoJSON)")
            date_from = gr.Date(label="Start Date")
            date_to = gr.Date(label="End Date")
            analyze_btn = gr.Button("Analyze Risk", variant="primary")

        with gr.Column(scale=2):
            map_output = gr.HTML(label="Risk Map")

    with gr.Row():
        insights_output = gr.Markdown(label="AI-Generated Insights")

    with gr.Row():
        charts_output = gr.Plot(label="Risk Analysis")

    analyze_btn.click(
        fn=analyze_region,
        inputs=[geojson_input, date_from, date_to],
        outputs=[map_output, insights_output, charts_output]
    )

demo.launch(share=True)
```

#### 6.2 Advanced Visualizations

**A. Kepler.gl for Geospatial Exploration**

```python
from keplergl import KeplerGl

def create_interactive_analysis(risk_df, satellite_df, amenities_df):
    """Rich multi-layer visualization"""

    map_config = {
        'version': 'v1',
        'config': {
            'mapState': {
                'latitude': 14.5,
                'longitude': 121.0,
                'zoom': 10
            }
        }
    }

    keplergl_map = KeplerGl(height=800, config=map_config)

    # Add layers
    keplergl_map.add_data(data=risk_df, name='Risk Zones')
    keplergl_map.add_data(data=satellite_df, name='Satellite Data')
    keplergl_map.add_data(data=amenities_df, name='Healthcare Facilities')

    return keplergl_map
```

**B. Plotly Dash for Complex Dashboards**

```python
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("AEDES Risk Assessment Platform"),

    dcc.Tabs([
        dcc.Tab(label='Risk Map', children=[
            dcc.Graph(id='choropleth-map'),
            dcc.Slider(id='time-slider', min=0, max=365, value=0,
                      marks={i: f'Day {i}' for i in range(0, 366, 30)})
        ]),

        dcc.Tab(label='Time Series', children=[
            dcc.Graph(id='risk-timeseries'),
            dcc.Dropdown(
                id='location-dropdown',
                options=[{'label': loc, 'value': loc} for loc in locations],
                value=locations[0]
            )
        ]),

        dcc.Tab(label='AI Insights', children=[
            html.Div(id='ai-insights-panel'),
            html.Button('Regenerate Insights', id='regenerate-btn')
        ])
    ])
])

@app.callback(
    Output('choropleth-map', 'figure'),
    Input('time-slider', 'value')
)
def update_map(day):
    # Filter data for selected day
    df_filtered = risk_data[risk_data['day'] == day]

    fig = px.density_mapbox(
        df_filtered,
        lat='latitude',
        lon='longitude',
        z='risk_level',
        radius=10,
        center=dict(lat=14.5, lon=121.0),
        zoom=10,
        mapbox_style='carto-darkmatter',
        color_continuous_scale='Turbo'
    )

    return fig

@app.callback(
    Output('ai-insights-panel', 'children'),
    Input('regenerate-btn', 'n_clicks')
)
def generate_insights(n_clicks):
    # Call Claude API
    insights = ai_analyst.generate_insights(current_data)
    return dcc.Markdown(insights)

if __name__ == '__main__':
    app.run_server(debug=True)
```

**C. Observable Framework for Data Stories**

```javascript
// Disease risk narrative with interactive charts
import * as Plot from "@observablehq/plot";
import * as d3 from "d3";

const riskData = await FileAttachment("risk_data.json").json();

display(md`# Disease Risk Assessment: Manila Metro Area

Our AI-powered analysis identified **${riskData.high_risk_zones.length} high-risk zones**
requiring immediate attention.`);

// Interactive scatter plot
display(Plot.plot({
  marks: [
    Plot.dot(riskData.points, {
      x: "ndvi",
      y: "surface_temperature",
      fill: "risk_level",
      r: "population_density",
      tip: true
    })
  ],
  color: {
    scheme: "YlOrRd",
    legend: true,
    label: "Risk Level"
  }
}));

// Time series with anomaly detection
display(Plot.plot({
  marks: [
    Plot.lineY(riskData.timeseries, {x: "date", y: "cases", stroke: "steelblue"}),
    Plot.ruleY([0]),
    Plot.dot(riskData.anomalies, {x: "date", y: "cases", fill: "red", r: 5})
  ]
}));
```

#### 6.3 Mobile Application

**React Native for Mobile Access:**

```typescript
// app/(tabs)/risk-map.tsx
import { useState, useEffect } from 'react';
import MapView, { Heatmap, Marker } from 'react-native-maps';
import { View, StyleSheet } from 'react-native';

export default function RiskMapScreen() {
  const [riskData, setRiskData] = useState([]);
  const [userLocation, setUserLocation] = useState(null);

  useEffect(() => {
    // Get user location
    getCurrentLocation().then(setUserLocation);

    // Fetch nearby risk data
    fetchRiskData(userLocation).then(setRiskData);
  }, [userLocation]);

  const calculatePersonalRisk = async () => {
    const response = await fetch('/api/personal-risk', {
      method: 'POST',
      body: JSON.stringify({ location: userLocation })
    });
    const data = await response.json();
    Alert.alert('Your Risk Level', data.insights);
  };

  return (
    <View style={styles.container}>
      <MapView
        style={styles.map}
        initialRegion={{
          latitude: userLocation?.latitude || 14.5,
          longitude: userLocation?.longitude || 121.0,
          latitudeDelta: 0.1,
          longitudeDelta: 0.1
        }}
      >
        <Heatmap
          points={riskData.map(d => ({
            latitude: d.latitude,
            longitude: d.longitude,
            weight: d.risk_level
          }))}
          radius={40}
          opacity={0.7}
        />

        {userLocation && (
          <Marker coordinate={userLocation} title="You are here" />
        )}
      </MapView>

      <Button title="Check My Risk" onPress={calculatePersonalRisk} />
    </View>
  );
}
```

---

## 7. MLOps & Model Management

### Current State
- Models saved as pickle files
- No versioning
- Manual retraining
- No monitoring

### Modernization Strategy

#### 7.1 Model Registry & Versioning

**MLflow Integration:**

```python
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

# Configure MLflow
mlflow.set_tracking_uri("http://mlflow-server:5000")
mlflow.set_experiment("disease-risk-assessment")

def train_and_register_model(X_train, y_train, model_name="risk-predictor"):
    """Train model with full tracking"""

    with mlflow.start_run(run_name=f"training-{datetime.now()}"):
        # Log parameters
        mlflow.log_params({
            "n_samples": len(X_train),
            "n_features": X_train.shape[1],
            "model_type": "AutoGluon",
            "training_date": datetime.now().isoformat()
        })

        # Train model
        predictor = TabularPredictor(label='risk_level')
        predictor.fit(
            train_data=X_train,
            time_limit=3600,
            presets='best_quality'
        )

        # Log metrics
        test_score = predictor.evaluate(X_test)
        mlflow.log_metrics({
            "test_f1": test_score['f1'],
            "test_accuracy": test_score['accuracy'],
            "test_roc_auc": test_score['roc_auc']
        })

        # Log model
        mlflow.sklearn.log_model(
            predictor,
            "model",
            registered_model_name=model_name
        )

        # Log artifacts
        mlflow.log_artifact("feature_importance.png")
        mlflow.log_dict(feature_metadata, "features.json")

        # Tag for production
        client = MlflowClient()
        latest_version = client.get_latest_versions(model_name)[0]

        if test_score['f1'] > 0.85:  # Quality threshold
            client.transition_model_version_stage(
                name=model_name,
                version=latest_version.version,
                stage="Production"
            )

        return predictor

# Load production model
def load_production_model(model_name="risk-predictor"):
    """Load current production model"""
    model_uri = f"models:/{model_name}/Production"
    return mlflow.sklearn.load_model(model_uri)
```

**Weights & Biases for Experiment Tracking:**

```python
import wandb

wandb.init(
    project="aedes-risk-assessment",
    config={
        "learning_rate": 0.001,
        "architecture": "ConvLSTM",
        "dataset": "satellite-2024",
        "epochs": 100
    }
)

# Log during training
for epoch in range(epochs):
    train_loss = train_one_epoch(model, train_loader)
    val_loss = validate(model, val_loader)

    wandb.log({
        "epoch": epoch,
        "train_loss": train_loss,
        "val_loss": val_loss,
        "learning_rate": scheduler.get_last_lr()[0]
    })

    # Log images
    if epoch % 10 == 0:
        fig = plot_predictions(model, sample_batch)
        wandb.log({"predictions": wandb.Image(fig)})

# Save best model
wandb.save("best_model.pt")
```

#### 7.2 Model Serving & Inference

**A. BentoML for Model Serving**

```python
import bentoml
from bentoml.io import JSON, NumpyNdarray

@bentoml.service(
    resources={"gpu": 1, "memory": "4Gi"},
    traffic={"timeout": 60}
)
class DiseaseRiskPredictor:
    def __init__(self):
        self.model = bentoml.mlflow.load_model("risk-predictor:latest")

    @bentoml.api
    def predict(self, features: NumpyNdarray) -> JSON:
        """Predict disease risk"""
        predictions = self.model.predict(features)
        probabilities = self.model.predict_proba(features)

        return {
            "risk_level": int(predictions[0]),
            "confidence": float(probabilities.max()),
            "risk_distribution": probabilities.tolist()
        }

    @bentoml.api(batchable=True, max_batch_size=100)
    def predict_batch(self, features: NumpyNdarray) -> JSON:
        """Batch prediction for efficiency"""
        predictions = self.model.predict(features)
        return {"predictions": predictions.tolist()}

# Deploy
bentoml.build("disease_risk_predictor", version="v2.0.0")
bentoml.containerize("disease_risk_predictor:v2.0.0")
```

**B. TorchServe for Deep Learning Models**

```python
# handler.py
from ts.torch_handler.base_handler import BaseHandler
import torch

class RiskPredictionHandler(BaseHandler):
    def preprocess(self, data):
        """Convert input to tensor"""
        satellite_images = [row['satellite_data'] for row in data]
        return torch.tensor(satellite_images)

    def inference(self, data):
        """Run model inference"""
        with torch.no_grad():
            predictions = self.model(data)
        return predictions

    def postprocess(self, inference_output):
        """Format output"""
        risk_levels = inference_output.argmax(dim=1).tolist()
        confidences = torch.softmax(inference_output, dim=1).max(dim=1).values.tolist()

        return [
            {"risk_level": level, "confidence": conf}
            for level, conf in zip(risk_levels, confidences)
        ]

# Package and deploy
# torch-model-archiver --model-name risk_predictor \
#   --version 2.0 \
#   --handler handler.py \
#   --export-path model_store
```

**C. NVIDIA Triton for Multi-Framework Serving**

```python
# config.pbtxt
name: "risk_predictor_ensemble"
platform: "ensemble"

input [
  {
    name: "satellite_input"
    data_type: TYPE_FP32
    dims: [3, 256, 256]
  },
  {
    name: "tabular_input"
    data_type: TYPE_FP32
    dims: [50]
  }
]

output [
  {
    name: "risk_level"
    data_type: TYPE_INT32
    dims: [1]
  }
]

ensemble_scheduling {
  step [
    {
      model_name: "satellite_encoder"
      model_version: -1
      input_map {
        key: "input"
        value: "satellite_input"
      }
      output_map {
        key: "embeddings"
        value: "sat_embeddings"
      }
    },
    {
      model_name: "risk_classifier"
      model_version: -1
      input_map {
        key: "sat_features"
        value: "sat_embeddings"
      }
      input_map {
        key: "tabular_features"
        value: "tabular_input"
      }
      output_map {
        key: "output"
        value: "risk_level"
      }
    }
  ]
}
```

#### 7.3 Automated Retraining Pipeline

**A. Airflow DAG for Scheduled Retraining**

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from datetime import datetime, timedelta

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['alerts@aedes.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'model_retraining_pipeline',
    default_args=default_args,
    description='Automated model retraining',
    schedule_interval='@weekly',  # Every week
    start_date=datetime(2024, 1, 1),
    catchup=False
) as dag:

    # Check for new data
    check_new_data = S3KeySensor(
        task_id='check_new_satellite_data',
        bucket_name='aedes-data',
        bucket_key='processed/satellite/{{ ds }}/*',
        timeout=3600
    )

    # Extract features
    extract_features = PythonOperator(
        task_id='extract_features',
        python_callable=extract_training_features,
        op_kwargs={'date': '{{ ds }}'}
    )

    # Train model
    train_model = PythonOperator(
        task_id='train_model',
        python_callable=train_risk_model,
        op_kwargs={'config': 'production'}
    )

    # Evaluate model
    evaluate_model = PythonOperator(
        task_id='evaluate_model',
        python_callable=evaluate_model_performance
    )

    # Deploy if better
    deploy_model = PythonOperator(
        task_id='deploy_model',
        python_callable=deploy_if_improved,
        trigger_rule='all_success'
    )

    # Update monitoring
    update_monitoring = PythonOperator(
        task_id='update_monitoring',
        python_callable=update_model_monitoring_dashboard
    )

    # Define dependencies
    check_new_data >> extract_features >> train_model >> evaluate_model >> deploy_model >> update_monitoring
```

**B. Continuous Training with Kubeflow**

```yaml
apiVersion: kubeflow.org/v1
kind: Pipeline
metadata:
  name: aedes-training-pipeline
spec:
  entrypoint: training-workflow
  templates:
  - name: training-workflow
    dag:
      tasks:
      - name: data-validation
        template: validate-data
      - name: feature-engineering
        template: engineer-features
        dependencies: [data-validation]
      - name: train-model
        template: train
        dependencies: [feature-engineering]
      - name: evaluate
        template: evaluate-model
        dependencies: [train-model]
      - name: deploy
        template: deploy-model
        dependencies: [evaluate]
        when: "{{tasks.evaluate.outputs.parameters.f1}} > 0.85"

  - name: train
    container:
      image: aedes/trainer:v2
      command: [python]
      args: [
        "train.py",
        "--data-path", "{{inputs.parameters.data-path}}",
        "--output-path", "/models/{{workflow.uid}}"
      ]
      resources:
        limits:
          nvidia.com/gpu: 2
          memory: "32Gi"
```

#### 7.4 Model Monitoring & Observability

**A. Evidently AI for Model Monitoring**

```python
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.test_suite import TestSuite
from evidently.tests import *

def monitor_model_performance(reference_data, current_data):
    """Monitor for data drift and model degradation"""

    # Column mapping
    column_mapping = ColumnMapping(
        target='risk_level',
        prediction='predicted_risk',
        numerical_features=['ndvi', 'surface_temp', 'precipitation'],
        categorical_features=['season', 'region']
    )

    # Generate report
    report = Report(metrics=[
        DataDriftPreset(),
        DataQualityPreset()
    ])

    report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping
    )

    # Save report
    report.save_html("monitoring_report.html")

    # Check for drift
    drift_results = report.as_dict()
    if drift_results['metrics'][0]['result']['dataset_drift']:
        # Alert and trigger retraining
        send_alert("Data drift detected!")
        trigger_retraining()

    return report

# Test suite for CI/CD
test_suite = TestSuite(tests=[
    TestNumberOfColumnsWithMissingValues(),
    TestNumberOfRowsWithMissingValues(),
    TestNumberOfConstantColumns(),
    TestNumberOfDuplicatedColumns(),
    TestColumnsType(),
    TestNumberOfDriftedColumns(columns=['ndvi', 'surface_temp'])
])

test_suite.run(reference_data=ref_data, current_data=prod_data)
test_suite.save_html("test_results.html")
```

**B. Prometheus + Grafana for Real-Time Monitoring**

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
prediction_counter = Counter('predictions_total', 'Total predictions made')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')
risk_distribution = Gauge('current_risk_distribution', 'Risk level distribution', ['risk_level'])

@prediction_latency.time()
def predict_with_monitoring(features):
    """Instrumented prediction function"""

    prediction = model.predict(features)

    # Update metrics
    prediction_counter.inc()
    risk_distribution.labels(risk_level=str(prediction)).inc()

    return prediction

# Grafana dashboard config (JSON)
dashboard_config = {
    "dashboard": {
        "title": "AEDES Model Performance",
        "panels": [
            {
                "title": "Predictions per Minute",
                "targets": [{"expr": "rate(predictions_total[1m])"}]
            },
            {
                "title": "Prediction Latency (p95)",
                "targets": [{"expr": "histogram_quantile(0.95, prediction_latency_seconds)"}]
            },
            {
                "title": "Risk Distribution",
                "targets": [{"expr": "current_risk_distribution"}]
            }
        ]
    }
}
```

---

## 8. Testing & Quality Assurance

### Current State
- No automated tests
- Manual validation only

### Modernization Strategy

#### 8.1 Unit & Integration Tests

```python
# tests/test_satellite_processing.py
import pytest
from aedes.remote_sensing import get_satellite_measures_from_points
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_ee_image():
    """Mock Google Earth Engine image"""
    mock_img = MagicMock()
    mock_img.select.return_value = mock_img
    mock_img.subtract.return_value = mock_img
    mock_img.divide.return_value = mock_img
    return mock_img

def test_ndvi_calculation(mock_ee_image):
    """Test NDVI calculation logic"""
    from aedes.remote_sensing import meanNDVICollection

    aoi = MagicMock()
    result = meanNDVICollection(mock_ee_image, aoi)

    assert isinstance(result, float)
    assert -1 <= result <= 1  # NDVI range

def test_satellite_data_pipeline():
    """Integration test for satellite data collection"""
    with patch('ee.ImageCollection') as mock_collection:
        points = generate_test_points()
        aoi = get_test_aoi()

        result_df = get_satellite_measures_from_points(
            points, aoi, '2024-01-01', '2024-01-31'
        )

        assert not result_df.empty
        assert 'ndvi' in result_df.columns
        assert result_df['ndvi'].between(-1, 1).all()

# tests/test_ml_models.py
def test_model_predictions():
    """Test model output format and ranges"""
    model = load_production_model()
    test_features = generate_test_features()

    predictions = model.predict(test_features)

    assert predictions.shape[0] == len(test_features)
    assert all(1 <= p <= 5 for p in predictions)  # Risk levels 1-5

def test_model_fairness():
    """Ensure model doesn't have spatial bias"""
    from aequitas.group import Group

    predictions_df = get_predictions_with_demographics()

    g = Group()
    xtab, _ = g.get_crosstabs(predictions_df)

    # Check for disparate impact
    assert xtab['fpr_disparity'].max() < 1.25  # Within acceptable range
```

#### 8.2 Property-Based Testing

```python
from hypothesis import given, strategies as st
import hypothesis.extra.numpy as hnp

@given(
    ndvi=st.floats(min_value=-1, max_value=1),
    temp=st.floats(min_value=-50, max_value=60),
    precip=st.floats(min_value=0, max_value=500)
)
def test_risk_calculation_properties(ndvi, temp, precip):
    """Property-based testing for risk calculation"""
    risk = calculate_risk(ndvi, temp, precip)

    # Properties that should always hold
    assert 1 <= risk <= 5
    assert isinstance(risk, int)

    # Monotonicity: higher temp + higher precip = higher risk
    if temp > 30 and precip > 100:
        assert risk >= 3

@given(hnp.arrays(dtype=np.float32, shape=(100, 10)))
def test_model_robustness(features):
    """Test model with random inputs"""
    try:
        predictions = model.predict(features)
        assert predictions.shape[0] == features.shape[0]
    except Exception as e:
        pytest.fail(f"Model failed on valid input: {e}")
```

#### 8.3 Performance & Load Testing

```python
import locust
from locust import HttpUser, task, between

class AEDESUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def assess_risk(self):
        """Most common operation"""
        self.client.post("/api/assess-risk", json={
            "aoi_geojson": test_geojson,
            "date_from": "2024-01-01",
            "date_to": "2024-12-31"
        })

    @task(1)
    def query_insights(self):
        """AI insights generation"""
        self.client.post("/api/query", json={
            "question": "What are the highest risk areas?"
        })

# Run: locust -f tests/load_test.py --users 100 --spawn-rate 10
```

---

## 9. Security & Compliance

### Modernization Strategy

#### 9.1 API Security

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """JWT token validation"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

@app.post("/api/assess-risk")
async def assess_risk(
    request: RiskRequest,
    user: dict = Depends(verify_token)
):
    """Protected endpoint"""
    # Rate limiting by user
    if await rate_limiter.is_rate_limited(user['sub']):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    return await process_risk_assessment(request)
```

#### 9.2 Data Privacy

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def anonymize_pii(text):
    """Remove PII from user inputs"""
    results = analyzer.analyze(text=text, language='en')
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text

# GDPR compliance
def handle_data_deletion_request(user_id):
    """Right to be forgotten"""
    # Delete all user data
    db.delete_user_assessments(user_id)
    db.delete_user_profile(user_id)

    # Log for audit
    audit_log.info(f"Deleted all data for user {user_id}")
```

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Months 1-3)

**Goals:** Modernize core infrastructure

- [ ] Set up cloud infrastructure (AWS/GCP)
- [ ] Migrate to containerized architecture
- [ ] Implement FastAPI backend
- [ ] Set up CI/CD pipelines
- [ ] Database migration (PostGIS + TimescaleDB)
- [ ] Implement authentication & authorization

**Deliverables:**
- Docker-compose development environment
- Kubernetes production deployment
- API documentation (OpenAPI)
- Security audit report

### Phase 2: Data & ML Modernization (Months 4-6)

**Goals:** Enhance data sources and ML capabilities

- [ ] Integrate cloud-native geospatial formats (COG, Zarr)
- [ ] Add real-time weather APIs
- [ ] Implement AutoGluon for AutoML
- [ ] Deploy MLflow for model management
- [ ] Set up model serving with BentoML
- [ ] Implement data drift monitoring

**Deliverables:**
- Automated data pipeline
- Model registry
- Improved model performance metrics
- Monitoring dashboard

### Phase 3: AI Integration (Months 7-9)

**Goals:** Add generative AI capabilities

- [ ] Integrate Claude API for insights generation
- [ ] Implement vision-language models
- [ ] Build RAG system for epidemiology knowledge
- [ ] Natural language querying
- [ ] Automated report generation
- [ ] Code generation for custom analyses

**Deliverables:**
- AI insights API
- Interactive Q&A system
- Automated reporting system
- Multi-modal analysis capabilities

### Phase 4: Advanced Features (Months 10-12)

**Goals:** Deploy production-ready platform

- [ ] Deep learning models (ConvLSTM, GNN)
- [ ] Real-time monitoring dashboard
- [ ] Mobile application
- [ ] Advanced visualizations (Deck.gl, Kepler.gl)
- [ ] Forecasting capabilities
- [ ] Alert system

**Deliverables:**
- Production web platform
- Mobile apps (iOS/Android)
- Real-time alerting system
- Forecasting models

### Phase 5: Scale & Optimize (Ongoing)

**Goals:** Production optimization

- [ ] Performance optimization
- [ ] Cost optimization
- [ ] User feedback integration
- [ ] Additional data sources
- [ ] Model improvements
- [ ] Feature expansion

---

## 11. Technology Stack Summary

### Backend
- **API:** FastAPI, GraphQL (Strawberry)
- **ML/AI:** AutoGluon, PyTorch, TensorFlow, Claude API
- **Geospatial:** GeoPandas, Rioxarray, Xarray, GDAL
- **Database:** PostgreSQL+PostGIS, TimescaleDB, Redis, Qdrant
- **Orchestration:** Airflow, Kubeflow

### Frontend
- **Web:** Next.js, React, TypeScript
- **Visualization:** Deck.gl, Kepler.gl, Plotly, Mapbox
- **Mobile:** React Native
- **Rapid Prototyping:** Gradio, Streamlit

### Infrastructure
- **Containers:** Docker, Kubernetes
- **Cloud:** AWS (recommended), GCP, Azure
- **CI/CD:** GitHub Actions, ArgoCD
- **Monitoring:** Prometheus, Grafana, Evidently

### Data Sources
- **Satellite:** Google Earth Engine, Sentinel Hub, Planet
- **Weather:** OpenWeatherMap, NASA POWER, ERA5
- **Social:** Twitter API, Reddit API, Google Trends
- **Health:** WHO API, ProMED-mail

### MLOps
- **Experiment Tracking:** MLflow, Weights & Biases
- **Model Serving:** BentoML, TorchServe, Triton
- **Monitoring:** Evidently AI, WhyLabs
- **Feature Store:** Feast, Tecton

---

## 12. Cost Estimation

### Monthly Operational Costs (Estimated)

**Cloud Infrastructure (AWS):**
- ECS/Fargate services: $300-500
- RDS PostgreSQL: $200-300
- S3 storage (1TB): $23
- Lambda executions: $50-100
- SageMaker endpoints: $500-800
- **Subtotal: $1,073-1,723/month**

**APIs & Services:**
- Anthropic Claude API: $500-2,000 (usage-based)
- Mapbox: $0-500 (free tier + overages)
- Sentinel Hub: $0-300
- Weather APIs: $0-100
- **Subtotal: $500-2,900/month**

**Total Estimated: $1,573-4,623/month**

**Cost Optimization Strategies:**
- Use spot instances for training
- Implement caching aggressively
- Optimize LLM prompts for token efficiency
- Use serverless where possible

---

## 13. Success Metrics

### Technical Metrics
- **Model Performance:** F1 score > 0.85, AUC > 0.90
- **API Latency:** p95 < 2 seconds for risk assessment
- **Uptime:** 99.9% availability
- **Data Freshness:** < 24 hours lag for satellite data

### Business Metrics
- **Accuracy:** 90%+ correct high-risk area identification
- **Early Warning:** Detect risk 2-4 weeks before outbreak
- **Coverage:** Support for 50+ metropolitan areas
- **User Engagement:** 1000+ monthly active users

### Impact Metrics
- **Public Health:** Measurable reduction in disease incidence
- **Resource Optimization:** 30% better allocation of prevention resources
- **Response Time:** 50% faster public health response

---

## 14. Risks & Mitigation

### Technical Risks
1. **Data availability/quality issues**
   - *Mitigation:* Multiple data sources, fallback mechanisms

2. **Model drift over time**
   - *Mitigation:* Continuous monitoring, automated retraining

3. **Scaling challenges**
   - *Mitigation:* Cloud-native architecture, load testing

### Operational Risks
1. **API costs exceeding budget**
   - *Mitigation:* Usage monitoring, caching, rate limiting

2. **Data privacy concerns**
   - *Mitigation:* Anonymization, compliance audit, encryption

3. **Dependency on third-party services**
   - *Mitigation:* Service redundancy, fallback options

---

## 15. Conclusion

This modernization plan transforms AEDES from a research prototype into a production-grade, AI-powered disease risk assessment platform. By leveraging cutting-edge technologies including:

- **Cloud-native geospatial data processing**
- **Advanced deep learning models**
- **Generative AI for insights and automation**
- **Real-time data integration**
- **Modern MLOps practices**

The platform will provide public health officials with:
- **Earlier warnings** of disease outbreaks
- **More accurate** risk assessments
- **Actionable insights** powered by AI
- **Real-time monitoring** capabilities
- **Better resource allocation** decisions

The phased implementation approach ensures manageable complexity while delivering value incrementally over 12 months.

---

## Appendix: Additional Resources

### Learning Resources
- [Google Earth Engine Documentation](https://developers.google.com/earth-engine)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [AutoGluon Documentation](https://auto.gluon.ai/)
- [MLflow Guide](https://mlflow.org/docs/latest/index.html)
- [Anthropic Claude API](https://docs.anthropic.com/)

### Example Repositories
- [Planetary Computer Examples](https://github.com/microsoft/PlanetaryComputerExamples)
- [Awesome Geospatial](https://github.com/sacridini/Awesome-Geospatial)
- [MLOps Best Practices](https://github.com/visenger/awesome-mlops)

### Community
- [GeoForAll](https://www.osgeo.org/community/geo4all/)
- [r/MachineLearning](https://reddit.com/r/MachineLearning)
- [r/datascience](https://reddit.com/r/datascience)
