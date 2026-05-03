# integrated_pipeline.py

import os
import subprocess
import webbrowser
import time
from moveaoi import move_aoi_from_downloads
AOI_PATH = "aoi.geojson"

def run_generate_map():
    print("🗺️ Step 1: Generating map and opening selector...")
    subprocess.run(["python", "generate_map.py"])
    webbrowser.open("interactive_map.html")
    print("🔍 Waiting for 'aoi.geojson' to be created...")

    try:
        # making move_aoi_download file to grab the coordinates
        # ✅ Use move_aoi_from_downloads to handle file waiting and moving
        move_aoi_from_downloads()
        print("✅ AOI file moved and ready.")
    except Exception as e:
        print(f"❌ Error handling AOI: {e}")
        exit()
#processing the satellite data and sending the data to sentinal 
def run_process_satellite_data():
    print("🛰️ Step 2: Running satellite data processing for NDVI...")
    subprocess.run(["python", "process_satellite_data.py"])
    print("✅ NDVI .tif file generated.")
#using the .tif file converted to png to easy access of data in PNG form
def run_imageonmap():
    print("🖼️ Step 3: Converting NDVI .tif to PNG...")
    subprocess.run(["python", "imageonmap.py"])
    print("✅ NDVI image (PNG) created.")

def run_ndvi_health_predictor():
    print("🧠 Step 4: Running NDVI health predictor...")
    subprocess.run(["python", "ndvi_health_predictor.py"])
    print("✅ Health prediction complete.")

def run_download_sentinel1_sar():
    print("💧 Step 5: Processing SMI from Sentinel-1 data...")
    subprocess.run(["python", "download_sentinel1_sar.py"])
    print("✅ S1_VH.tif and S1_VV.tif is created")

def run_smi_processor():
    print("💧 Step 5: Processing SMI from Sentinel-1 data...")
    subprocess.run(["python", "smi_processor.py"])
    print("✅ SMI overlay PNG created.")

def update_status(status):
    with open("status.js", "w") as f:
        f.write(f'window.satelliteProcessingStatus = "{status}";')

if __name__ == "__main__":
    print("\n🔄 === Integrated Satellite Workflow Starting ===\n")
    update_status("processing")
    
    run_generate_map()
    run_process_satellite_data()
    run_imageonmap()
    run_ndvi_health_predictor()
    run_download_sentinel1_sar()
    run_smi_processor()
    
    print("\n🎉 Workflow complete. All outputs generated.\n")
    
   
    update_status("complete")
    
    print("🌍 Dashboard updated in-place (if open).")
    print("✅ Process finished.")



