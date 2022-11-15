import ee 
import geopandas as gpd
import folium
import pprint

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
    
ee.Initialize()


sheng = gpd.read_file('gadm41_CHN_2.shp',method='vertex')
xsbn= sheng[sheng['GID_2'] == 'CHN.30.14_1'].bounds
collection = ee.ImageCollection("LANDSAT/LT04/C02/T2_L2")
geom = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([xsbn['minx'].iloc[0],xsbn['miny'].iloc[0]])),
    ee.Feature(ee.Geometry.Point([xsbn['minx'].iloc[0],xsbn['maxy'].iloc[0]])),
    ee.Feature(ee.Geometry.Point([xsbn['maxx'].iloc[0],xsbn['maxy'].iloc[0]])),
    ee.Feature(ee.Geometry.Point([xsbn['maxx'].iloc[0],xsbn['miny'].iloc[0]]))])
xsbncol = collection.filterDate('1990-01-01','1999-12-31').filterBounds(geom)
pprint.pprint(xsbncol.size())

def evi(img):
    nir=img.select('SR_B4').divide(10000)
    red = img.select('SR_B3').divide(10000)
    blue = img.select('SR_B1').divide(10000)
    numerator = (nir.subtract(red)).multiply(2.5)
    denom1 = red.multiply(6)
    denom2 = blue.multiply(7.5)
    denomEVI = nir.add(denom1).subtract(denom2).add(1)
    
    img = numerator.divide(denomEVI).rename('EVI')
    return img

#xsbnEVI = xsbncol.map(evi)
#xsevimean = xsbnEVI.reduce(ee.Reducer.mean())
eviparam = {'bands':['EVI_mean'],'min':-1,'max':1,'palette':['red','white','green']}
map1 = folium.Map(location = [22,101],zoom_start=10)
years=range(1990,2000)
for i in years:
    workingcol = xsbncol.filterDate(str(i)+"-01-01",str(i)+"-12-31")
    eviimg = workingcol.map(evi).reduce(ee.Reducer.mean())
    folium.Map.add_ee_layer(map1,eviimg,eviparam,str(i)+' EVI mean')


#for i in percentiles:
#    xsbnperc = xsbnEVI.reduce(ee.Reducer.percentile([i]))
#    map2 = folium.Map.add_ee_layer(map1,xsbnperc,{'min':-1,'max':1,'palette':['red','white','green']},str(i)+'%')
#map2 = folium.Map.add_ee_layer(map1,xsevimean,eviparam,'EVI Mean')
folium.LayerControl().add_to(map1)
map1.save('map4.html')

