import ee 
import folium
import geopandas as gpd
import pprint as pp
import os 
import pathlib


if pathlib.Path.cwd() == pathlib.PosixPath('/Users/timothyclark/Documents/Python/remote_sensing'):
    os.chdir('/Users/timothyclark/Documents/Python/remote_sensing/EEPractice')

def add_ee_layer(self,img,visparams,name):
    map_id_dict = ee.Image(img).getMapId(visparams)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
        name = name,
        overlay=True,
        control=True
    ).add_to(self)
folium.Map.add_ee_layer = add_ee_layer
    
def gdb_to_eefeature():
    pass

ee.Initialize()

sheng = gpd.read_file('gadm41_CHN_2.shp',method='vertex')
xsbn= sheng[sheng['GID_2'] == 'CHN.30.14_1'].bounds
collection = ee.ImageCollection("LANDSAT/LT04/C02/T2_L2")
geom = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([xsbn['minx'].iloc[0],xsbn['miny'].iloc[0]])),
    ee.Feature(ee.Geometry.Point([xsbn['minx'].iloc[0],xsbn['maxy'].iloc[0]])),
    ee.Feature(ee.Geometry.Point([xsbn['maxx'].iloc[0],xsbn['maxy'].iloc[0]])),
    ee.Feature(ee.Geometry.Point([xsbn['maxx'].iloc[0],xsbn['miny'].iloc[0]]))])
xsbncol = collection.filterDate('1990-01-01','1999-12-31').filterBounds(geom)
a = xsbncol.size 
print(a)
