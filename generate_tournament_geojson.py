import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import json

# === Step 1: Load spreadsheet ===
df = pd.read_excel("Map Courses.xlsx")
df = df.dropna(subset=["Course Name", "Region", "Address"])

# === Step 2: Geocode ===
geolocator = Nominatim(user_agent="nccga_map")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

df["location"] = df["Address"].apply(geocode)
df["latitude"] = df["location"].apply(lambda loc: loc.latitude if loc else None)
df["longitude"] = df["location"].apply(lambda loc: loc.longitude if loc else None)

df = df.dropna(subset=["latitude", "longitude"])

# === Step 3: Build GeoJSON ===
features = []
for _, row in df.iterrows():
    features.append({
        "type": "Feature",
        "properties": {
            "course_name": row["Course Name"],
            "region": row["Region"]
        },
        "geometry": {
            "type": "Point",
            "coordinates": [row["longitude"], row["latitude"]]
        }
    })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

# === Step 4: Save GeoJSON ===
with open("tournaments.geojson", "w") as f:
    json.dump(geojson, f, indent=2)

print("✅ tournaments.geojson created with", len(features), "features.")
