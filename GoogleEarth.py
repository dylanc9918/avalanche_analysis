import ee
import pandas as pd

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


def aspect_to_cardinal(aspect):
    """
    Convert aspect in degrees to cardinal direction.
    """

    if (aspect >= 337.5 or aspect < 22.5):
        return "North"
    elif (aspect >= 22.5 and aspect < 67.5):
        return "Northeast"
    elif (aspect >= 67.5 and aspect < 112.5):
        return "East"
    elif (aspect >= 112.5 and aspect < 157.5):
        return "Southeast"
    elif (aspect >= 157.5 and aspect < 202.5):
        return "South"
    elif (aspect >= 202.5 and aspect < 247.5):
        return "Southwest"
    elif (aspect >= 247.5 and aspect < 292.5):
        return "West"
    elif (aspect >= 292.5 and aspect < 337.5):
        return "Northwest"
    else:
        return "Unknown"
