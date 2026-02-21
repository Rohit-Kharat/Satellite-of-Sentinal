import numpy as np
import rasterio
import matplotlib.pyplot as plt
import os

def calculate_smi(vv_path, vh_path, output_path):
    with rasterio.open(vv_path) as vv_src, rasterio.open(vh_path) as vh_src:
        vv = vv_src.read(1).astype(np.float32)
        vh = vh_src.read(1).astype(np.float32)
        bounds = vv_src.bounds

    # NDPI (Normalized Difference Polarization Index)
    ndpi = (vv - vh) / (vv + vh + 1e-6)

    # Normalize as Soil Moisture Index
    smi = (ndpi - np.nanmin(ndpi)) / (np.nanmax(ndpi) - np.nanmin(ndpi))

    # Save as PNG
    plt.imsave(output_path, smi, cmap="Blues")
    print(f"✅ Soil Moisture Index saved to {output_path}")

    # Inject into interactive_map.html
    inject_smi_into_map(output_path, bounds)

def inject_smi_into_map(png_path, bounds, map_path="interactive_map.html"):
    print(f"🗺️ Injecting SMI overlay into {map_path}...")
    if not os.path.exists(map_path):
        print(f"⚠️ Warning: {map_path} not found.")
        return

    overlay_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
    
    with open(map_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the folium map ID
    import re
    map_id_match = re.search(r'var (map_[a-z0-9]+) = L.map', content)
    if not map_id_match:
        print("❌ Error: Could not find map ID in HTML.")
        return
    map_id = map_id_match.group(1)

    smi_script = f"""
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            var checkMap = setInterval(function() {{
                if (window['{map_id}']) {{
                    clearInterval(checkMap);
                    var theMap = window['{map_id}'];
                    var smiLayer = L.imageOverlay(
                        '{png_path}',
                        {overlay_bounds},
                        {{ opacity: 0.7, interactive: true }}
                    );
                    smiLayer.addTo(theMap);
                }}
            }}, 100);
        }});
    </script>
    """

    if "</body>" in content:
        # Avoid duplicate SMI layers
        if f"'{png_path}'" in content:
             content = re.sub(rf'<script>.*?{re.escape(png_path)}.*?</script>', '', content, flags=re.DOTALL)

        new_content = content.replace("</body>", smi_script + "\n</body>")
        with open(map_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ SMI Layer injected into {map_path}")

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

