# Avalanche Learning Model

The **Avalanche Learning Model** analyzes avalanche data for anomaly detection and feature importance using machine learning. It is designed to help identify unusual avalanche patterns and understand the factors contributing to avalanche risks.

---

## 🔑 Key Objectives

### 📦 Data Preprocessing

- Cleans and transforms raw avalanche data.
- Parses features like size, likelihood, and aspect for easier encoding and analysis.

### 🛠️ Feature Engineering

- Converts categorical features (e.g., slope aspect) into numerical representations (e.g., sine/cosine encoding for circular variables).
- Pivots problem-related columns into separate features for each avalanche problem.

### 🚨 Anomaly Detection

- Uses models like **Isolation Forest** to detect anomalies in avalanche data.

### 🔍 Explainability

- Leverages **SHAP** (SHapley Additive exPlanations) to interpret model predictions and understand feature importance.

---

## 📂 File Breakdown

### `AnalysisReport.ipynb`

**Purpose:**  
End-to-end data analysis and modeling notebook.

**Contents:**

- Data loading and cleaning.
- Exploratory Data Analysis (EDA).
- Feature engineering (encoding, transformation).
- Model training using Isolation Forest.
- SHAP-based feature importance and visualization.
- Pairplots and other visualizations for insights.

---

### `ModelTrain.ipynb`

**Purpose:**  
Focused notebook for model training and preprocessing pipeline development.

**Contents:**

- Helper functions for data wrangling and feature extraction.
- Parsing and encoding of categorical and ordinal features.
- Construction of preprocessing pipelines using scikit-learn.
- Model fitting and anomaly scoring.
- SHAP explainability for model interpretation.

---

### `prepped_merge_data.json`

**Purpose:**  
Preprocessed avalanche datasets used as input for analysis and modeling.

**Contents:**

- Cleaned and merged avalanche incident records.
- Includes features such as location, weather, forecasted problems, and more.

---

## ⚙️ Usage

### Data Preparation

Ensure the JSON data files are present in the working directory.

### Run Notebooks

- Use `AnalysisReport.ipynb` for a full walkthrough from data cleaning to model interpretation.

### Model Interpretation

- Visualize feature importance and anomaly scores using built-in SHAP and seaborn plots.

---

## 🧰 Requirements

- Python 3.x
- `pandas`, `numpy`, `scikit-learn`, `shap`, `seaborn`, `matplotlib`

---

## 🧠 Project Structure

This project helps researchers and practitioners:

- Explore avalanche data.
- Detect unusual patterns.
- Understand key risk factors using interpretable machine learning.
