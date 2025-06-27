import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, MultiPoint

# Read your geocoded data
df = pd.read_excel("NCCGA_Geocoded.xlsx")
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

regions = []
for region_name, group in gdf.groupby("Region"):
    points = list(group.geometry)
    if len(points) < 3:
        # Can't make a polygon from fewer than 3 points: keep as MultiPoint
        geom = MultiPoint(points).convex_hull
    else:
        # Create convex hull
        hull = MultiPoint(points).convex_hull
        # Buffer slightly to smooth edges visually (adjust buffer distance as needed)
        smoothed = hull.buffer(0.2)  # degrees; tweak for your needs
        geom = smoothed
    regions.append({
        "region": region_name,
        "schools": group["School"].tolist(),
        "geometry": geom
    })

# Create GeoDataFrame for regions
regions_gdf = gpd.GeoDataFrame(regions)

# Save to regions.geojson
regions_gdf.to_file("regions.geojson", driver="GeoJSON")
print("✅ Generated smoother regions.geojson!")
