
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.svm import OneClassSVM
from sklearn.pipeline import Pipeline
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, precision_score
import pandas as pd
import numpy as np
import re


def convert_to_binary(column, pattern):
    """Function to extract the binary encodings in the column."""
    return column.str.extract(pattern).fillna(0).agg(''.join, axis=1).astype(int)


def aspect_to_cardinal(aspect):
    """
    Convert aspect in degrees to cardinal direction.
    """

    if (aspect >= 337.5 or aspect < 22.5):
        return "N"
    elif (aspect >= 22.5 and aspect < 67.5):
        return "NE"
    elif (aspect >= 67.5 and aspect < 112.5):
        return "E"
    elif (aspect >= 112.5 and aspect < 157.5):
        return "SE"
    elif (aspect >= 157.5 and aspect < 202.5):
        return "S"
    elif (aspect >= 202.5 and aspect < 247.5):
        return "SW"
    elif (aspect >= 247.5 and aspect < 292.5):
        return "W"
    elif (aspect >= 292.5 and aspect < 337.5):
        return "NW"
    else:
        return "Unknown"


def process_avalanche_data(df):
    """pivot the problems into columns and extract binary values."""
    # Extract binary values for elevation and aspect
    df['problem_elevation_binary'] = convert_to_binary(
        df['problem_elevation'], r'(\d)-(\d)-(\d)')
    df['problem_aspect_binary'] = convert_to_binary(
        df['problem_aspect'], r'(\d)-(\d)-(\d)-(\d)-(\d)-(\d)-(\d)-(\d)')

    pivoted = df.pivot_table(
        index=['lat', 'lon', 'elevation', 'forecast_region', 'start_angle', 'confidence', 'aspect', 'alp_rating', 'tln_rating', 'btl_rating', 'size_min',
               'size_max', 'likelihood_min', 'likelihood_max'],
        columns='problem',
        values=['problem_elevation_binary',
                'problem_aspect_binary'],
        aggfunc='first'
    )

    pivoted.columns = [f"{col[1]}_{col[0]}" for col in pivoted.columns]

    # Reset the index to make lat and lon regular columns
    pivoted = pivoted.reset_index()

    return pivoted


# Load data
df = pd.read_json("avalanche_merge.json", lines=True)

# setting ordinal order for ordinal features
ordinal_order = {
    'alp_rating': ['low', 'moderate', 'considerable', 'high', 'extreme'],
    'tln_rating': ['low', 'moderate', 'considerable', 'high', 'extreme'],
    'btl_rating': ['norating', 'low', 'moderate', 'considerable', 'high', 'extreme'],
    'confidence': ['notdefined', 'low', 'moderate', 'high'],
    'likelihood_min': ['unlikely', 'possible',
                       'likely', 'verylikely', 'certain'],
    'likelihood_max': ['unlikely', 'possible',
                       'likely', 'verylikely', 'certain'],

}


# Parse features for easier encoding
df[['size_min', 'size_max']] = df['size'].str.extract(
    r'size-(\d+)-(\d+)', expand=True).astype(int)
df['likelihood'] = df['likelihood'].str.replace('_en', '')
df[['likelihood_min', 'likelihood_max']] = df['likelihood'].str.extract(
    r'likelihood-([a-zA-Z]+)(?:_([a-zA-Z]+))?'
)

df['likelihood_min'] = df['likelihood_min']
df['likelihood_max'] = df['likelihood_max'].fillna(df['likelihood_min'])


avalanche_wrangled = process_avalanche_data(df).drop(['lat', 'lon'], axis=1)


avalanche_wrangled['aspect'] = avalanche_wrangled['aspect'].apply(
    lambda x: aspect_to_cardinal(x) if isinstance(x, (int, float)) else x)


avalanche_wrangled[avalanche_wrangled.select_dtypes(include=['float64']).columns] = avalanche_wrangled[avalanche_wrangled.select_dtypes(
    include=['float64']).columns].fillna(0).astype(int)


ordinal_columns = avalanche_wrangled[ordinal_order.keys()].columns

categorical_columns = avalanche_wrangled.select_dtypes(
    include=['object', 'category']).columns.drop(ordinal_order.keys())

numerical_columns = avalanche_wrangled.select_dtypes(
    exclude=['object', 'category']).columns


numeric_preprocessor = Pipeline(
    steps=[
        ("imputation_constant", SimpleImputer(strategy="constant", fill_value=0))
    ]
)

ordinal_preprocessor = Pipeline(
    steps=[
        ("imputation_constant", SimpleImputer(
            strategy="constant", fill_value="unknown")),
        ("ordinal", OrdinalEncoder(categories=[
         ordinal_order[col] for col in ordinal_columns]))
    ]
)
categorical_preprocessor = Pipeline(
    steps=[
        ("imputation_constant", SimpleImputer(
            strategy="constant", fill_value="unknown")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_preprocessor, numerical_columns),
        ("ord", ordinal_preprocessor, ordinal_columns),
        ("cat", categorical_preprocessor, categorical_columns)
    ]
)

pipeline = Pipeline(steps=[
    # ("preprocessor", preprocessor),
    ("isolation_forest", IsolationForest(
        n_estimators=100, contamination=0.02, random_state=42))
])


X_train, X_test = train_test_split(
    avalanche_wrangled, test_size=0.2, random_state=42)


pipeline.fit(X_train)


# Predict on the training and testing data
y_train_pred = pipeline.predict(X_train)
y_test_pred = pipeline.predict(X_test)

# Convert predictions to binary (1 = normal, -1 = anomaly)
y_train_pred = np.where(y_train_pred == 1, 0, 1)
y_test_pred = np.where(y_test_pred == 1, 0, 1)


# Evaluate the model
print("Training Data Evaluation:")
print(classification_report(np.zeros(len(y_train_pred)), y_train_pred))

print("Testing Data Evaluation:")
print(classification_report(np.zeros(len(y_test_pred)), y_test_pred))


print('done')
