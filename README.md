# Avalanche Learning Model
The purpose of this model is to analyze avalanche data for anomaly detection and feature importance analysis. It uses machine learning techniques to preprocess, transform, and model avalanche-related data to identify patterns and outliers. The key objectives include:

Data Preprocessing:

Cleaning and transforming raw avalanche data.
Parsing features like size, likelihood, and aspect for easier encoding and analysis.
Feature Engineering:

Converting categorical features (e.g., slope aspect) into numerical representations.
Pivoting problem-related columns into separate features for each avalanche problem.
Anomaly Detection:

Using models like Isolation Forest to detect anomalies in avalanche data.
Explainability:

Leveraging SHAP (SHapley Additive exPlanations) to interpret the model's predictions and understand feature importance.
The model is designed to assist in identifying unusual avalanche patterns and understanding the factors contributing to avalanche risks.
