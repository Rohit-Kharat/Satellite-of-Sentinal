import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import glob
import os
import rasterio
import folium
from branca.element import Element

def generate_training_data(samples=300):
    np.random.seed(42)
    ndvi = np.random.rand(samples)
    soil_moisture = np.random.rand(samples)
    rainfall = np.random.rand(samples) * 100  # mm

    labels = []
    for i in range(samples):
        if ndvi[i] < 0.2 or soil_moisture[i] < 0.2:
            labels.append("Bad")
        elif 0.2 <= ndvi[i] < 0.5:
            labels.append("Moderate")
        else:
            labels.append("Good")
    
    df = pd.DataFrame({
        'ndvi': ndvi,
        'soil_moisture': soil_moisture,
        'rainfall': rainfall,
        'health': labels
    })
    return df

def train_model():
    df = generate_training_data()
    X = df[['ndvi', 'soil_moisture', 'rainfall']]
    y = df['health']
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def get_suggestions(label):
    if label == "Bad":
        return [
            "⚠️ Increase irrigation immediately.",
            "🧪 Apply NPK fertilizer after soil testing.",
            "🐛 Check for pests or diseases."
        ]
    elif label == "Moderate":
        return [
            "💧 Slightly increase watering.",
            "🌿 Apply foliar nutrient spray.",
            "👀 Monitor environmental stress closely."
        ]
    elif label == "Good":
        return [
            "✅ Maintain current practices.",
            "🌾 Apply precision fertilizer.",
            "📅 Plan harvest based on NDVI trends."
        ]

def load_ndvi_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {image_path}")
    ndvi = img / 255.0  
    return ndvi

def analyze_zones(ndvi_array, model, zone_size=10):
    h, w = ndvi_array.shape
    results = []

    for y in range(0, h, zone_size):
        for x in range(0, w, zone_size):
            zone = ndvi_array[y:y+zone_size, x:x+zone_size]
            avg_ndvi = np.mean(zone)
            soil_moisture = np.random.uniform(0.3, 0.7) 
            rainfall = np.random.uniform(20, 100)       

            features = pd.DataFrame([{
                'ndvi': avg_ndvi,
                'soil_moisture': soil_moisture,
                'rainfall': rainfall
            }])

            prediction = model.predict(features)[0]
            suggestions = get_suggestions(prediction)

            results.append({
                'zone': f'({x},{y})',
                'avg_ndvi': round(avg_ndvi, 3),
                'soil_moisture': round(soil_moisture, 2),
                'rainfall': round(rainfall, 1),
                'health': prediction,
                'suggestions': suggestions
            })

    return results

def inject_report_into_map(results, map_path="interactive_map.html"):
    print(f"📊 Injecting health report into {map_path}...")
    
    # Generate HTML for the sidebar
    rows = ""
    for r in results:
        suggestions_html = "".join(f"<li>{s}</li>" for s in r['suggestions'])
        rows += f"""
        <tr class="{r['health']}">
            <td>{r['zone']}</td>
            <td>{r['avg_ndvi']}</td>
            <td>{r['health']}</td>
            <td><ul>{suggestions_html}</ul></td>
        </tr>
        """

    sidebar_html = f"""
    <div id="health-sidebar" style="
        position: fixed; 
        top: 10px; 
        left: 50px; 
        width: 380px; 
        height: 85%; 
        background: rgba(255, 255, 255, 0.95); 
        z-index: 1000; 
        overflow-y: auto; 
        padding: 15px; 
        box-shadow: 0 0 15px rgba(0,0,0,0.3);
        border-radius: 8px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    ">
        <h2 style="margin-top: 0; color: #2e7d32;">🌿 Crop Health Report</h2>
        
        <div style="margin-bottom: 20px; text-align: center;">
            <h4 style="margin-bottom: 5px;">NDVI Analysis Plot</h4>
            <img src="ndvi_plot.png" alt="NDVI Plot" style="width: 100%; border-radius: 4px; border: 1px solid #ccc;">
        </div>

        <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
            <thead>
                <tr style="background: #2e7d32; color: white;">
                    <th style="border: 1px solid #ccc; padding: 6px;">Zone</th>
                    <th style="border: 1px solid #ccc; padding: 6px;">NDVI</th>
                    <th style="border: 1px solid #ccc; padding: 6px;">Health</th>
                    <th style="border: 1px solid #ccc; padding: 6px;">Suggestions</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        <style>
            .Bad {{ background-color: #ffd6d6; color: #b71c1c; }}
            .Moderate {{ background-color: #fff5cc; color: #f57f17; }}
            .Good {{ background-color: #d6ffd6; color: #1b5e20; }}
            #health-sidebar::-webkit-scrollbar {{ width: 8px; }}
            #health-sidebar::-webkit-scrollbar-thumb {{ background: #ccc; border-radius: 4px; }}
        </style>
        <button onclick="document.getElementById('health-sidebar').style.display='none'" style="
            margin-top: 15px;
            width: 100%;
            padding: 10px;
            background: #d32f2f;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        ">Close Dashboard</button>
    </div>
    """

    # We can't easily use Folium here since the file is already saved as HTML
    # We will manually inject the HTML before the </body> tag
    if not os.path.exists(map_path):
        print(f"⚠️ Warning: {map_path} not found. Skipping injection.")
        return

    with open(map_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "</body>" in content:
        # Avoid duplicate sidebars if script runs multiple times
        import re
        if 'id="health-sidebar"' in content:
            content = re.sub(r'<div id="health-sidebar".*?</div>', '', content, flags=re.DOTALL)
        
        new_content = content.replace("</body>", sidebar_html + "\n</body>")
        with open(map_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ Health report and Plot injected into {map_path}")
    else:
        print("❌ Error: Could not find </body> tag in HTML.")

def run_pipeline(image_path):
    print("📥 Loading image and training model...")
    model = train_model()
    ndvi = load_ndvi_image(image_path)
    results = analyze_zones(ndvi, model)

    # Save NDVI plot for the sidebar
    plt.figure(figsize=(6, 4))
    plt.imshow(ndvi, cmap='YlGn')
    plt.title("NDVI Model Visualization")
    plt.colorbar(label="NDVI")
    plt.tight_layout()
    plt.savefig("ndvi_plot.png")
    plt.close()
    print("📈 NDVI plot saved as ndvi_plot.png")

    # Instead of generating a new report, inject into interactive_map.html
    inject_report_into_map(results)

    print("\n📊 Zone-wise Crop Health Prediction complete.")


if __name__ == "__main__":
    tif_files = sorted(glob.glob("ndvi_*.tif"), reverse=True)
    if not tif_files:
        print("❌ No NDVI .tif files found in the current directory.")
        exit()

    latest_tif = tif_files[0]
    # In this new flow, we assume imageonmap.py already created the PNG for the latest TIF
    latest_png = os.path.splitext(latest_tif)[0] + ".png"
    if not os.path.exists(latest_png):
        print(f"⚠️ PNG not found for {latest_tif}. Please run imageonmap.py first.")
        # Fallback or run conversion logic
    
    run_pipeline(latest_png)

