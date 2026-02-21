# from flask import Flask, render_template, send_file
# import os

# app = Flask(__name__)

# # Set correct path for NDVI file
# ndvi_png = os.path.join(os.getcwd(), "ndvi_output.png")

# @app.route("/ndvi")
# def get_ndvi():
#     if not os.path.exists(ndvi_png):
#         return "❌ Error: NDVI image not found. Please process the NDVI first.", 404
#     return send_file(ndvi_png, mimetype="image/png")

# @app.route("/")
# def index():
#     return render_template("index.html")

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, render_template, send_file, jsonify
import rasterio
from rasterio.warp import transform_bounds
from rasterio.crs import CRS
import os

app = Flask(__name__)

# File paths
ndvi_tif_path = "ndvi_20250320_215628.tif"  # Update this path
ndvi_png = "ndvi_output.png"

def ensure_georeferencing():
    """Check if NDVI TIFF has a CRS; assign one if missing."""
    with rasterio.open(ndvi_tif_path, "r+") as src:
        if src.crs is None:
            print("⚠️ NDVI file is missing CRS. Assigning EPSG:4326.")
            src.crs = CRS.from_epsg(4326)  # Assign WGS 84 (lat/lon)

def get_latlon_bounds():
    """Extract latitude/longitude bounds from NDVI TIFF file."""
    try:
        with rasterio.open(ndvi_tif_path) as src:
            if src.crs is None:
                return None  # No CRS found, image is not georeferenced

            bounds = src.bounds  # (left, bottom, right, top)
            src_crs = src.crs  # Source CRS

            # Convert to lat/lon (EPSG:4326)
            latlon_bounds = transform_bounds(src_crs, "EPSG:4326", *bounds)
            return latlon_bounds  # (min_lon, min_lat, max_lon, max_lat)
    except Exception as e:
        print(f"Error processing NDVI file: {e}")
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ndvi")
def get_ndvi():
    """Serve the NDVI image."""
    if not os.path.exists(ndvi_png):
        return "❌ Error: NDVI image not found.", 404
    return send_file(ndvi_png, mimetype="image/png")

@app.route("/ndvi_bounds")
def ndvi_bounds():
    """Return the NDVI bounding box as JSON."""
    ensure_georeferencing()  # Ensure CRS is set
    bounds = get_latlon_bounds()
    if bounds:
        return jsonify({"min_lon": bounds[0], "min_lat": bounds[1], "max_lon": bounds[2], "max_lat": bounds[3]})
    return jsonify({"error": "NDVI file is missing georeferencing data."}), 400

if __name__ == "__main__":
    app.run(debug=True)
