import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Read your cleaned master spreadsheet
df = pd.read_excel("NCCGA_Master.xlsx")

# Set up geocoder with a user agent
geolocator = Nominatim(user_agent="nccga-map-geocoder")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Create a full location string from City and State
df["location"] = df["City"] + ", " + df["State"]

# Geocode
print("Geocoding schools — this will take time…")
df["geocode"] = df["location"].apply(geocode)

# Extract lat/lon
df["Latitude"] = df["geocode"].apply(lambda x: x.latitude if x else None)
df["Longitude"] = df["geocode"].apply(lambda x: x.longitude if x else None)

# Save to new Excel file
df.to_excel("NCCGA_Geocoded.xlsx", index=False)
print("✅ Geocoding complete. Results saved to NCCGA_Geocoded.xlsx")
