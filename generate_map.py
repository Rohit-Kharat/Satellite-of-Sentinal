import folium
from folium.plugins import Draw
from branca.element import Element

# Create an interactive map with Google Hybrid satellite tiles (satellite + labels)
m = folium.Map(
    location=[30.0, 70.0],
    zoom_start=5,
    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attr="Google",
    max_zoom=20,
    max_native_zoom=20,
)

# Add search bar (geocoder) for searching cities/places
geocoder_css = Element('<link rel="stylesheet" href="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.css" />')
geocoder_js = Element('<script src="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"></script>')
m.get_root().header.add_child(geocoder_css)
m.get_root().header.add_child(geocoder_js)

geocoder_init = Element("""
<script>
    document.addEventListener("DOMContentLoaded", function() {
        var mapEl = document.querySelector('.folium-map');
        var mapId = mapEl.id;
        // Wait for map variable to be available
        var checkMap = setInterval(function() {
            if (window[mapId] || window['map_' + mapId]) {
                clearInterval(checkMap);
                var theMap = window[mapId] || window['map_' + mapId];
                L.Control.geocoder({
                    defaultMarkGeocode: false,
                    position: 'topright',
                    placeholder: 'Search city or place...',
                    collapsed: false,
                    suggest: true,
                    suggestMinLength: 2,
                    suggestTimeout: 250,
                    queryMinLength: 1,
                }).on('markgeocode', function(e) {
                    var bbox = e.geocode.bbox;
                    theMap.fitBounds(bbox);
                    L.marker(e.geocode.center).addTo(theMap)
                        .bindPopup(e.geocode.name).openPopup();
                }).addTo(theMap);
            }
        }, 100);
    });
</script>
""")
m.get_root().html.add_child(geocoder_init)

# Add drawing tools
draw = Draw(export=True, filename="aoi.geojson")
draw.add_to(m)

# Save map as an HTML file
m.save("interactive_map.html")

print("Open 'interactive_map.html' in a browser, draw AOI, and download 'aoi.geojson'.")
