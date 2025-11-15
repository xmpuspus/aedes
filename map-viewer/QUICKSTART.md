# 🚀 Quick Start Guide

Get the AEDES Map Viewer running in **5 minutes**!

## Prerequisites Check

Before starting, make sure you have:
- [ ] Python 3.8 or higher installed
- [ ] Internet connection
- [ ] Google Earth Engine account ([sign up here](https://earthengine.google.com/signup/))

## Step-by-Step Setup

### Step 1: Navigate to Directory
```bash
cd map-viewer
```

### Step 2: Run Startup Script

**On Linux/Mac:**
```bash
./start.sh
```

**On Windows:**
```batch
start.bat
```

**Or manually:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install AEDES
cd ..
pip install -e .
cd map-viewer

# Authenticate Google Earth Engine (first time only)
earthengine authenticate

# Start server
python backend/app.py
```

### Step 3: Authenticate Google Earth Engine (First Time Only)

If you see a warning about GEE not being initialized:

```bash
earthengine authenticate
```

This will:
1. Open your browser
2. Ask you to sign in with Google
3. Give you an authorization code
4. Save credentials for future use

### Step 4: Open Browser

Navigate to:
```
http://localhost:5000
```

### Step 5: Try It Out!

**Option A: Quick Test**
1. Click the "🚀 Quick Test (Quezon City)" button
2. See instant results!

**Option B: Draw Your Own**
1. Click the square tool in the map toolbar
2. Draw a rectangle anywhere in the world
3. Wait 30-60 seconds
4. Explore the results!

## 🎯 Example Locations to Try

### Philippines
- **Metro Manila**: Lat 14.6, Lon 121.0
- **Cebu City**: Lat 10.3, Lon 123.9
- **Davao City**: Lat 7.0, Lon 125.6

### Other Interesting Locations
- **Amazon Rainforest**: Lat -3.0, Lon -60.0 (dense vegetation)
- **Sahara Desert**: Lat 25.0, Lon 5.0 (barren land)
- **California**: Lat 36.7, Lon -119.7 (varied terrain)
- **Singapore**: Lat 1.3, Lon 103.8 (urban area)

## ⚡ Keyboard Shortcuts

- **Escape** - Cancel drawing
- **Delete** - Remove selected rectangle
- **+/-** - Zoom in/out

## 📊 Understanding Your Results

### Colors on Map
- 🔵 **Blue** = Water
- 🟤 **Tan** = Barren/Desert
- 🟡 **Yellow** = Sparse vegetation
- 🟢 **Light Green** = Moderate vegetation
- 🌲 **Dark Green** = Dense forest

### Key Metrics
- **NDVI** - Vegetation health (-1 to 1)
- **NDWI** - Water content (-1 to 1)
- **Temperature** - Surface temperature (°C)
- **Precipitation** - Rainfall rate

## 🔧 Adjust Settings

### Date Range
- Default: Last 3 months
- Can select any date range
- More recent = faster processing

### Sample Points
- Minimum: 5 points (fastest)
- Default: 20 points (balanced)
- Maximum: 50 points (most detailed)

## 💾 Export Your Data

1. After getting results, look at the right panel
2. Click "📥 Export to CSV"
3. Open in Excel, Google Sheets, or Python

## ❌ Common Issues & Fixes

### "GEE not available"
```bash
earthengine authenticate
```

### "Module not found"
```bash
cd ..
pip install -e .
cd map-viewer
```

### Server won't start
```bash
# Check if port 5000 is already in use
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Use a different port
python backend/app.py --port 5001
```

### Map not loading
- Check browser console (F12)
- Try different browser (Chrome recommended)
- Clear browser cache

## 🎓 Next Steps

Once you're comfortable with the basics:

1. **Compare Seasons** - Run analysis for different months
2. **Track Changes** - Compare same location over time
3. **Study Patterns** - Look for correlations between metrics
4. **Export & Analyze** - Use CSV data in Excel/Python
5. **Customize** - Modify the code to add new features

## 📞 Need Help?

1. Check [README.md](README.md) for detailed documentation
2. See [INTERACTIVE_MAP_PLAN.md](../INTERACTIVE_MAP_PLAN.md) for architecture details
3. Google Earth Engine docs: https://developers.google.com/earth-engine

## 🎉 You're Ready!

You should now have a fully functional satellite data viewer. Happy exploring! 🌍

---

**Time to first result: ~2 minutes**
**Easy rating: ⭐⭐⭐⭐⭐**
