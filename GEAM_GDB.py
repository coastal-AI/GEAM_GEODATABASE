import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry import Point, Polygon
from bokeh.io import output_file, save, show
from bokeh.models import TapTool, CustomJS, HoverTool, WheelZoomTool
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Div
from bokeh.models.tiles import WMTSTileSource
from bokeh.layouts import column


# Load the data
groundtruth_df = pd.read_excel('/Users/fer/Documents/PYTHON/15_GEAM_GDB_GitHub/data/GROUNDTRUTH_DB.xlsx')
groundtruth_gdf = gpd.GeoDataFrame(groundtruth_df, geometry=[Point(xy) for xy in zip(groundtruth_df['dwc:decimalLongitude'], groundtruth_df['dwc:decimalLatitude'])], crs='EPSG:4326')

stations_df = pd.read_excel('/Users/fer/Documents/PYTHON/15_GEAM_GDB_GitHub/data/STATIONS_DB.xlsx')
stations_gdf = gpd.GeoDataFrame(stations_df, geometry=[Point(xy) for xy in zip(stations_df['dwc:decimalLongitude'], stations_df['dwc:decimalLatitude'])], crs='EPSG:4326')

uv_df = pd.read_excel('/Users/fer/Documents/PYTHON/15_GEAM_GDB_GitHub/data/UV_DB.xlsx')
uv_df['geometry'] = uv_df['dwc:footprintWKT'].apply(wkt.loads)  
uv_gdf = gpd.GeoDataFrame(uv_df, geometry='geometry', crs="EPSG:4326")

drone_df = pd.read_excel('/Users/fer/Documents/PYTHON/15_GEAM_GDB_GitHub/data/DRONE_DB.xlsx')
drone_df['geometry'] = drone_df['dwc:footprintWKT'].apply(wkt.loads)  
drone_gdf = gpd.GeoDataFrame(drone_df, geometry='geometry', crs="EPSG:4326")

# Convert all GeoDataFrames to EPSG:3857
groundtruth_gdf = groundtruth_gdf.to_crs(epsg=3857)
drone_gdf = drone_gdf.to_crs(epsg=3857)
uv_gdf = uv_gdf.to_crs(epsg=3857)
stations_gdf = stations_gdf.to_crs(epsg=3857)

# Prepare data sources for different types of data
groundtruth_source = ColumnDataSource(data={
    'x': groundtruth_gdf.geometry.x,
    'y': groundtruth_gdf.geometry.y,
    'occurrenceID': groundtruth_gdf['dwc:occurrenceID']
})

stations_source = ColumnDataSource(data={
    'x': stations_gdf.geometry.x,
    'y': stations_gdf.geometry.y,
    'locationID': stations_gdf['dwc:locationID']
})

# Extract xs and ys as lists of lists for underwater video data
uv_data = {
    'xs': [list(geom.xy[0]) for geom in uv_gdf.geometry],
    'ys': [list(geom.xy[1]) for geom in uv_gdf.geometry],
    'eventID': uv_gdf['dwc:eventID']
}
uv_source = ColumnDataSource(data=uv_data)

# Prepare data for drone polygons
drone_data = {
    'xs': [list(geom.exterior.coords.xy[0]) for geom in drone_gdf.geometry],
    'ys': [list(geom.exterior.coords.xy[1]) for geom in drone_gdf.geometry],
    'eventID': drone_gdf['dwc:eventID']
}
drone_source = ColumnDataSource(data=drone_data)

# Create the map plot with CartoLight tiles
tile_url = 'https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png'
tile_source = WMTSTileSource(url=tile_url)

# Initialize figure with required tools and responsive sizing
map_figure = figure(
    x_axis_type="mercator",
    y_axis_type="mercator",
    tools="tap, wheel_zoom, pan, reset",
    sizing_mode="stretch_both"  # Make the map fill available space
)
map_figure.add_tile(tile_source)
map_figure.toolbar.active_scroll = map_figure.select_one(WheelZoomTool)

# Plot the data points and lines
underwater_video_renderer = map_figure.multi_line(xs='xs', ys='ys', source=uv_source, line_width=3, color='blue', legend_label='Underwater video tracks')
stations_renderer = map_figure.scatter('x', 'y', source=stations_source, size=5, color='red', legend_label='Sampling stations')
groundtruth_renderer = map_figure.scatter('x', 'y', source=groundtruth_source, size=3, color='green', legend_label='Species presence/absence')
drone_renderer = map_figure.patches('xs', 'ys', source=drone_source, fill_alpha=0.2, line_width=2, fill_color="grey", legend_label='Drone surveys')

# Customize the legend
map_figure.legend.title_text_font_size = '12pt'
map_figure.legend.label_text_font_size = '10pt'
map_figure.legend.location = 'top_left'
map_figure.legend.click_policy = 'hide'

# Add HoverTools for displaying eventID and occurrenceID
hover_tool_event = HoverTool(renderers=[stations_renderer], tooltips=[("Location ID", "@locationID")])
hover_tool_occurrence = HoverTool(renderers=[groundtruth_renderer], tooltips=[("Occurrence ID", "@occurrenceID")])
hover_tool_video = HoverTool(renderers=[underwater_video_renderer], tooltips=[("Event ID", "@eventID")])
hover_tool_drone = HoverTool(renderers=[drone_renderer], tooltips=[("Event ID", "@eventID")])
map_figure.add_tools(hover_tool_event, hover_tool_occurrence, hover_tool_video, hover_tool_drone)

# Interactive Divs for displaying IDs
event_id_div = Div(text="", width=200, height=100)
occurrence_id_div = Div(text="", width=200, height=100)

# Title for the visualization
main_title = Div(text="""
    <div style='text-align: center;'>
        <div style='font-size: 2.5vw; font-weight: bold;'>SEAGRASS ECOLOGY GROUP GEODATABASE</div>
        <div style='font-size: 2vw;'>IEO-CSIC</div>
        <div style='font-size: 0.5vw; '>_____________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________</div>
    </div>
""", sizing_mode="stretch_width")

# Layout setup with stretch_both for full screen use
layout = column(main_title, map_figure, sizing_mode="stretch_both")
output_file('/Users/fer/Documents/PYTHON/15_GEAM_GDB_GitHub/docs/index.html', title="GEAM GEODATABASE")

# Save and display
save(layout)
show(layout)
