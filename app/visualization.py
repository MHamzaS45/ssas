""" INTERACTIVE MAP (LEAFLET.js) VISUALIZATION"""

# Folium selected as to add zoom, pan, hover tooltips and layer toggles features
import folium
from folium.plugins import HeatMap, HeatMapWithTime

from app.models import AnalysisRequest, AnalysisResult

# Distinguished color palette for route visualization 
GUARD_COLORS = ['gray', 'darkgreen', 'beige', 'cadetblue', 'purple']

def generate_map(request: AnalysisRequest, result: AnalysisRequest, base_lat: float = 40.7128, base_lon: float = -74.0060) -> str:
    facility = request.facility
    # scale factor - 1 facility unit = 0.00001 degrees(1.11 meters)
    scale = 0.000045
    center_lat = base_lat + (facility.height / 2) * scale 
    center_lon = base_lon + (facility.width / 2) * scale 

    # Map
    m = folium.Map( location=[center_lat, center_lon],
                   zoom_start = 17, 
                   max_zoom = 49,
                   tiles=None, )
    
    # control over layout and theme
    folium.TileLayer(
        tiles ="cartodbdark_matter", name = "Dark Thme", attr = "CartoDB" ).add_to(m)
    
    

    # Draw each guard's patrol route as a coloured polyline. 
    for i, route in enumerate(request.routes):
        color = GUARD_COLORS[i % len(GUARD_COLORS)]
        coordinates = [[base_lat + wp.y * scale, base_lon + wp.x * scale] for wp in route.waypoints]
        folium.PolyLine(
            locations=coordinates,
            color=color,
            weight=3,
            opacity=0.8,
            tooltip=f"Guard {route.guard_id}",
        ).add_to(m)
        folium.Marker(
            location=[base_lat + route.waypoints[0].y * scale, base_lon + route.waypoints[0].x * scale],
            popup=f"Guard {route.guard_id} - Start",
            icon=folium.Icon(color=color, icon="user", prefix="fa"),
        ).add_to(m)

        # Mark initialization with a pin
        folium.Marker(
            location=[route.waypoints[0].y, route.waypoints[0].x],
            popup=f"Guard{route.guard_id} - Start",
            icon=folium.Icon(color=color, icon="user", prefix="fa"), #FONT-AWESOME
        ).add_to(m)
    
    # Heatmap signatures
        
    if result.risk_zones:
        """ Convert each risk zone into a [lat, lon, weight] triplet.
        The weight is 1.0 - coverage_score, so cells with the lowest
        coverage get the hottest color.
        """
        heat_data = [
            [base_lat + rz.center_y * scale, base_lon + rz.center_x * scale, 1.0 - rz.coverage_score]
            for rz in result.risk_zones
        ]
        HeatMap(
            heat_data,
            name="Risk Zones",
            radius=20,
            blur=15,
            gradient={0.4: "yellow", 0.65: "orange", 1: "red"},
        ).add_to(m)

        # Mark CRITICAL severity zones with red circle markers
        for rz in result.risk_zones:
            if rz.severity == "CRITICAL":
                # Render critical zones via red dots
                folium.CircleMarker(
                    location=[base_lat + rz.center_y * scale, base_lon + rz.center_x * scale],
                    radius=4,
                    color="red",
                    fill=True,
                    fill_opacity=0.7,
                    popup=f"RISK ZONE<br>Score: {rz.coverage_score}<br>Severity: {rz.severity}",
                ).add_to(m)
 
    # Add a layer toggle control and return the full HTML
    folium.LayerControl().add_to(m)

    return m._repr_html_()

"""
Temporal Map:
 Animated map with risk zones displayed through the windows. Patrol routes are drawn as faint polylines.
 Render an animaed heatmap with a playback slider
"""
def generate_temporal_map(request: AnalysisRequest, temporal_results: list[dict]) -> str:
    """Generate an animated heatmap showing risk zones over time."""
    facility = request.facility
    center_lat = facility.height / 2
    center_lon = facility.width / 2

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles=None,
    )
    folium.TileLayer(
        tiles="cartodbdark_matter", name="Dark Theme", attr="CartoDB"
    ).add_to(m)
    m.fit_bounds([[0, 0], [facility.height, facility.width]])

    # Build time-series data: one list of [lat, lng, weight] per window
    heat_data_time = []
    time_index = []

    for window in temporal_results:
        window_points = [
            [cell["center_y"], cell["center_x"], 1.0 - cell["coverage_score"]]
            for cell in window["risk_cells"]
        ]
        heat_data_time.append(window_points)
        time_index.append(
            f"{int(window['window_start'])}s - {int(window['window_end'])}s"
        )

    # Animate risk zones with a time slider
    HeatMapWithTime(
        heat_data_time,
        index=time_index,
        auto_play=True,
        max_opacity=0.6,
        radius=20,
        name="Temporal Risk",
    ).add_to(m)

    # Add patrol routes for reference
    for i, route in enumerate(request.routes):
        color = GUARD_COLORS[i % len(GUARD_COLORS)]
        coordinates = [[wp.y, wp.x] for wp in route.waypoints]
        folium.PolyLine(
            locations=coordinates,
            color=color,
            weight=2,
            opacity=0.5,
            tooltip=f"Guard {route.guard_id}",
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m._repr_html_()




""" verify no syntax errors through running
python -c "from app.visualization import generate_map; print('visualization module loaded')"
"""
