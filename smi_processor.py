import numpy as np
import rasterio
import matplotlib.pyplot as plt
import os

def calculate_smi(vv_path, vh_path, output_path):
    with rasterio.open(vv_path) as vv_src, rasterio.open(vh_path) as vh_src:
        vv = vv_src.read(1).astype(np.float32)
        vh = vh_src.read(1).astype(np.float32)

    # NDPI (Normalized Difference Polarization Index)
    ndpi = (vv - vh) / (vv + vh + 1e-6)

    # Normalize as Soil Moisture Index
    smi = (ndpi - np.nanmin(ndpi)) / (np.nanmax(ndpi) - np.nanmin(ndpi))

    # Save as PNG
    plt.imsave(output_path, smi, cmap="Blues")
    print(f"✅ Soil Moisture Index saved to {output_path}")

# 🔽 This block runs when you execute the file directly
if __name__ == "__main__":
    vv_path = "sentinel1/S1_VV.tif"
    vh_path = "sentinel1/S1_VH.tif"
    output_path = "smi_overlay.png"

    # Ensure output folder exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    calculate_smi(vv_path, vh_path, output_path)
