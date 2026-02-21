import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

tif_files = sorted(glob.glob("ndvi_*.tif"), reverse=True)

if not tif_files:
    raise FileNotFoundError("❌ No NDVI .tif files found in the directory.")

# Use the latest file based on filename
ndvi_tif = tif_files[0]
ndvi_png = os.path.splitext(ndvi_tif)[0] + ".png"  # Same base name for output PNG
# Open NDVI file
with rasterio.open(ndvi_tif) as src:
    ndvi_data = src.read(1).astype(np.float32)
    profile = src.profile
    bounds = src.bounds  # Get bounding box for Leaflet map

# Normalize NDVI for visualization (-1 to 1 mapped to 0-255)
ndvi_normalized = ((ndvi_data - np.nanmin(ndvi_data)) /
                   (np.nanmax(ndvi_data) - np.nanmin(ndvi_data)) * 255).astype(np.uint8)

# Save as PNG in the correct project directory
plt.imsave(ndvi_png, ndvi_normalized, cmap="RdYlGn")

print(f"✅ NDVI Image converted to PNG and saved at {os.path.abspath(ndvi_png)}")
print(f"Bounding Box: {bounds}")
