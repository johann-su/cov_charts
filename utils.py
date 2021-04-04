import geopandas as gpd
import pandas as pd

from covid_charts import vars

def make_shapefiles():
    state = gpd.read_file('./data/vg2500_geo84/vg2500_bld.shp')
    county = gpd.read_file('./data/vg2500_geo84/vg2500_krs.shp')

    county['state'] = county.apply(lambda row: vars.RS[row['RS'][:2]], axis=1)

    state.to_file('./data/shapefiles_germany/shapefile_state')
    county.to_file('./data/shapefiles_germany/shapefile_county')