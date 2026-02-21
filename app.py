from flask import Flask, render_template, send_file

app = Flask(__name__)

# Route to serve the main dashboard
@app.route("/")
def index():
    return render_template("index.html")

# Routes to serve GeoTIFF files
@app.route("/ndvi")
def get_ndvi():
    return send_file("ndvi.tif", mimetype="image/tiff")

if __name__ == "__main__":
    app.run(debug=True)



