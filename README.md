# DM Mapping Project
As part of my PADI Divemaster course, I have a dive site mapping project. The following python script and html pages are scripts I wrote to help me ingest the data, transform it and display it using mapping tools.
This is is quite specific to my data collection and data collection methods. It's also no where near production quality code. No attempt at optimizations were made. I'm not a python developer so there are probably lots of things that could have
been done in a better way and a much more optimal way. Same goes for the javascript code that uses `mapbox-gl` .. I borrowed heavily form the examples they provide and made more of a proof of concept than anything else.

## write_data_to_layer_files.py
This script takes `DiveData.json` data, loads it in. Does some calculations and spits out a bunch of `geojson` files.
These files can then be used by Mapping software like qgis or online map tools like mapbox.

## site
The html code that is in this directory is used to show a map in the browser with the data and show tide predictions on each data point collected. It's a work in progress...
For testing there is a `docker-compose` and basic `Caddy` file to quickly spin up a http server to serve the files (Otherwise the browser will complain about fetches)

## Tools Used
### LatLong to UTM Converter
Easy Convert UTM to lat long and vise versa: https://www.latlong.net/lat-long-utm.html
### Mapbox
Mapbox for viewing map data in a browser: mapbox.com
### QGIS 
QGIS for quick loading and viewing of geojson layers on desktop: https://qgis.org/en/site/
#### QGIS Map Layers used
GeoNB offers map services, including GIS Layer maps that we can connect to using our GIS software

https://geonb.snb.ca/image/rest/services
GeoNB webapp map: https://geonb.snb.ca/geonb/

Using this data we can import different layers. For example: `Elevation/DEM_Shaded_Relief_MNE_Relief_Ombre (ImageServer)`
https://docs.mapbox.com/help/tutorials/mapbox-arcgis-qgis/
### GPS Logger on Android
https://play.google.com/store/apps/details?id=eu.basicairdata.graziano.gpslogger&hl=en_CA&gl=US

This tool allowed me to take a gps recording and export the raw data in `kml` format that's understood by most gis and mapping tools
`gps_app_data/` holds the data I got from it

### Python 
Python for pragmatically loading, transforming and writing down data in specific formats: https://www.python.org/
#### Dependencies
- Pandas for reading csv file: https://pypi.org/project/pandas/
- Fiona for writing to shapefile: https://pypi.org/project/Fiona/
- Pyproj for cartographic projections and coordinate transformations: https://pypi.org/project/pyproj/
### References
- Shapefile technical description: https://www.esri.com/content/dam/esrisites/sitecore-archive/Files/Pdfs/library/whitepapers/pdfs/shapefile.pdf
- GeoJson Specification: https://geojson.org/
- Tutorial on using python to write to shapefile: https://hatarilabs.com/ih-en/how-to-create-a-pointlinepolygon-shapefile-with-python-and-fiona-tutorial
- Polar coordinates to Cartesian coordinates: https://www.mathsisfun.com/polar-cartesian-coordinates.html
- https://ocefpaf.github.io/python4oceanographers/blog/2013/12/16/utm/
- https://vvvv.org/blog/polar-spherical-and-geographic-coordinates

## Notes
In cartesian notation
the conversion from polar coordinates are:

* x = r × cos( θ )
* y = r × sin( θ )

However, this assumes degree 0 to be pointing positive x axis.
Since in our case degree 0 is pointing north we want it to be positive y axis.
So in our case we should use:
* x = r × sin( θ )
* y = r × cos( θ )