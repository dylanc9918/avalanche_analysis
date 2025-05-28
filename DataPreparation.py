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
    "SELECT * FROM weather_api_complete", engine)


forecast_summary = pd.read_sql_query(
    "SELECT id, alp_rating,tln_rating, btl_rating, confidence FROM forecast_summary", engine)

forecast_problems = pd.read_sql(
    "SELECT id,problem, elevation AS problem_elevation, aspect AS problem_aspect,likelihood, size FROM forecast_problems", engine)


incident_dates = weather_api.groupby('id')['date'].max().reset_index()
incident_dates = incident_dates.rename(columns={'date': 'incident_date'})

weather_api = pd.merge(weather_api, incident_dates, on='id', how='left')

# Calculate n_days_before for each row
weather_api['n_days_before'] = (
    weather_api['incident_date'] - weather_api['date'])


weather_api['n_days_before'] = weather_api['n_days_before'].map(
    lambda x: x.days)

# Create the n_label column (e.g., n_0, n_1, ...)
weather_api['date'] = 'n_' + weather_api['n_days_before'].astype(str)

weather_vars = [col for col in weather_api.columns if col not in [
    'id', 'date', 'incident_date', 'n_days_before']]

weather_pivot = weather_api.pivot_table(
    index='id',
    columns='date',
    values=weather_vars
)

# Flatten MultiIndex columns: (max_temp, n_0) -> n_0_max_temp
weather_pivot.columns = [f"{col[0]}_{col[1]}" for col in weather_pivot.columns]
weather_pivot = weather_pivot.reset_index()


avalanche_merge = pd.merge(pd.merge(pd.merge(pd.merge(incident_summary, avalanche_summary,
                           on='id'), forecast_summary, on='id'), forecast_problems, on='id'), weather_pivot, on='id')

try:
    existing_data = pd.read_json('prepped_merge_data.json', lines=True)
except FileNotFoundError:
    print("prepped_merge_data.json not found. Assuming no existing data.")
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

output_file = 'calculated_merge_data.json'
merged_data.to_json(output_file, orient='records', lines=True)
