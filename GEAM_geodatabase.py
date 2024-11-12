from bokeh.io import output_file, save, show
from bokeh.models import TapTool, CustomJS, HoverTool, WheelZoomTool
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Div
from bokeh.models.tiles import WMTSTileSource
from bokeh.layouts import column
from datetime import datetime

# Load the data
groundtruth_data = pd.read_excel('data/GROUNTRUTH_DB.xlsx')
stations_data = pd.read_excel('data/STATIONS_DB.xlsx')
uv_data = pd.read_excel('data/UV_DB.xlsx')
drone_data = pd.read_excel('data/DRONE_DB.xlsx')


# Prepare the current date for output file naming
current_date = datetime.now().strftime('%Y%m%d')

# Prepare data sources for different types of data
groundtruth_source = ColumnDataSource(data={
    'x': groundtruth_gdf.geometry.x,
    'y': groundtruth_gdf.geometry.y,
    'occurrenceID': groundtruth_gdf['occurrenceID']
})

stations_source = ColumnDataSource(data={
    'x': stations_gdf.geometry.x,
    'y': stations_gdf.geometry.y,
    'eventID': stations_gdf['eventID']
})

# Extract xs and ys as lists of lists for underwater video data
underwater_video_data = {
    'xs': [list(geom.xy[0]) for geom in underwater_video_gdf.geometry],
    'ys': [list(geom.xy[1]) for geom in underwater_video_gdf.geometry],
    'eventID': underwater_video_gdf['eventID']
}
underwater_video_source = ColumnDataSource(data=underwater_video_data)

# Prepare data for drone polygons
drone_data = {
    'xs': [list(geom.exterior.coords.xy[0]) for geom in drone_gdf.geometry],
    'ys': [list(geom.exterior.coords.xy[1]) for geom in drone_gdf.geometry],
    'eventID': drone_gdf['eventID']
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
underwater_video_renderer = map_figure.multi_line(xs='xs', ys='ys', source=underwater_video_source, line_width=3, color='blue', legend_label='Underwater video tracks')
stations_renderer = map_figure.scatter('x', 'y', source=stations_source, size=7, color='red', legend_label='Sampling stations')
groundtruth_renderer = map_figure.scatter('x', 'y', source=groundtruth_source, size=3, color='green', legend_label='Species presence/absence')
drone_renderer = map_figure.patches('xs', 'ys', source=drone_source, fill_alpha=0.2, line_width=2, fill_color="grey", legend_label='Drone surveys')

# Customize the legend
map_figure.legend.title_text_font_size = '12pt'
map_figure.legend.label_text_font_size = '10pt'
map_figure.legend.location = 'top_left'
map_figure.legend.click_policy = 'hide'

# Add HoverTools for displaying eventID and occurrenceID
hover_tool_event = HoverTool(renderers=[stations_renderer], tooltips=[("Event ID", "@eventID")])
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
output_file(f'/Users/fer/Documents/PYTHON/14_GEAM_GDB/{current_date}_GEAM_GDB.html', title="GEAM GEODATABASE")

# Save and display
save(layout)
show(layout)
