# Telecom Customer Churn Prediction

Predicting customer churn for a telecom company using an end-to-end data pipeline covering synthetic data generation, SQL analysis, feature engineering, and XGBoost classification.

## Overview

This project builds a reproducible churn prediction pipeline:

1. Synthetic telecom customer data generation
2. SQL-based exploratory analysis of churn patterns and customer behavior
3. Feature engineering with pandas
4. XGBoost classification for churn prediction

**Result:** The baseline XGBoost model achieved a ROC-AUC of **0.9713** on the test set *(synthetic data — not a claim of real-world performance)*.

## Project Structure

```text
├── data/                    # Generated/raw data files
├── day3_xgboost/            # XGBoost model outputs
├── query_outputs/           # Results from SQL analysis
├── generate_data.py         # Synthetic data generation
├── pandas_pipeline.py       # Feature engineering pipeline
├── xgboost_pipeline.py      # Model training pipeline
├── schema.sql               # Database schema
├── queries.sql              # Core SQL analysis queries
├── window_analysis.sql      # Time-window churn analysis
├── setup_db.sh              # Database setup script
├── run_pipeline.sh          # Runs the data pipeline end-to-end
├── run_verification.sh      # Verifies pipeline outputs
└── run_window_analysis.sh   # Runs window-based SQL analysis
```

## How to Run

```bash
# 1. Set up the database
./setup_db.sh

# 2. Generate synthetic data
python generate_data.py

# 3. Run the pipeline
./run_pipeline.sh

# 4. Verify outputs
./run_verification.sh
```

## Results

* **Model:** XGBoost classifier
* **ROC-AUC:** 0.9713 *(on synthetic/generated data — not a claim of real-world performance)*
* SQL analysis used to investigate customer churn patterns and behavior
* Feature engineering incorporated behavioral and usage-window features

## Tech Stack

* **Python:** pandas, XGBoost
* **SQL:** Database setup and behavioral analysis
* **Shell scripting:** Pipeline orchestration and verification

## Future Work

* Hyperparameter tuning
* Cloud deployment
* Prediction API
* Dashboard for churn predictions

## Author

**Harika Etikela**

[GitHub](https://github.com/harikaetikela) · [LinkedIn](https://linkedin.com/in/harikaetikela13)
