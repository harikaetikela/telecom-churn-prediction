# Day 3: XGBoost Churn Prediction Model

## Overview
Built an XGBoost classifier to predict customer churn using a preprocessing pipeline (StandardScaler + OneHotEncoder) combined with the model into a single sklearn Pipeline object.

## Why XGBoost?
XGBoost handles non-linear relationships between features well and provides built-in feature importance, making it both accurate and interpretable - important for explaining predictions to a retention team.

## Model Configuration
- max_depth: 6
- learning_rate: 0.1
- n_estimators: 100
- subsample: 0.8
- colsample_bytree: 0.8
- gamma: 1

subsample and colsample_bytree were both set below 1.0 intentionally as regularization, so each tree sees a random subset of rows and features - this reduces overfitting risk.

## Results (Test Set, 20,000 customers)
| Metric | Score |
|--------|-------|
| Accuracy | 90.41% |
| Precision | 78.65% |
| Recall | 89.10% |
| F1 Score | 83.55% |
| ROC-AUC | 97.13% |

## Top Churn Drivers
1. Tenure (52.8% importance)
2. Contract Duration (21.0% importance)
3. Complaint Trend (9.1% importance)

These three features alone account for 82.9% of the model's decision-making.

## Business Insight
Customer lifecycle stage - not billing amount or demographics - is the dominant churn signal. This aligns with earlier SQL analysis showing month-to-month customers churn at 36.7% vs. 15.0% for two-year contract holders.

Recommended actions:
1. Proactive retention outreach for customers in their first 6 months
2. Incentivize upgrading from month-to-month to longer-term contracts

## Files
- xgboost_pipeline.py - training script
- churn_model_v1.pkl - trained model pipeline
- feature_importance.csv - full feature ranking
- feature_importance.png - visualization

