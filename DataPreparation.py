import pandas as pd
import numpy as np
from DBconn.db_connection import engine
from GoogleEarth import get_missing_values
# THis is the main file to import and combine all the data from the database as well as fill in missing values using Google Earth Engine
incident_summary = pd.read_sql_query(
    "SELECT id, date, forecast_region, ST_X(coord) as lat, ST_Y(coord) as lon FROM incident_summary_nonfatal", engine)

avalanche_summary = pd.read_sql_query(
    "SELECT id, elevation, start_angle, aspect FROM avalanches_nonfatal", engine)

weather_api = pd.read_sql_query(
    "SELECT id, wind_dir, wind_speed_max, snowfall_sum, temperature_max FROM weather_api", engine)


forecast_summary = pd.read_sql_query(
    "SELECT id, alp_rating,tln_rating, btl_rating, confidence FROM forecast_summary", engine)

forecast_problems = pd.read_sql(
    "SELECT id,problem, elevation AS problem_elevation, aspect AS problem_aspect,likelihood, size FROM forecast_problems", engine)


avalanche_merge = pd.merge(pd.merge(pd.merge(pd.merge(incident_summary, avalanche_summary,
                           on='id'), forecast_summary, on='id'), forecast_problems, on='id'), weather_api, on='id')

try:
    existing_data = pd.read_json('merge_data.json', lines=True)
except FileNotFoundError:
    print("calculated_merge_data.json not found. Assuming no existing data.")
    existing_data = pd.DataFrame(columns=['id'])

new_ids = set(avalanche_merge['id']) - set(existing_data['id'])

new_data = avalanche_merge[avalanche_merge['id'].isin(new_ids)]

print(f"Number of new records to add: {len(new_data)}")

# missing values in the data
missing_values_df = new_data.loc[
    new_data[['elevation', 'aspect',
              'start_angle']].isnull().any(axis=1)
]

missing_values_grouped = missing_values_df.groupby('id').first()

calculated_values = {}

# Calculate missing values for each unique id
for id, row in missing_values_grouped.iterrows():
    elevation_value, slope_value, aspect_value = get_missing_values(row)
    calculated_values[id] = {
        'elevation': elevation_value,
        'aspect': aspect_value,
        'start_angle': slope_value
    }
    print(f"Missing values filled for id: {id}")

# Apply the calculated values back to the DataFrame
for id, values in calculated_values.items():
    new_data.loc[avalanche_merge['id'] == id, ['elevation', 'aspect', 'start_angle']] = \
        values['elevation'], values['aspect'], values['start_angle']

complete_df = pd.concat([existing_data, new_data], ignore_index=True)

columns_to_update = ['elevation', 'aspect', 'start_angle']

# Merge the existing data with the new data on 'id'
complete_df = complete_df[['id'] + columns_to_update]
merged_data = pd.merge(
    avalanche_merge.drop(columns=['elevation', 'aspect', 'start_angle']),
    complete_df,
    on='id',
    how='left',
    suffixes=('', '_existing')
)

merged_data = merged_data.drop_duplicates()

output_file = 'prepped_merge_data.json'
merged_data.to_json(output_file, orient='records', lines=True)
