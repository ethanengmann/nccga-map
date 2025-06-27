import pandas as pd
import json
from shapely.geometry import MultiPoint, mapping, Point

# Load the geocoded Excel
df = pd.read_excel("NCCGA_Geocoded.xlsx")

# Initialize GeoJSON structures
schools_features = []
regions_dict = {}

# Build school points and group by region
for _, row in df.iterrows():
    school = row['School']
    region = row['Region']
    lat = row['Latitude']
    lon = row['Longitude']

    # Skip rows without valid coordinates
    if pd.isnull(lat) or pd.isnull(lon):
        continue
    slug = (
        school.strip()
              .lower()
              .replace("  ", " ")
              .replace(" ", "-")
    )
    team_url = f"https://nccga.org/app/teams/{slug}"

    # Add school point
    schools_features.append({
        "type": "Feature",
        "properties": {
            "school": school,
            "region": region
        },
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        }
    })

    # Collect points per region
    regions_dict.setdefault(region, []).append(Point(lon, lat))

# Build regions polygons using convex hulls with smoothing
regions_features = []
for region, points in regions_dict.items():
    if len(points) == 1:
        # Single school -> Point geometry
        geometry = mapping(points[0])
    elif len(points) == 2:
        # Two schools -> LineString geometry
        geometry = {
            "type": "LineString",
            "coordinates": [list(p.coords)[0] for p in points]
        }
    else:
        # Three or more -> Convex hull polygon + smoothing
        multipoint = MultiPoint(points)
        smoothed = multipoint.convex_hull.buffer(0.15).simplify(0.01)
        geometry = mapping(smoothed)

    regions_features.append({
        "type": "Feature",
        "properties": {
            "region": region,
            "schools": [f["properties"]["school"] for f in schools_features if f["properties"]["region"] == region]
        },
        "geometry": geometry
    })

# Write schools.geojson
with open("schools.geojson", "w") as f:
    json.dump({
        "type": "FeatureCollection",
        "features": schools_features
    }, f, indent=2)

# Write regions.geojson
with open("regions.geojson", "w") as f:
    json.dump({
        "type": "FeatureCollection",
        "features": regions_features
    }, f, indent=2)

print("✅ Generated schools.geojson and regions.geojson with smoothing!")
