###################################
## WKT extract from orthomosaics ##
###################################

# This script allows to obtain the extend (WKT) and centroid of orthomosaics
# Required packages
library(raster)
library(sf)

# Process

MAP <- "/Users/jordi/Documents/Research/Projects/00 Hidden Deserts/2024TAVOLARA/20241023CalaGreca/Products/20241023CalaGraca.files/20241023CalaGraca.tif"

rMAP <- raster(MAP)
projection(rMAP)

extent_bounds <- extent(rMAP)
extent_polygon <- as(extent_bounds, "SpatialPolygons")
extent_polygon_sf <- st_as_sf(extent_polygon)
extent_wkt <- st_as_text(st_geometry(extent_polygon_sf))
print(extent_wkt)

centroid <- st_centroid(extent_polygon_sf)
print(centroid)
