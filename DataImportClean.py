import pandas as pd
import numpy as np
from DBconn.db_connection import engine
from GoogleEarth import get_missing_values

incident_summary = pd.read_sql_query(
    "SELECT id, forecast_region, ST_X(coord) as lat, ST_Y(coord) as lon FROM incident_summary_nonfatal", engine)

avalanche_summary = pd.read_sql_query(
    "SELECT id, elevation, start_angle, aspect FROM avalanches_nonfatal", engine)


forecast_summary = pd.read_sql_query(
    "SELECT id, alp_rating,tln_rating, btl_rating, confidence FROM forecast_summary", engine)

forecast_problems = pd.read_sql(
    "SELECT id,problem, elevation AS problem_elevation, aspect AS problem_aspect,likelihood, size FROM forecast_problems", engine)


avalanche_merge = pd.merge(pd.merge(pd.merge(incident_summary, avalanche_summary,
                           on='id'), forecast_summary, on='id'), forecast_problems, on='id').drop(['id'], axis=1)

# using google earth engine to fill in elevation, slope and aspect values
for index, row in avalanche_merge.loc[
    avalanche_merge[['elevation', 'aspect',
                     'start_angle']].isnull().any(axis=1)
].iterrows():
    elevation_value, slope_value, aspect_value = get_missing_values(row)
    avalanche_merge.at[index, 'elevation'] = elevation_value
    avalanche_merge.at[index, 'aspect'] = aspect_value
    avalanche_merge.at[index, 'start_angle'] = slope_value

output_file = 'avalanche_merge.json'
avalanche_merge.to_json(output_file, orient='records', lines=True)
