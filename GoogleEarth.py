import ee
import pandas as pd
from DBconn.db_connection import engine
import numpy as np

ee.Authenticate()
ee.Initialize(project="avalanche-project-456602")

dem = ee.Image('NASA/NASADEM_HGT/001').select('elevation')

elevation = dem.select('elevation')

slope = ee.Terrain.slope(elevation)

aspect = ee.Terrain.aspect(elevation)


def get_missing_values(row):
    point = ee.Geometry.Point(row['lon'], row['lat'])

    if pd.isnull(row['elevation']):
        elevation_value = elevation.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=30  # Scale in meters
        ).get('elevation').getInfo()
    else:
        elevation_value = row['elevation']

    if pd.isnull(row['start_angle']):
        slope_value = slope.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=30
        ).get('slope').getInfo()
    else:
        slope_value = row['start_angle']

    if pd.isnull(row['aspect']):
        aspect_value = aspect.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=30
        ).get('aspect').getInfo()
    else:
        aspect_value = row['aspect']

    return elevation_value, slope_value, aspect_value
