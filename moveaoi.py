# move_aoi.py
import os
import time
import shutil

def move_aoi_from_downloads(filename="aoi.geojson", wait_for_file=True, timeout=300000):
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    aoi_path = os.path.join(downloads_folder, filename)
    project_directory = os.getcwd()
    new_aoi_path = os.path.join(project_directory, filename)

    if os.path.exists(new_aoi_path):
        print(f"✅ AOI already exists in project: {new_aoi_path}")
        return new_aoi_path

    if wait_for_file:
        print("⏳ Waiting for AOI file to appear in Downloads folder...")
        start_time = time.time()
        while not os.path.exists(aoi_path):
            time.sleep(1)
            if time.time() - start_time > timeout:
                raise TimeoutError(f"❌ Timeout: '{filename}' not found in Downloads within {timeout} seconds.")

    if os.path.exists(aoi_path):
        shutil.move(aoi_path, new_aoi_path)
        print(f"✅ Moved '{filename}' from Downloads to {new_aoi_path}")
    else:
        raise FileNotFoundError(f"❌ '{filename}' not found in Downloads or project directory.")

    return new_aoi_path
