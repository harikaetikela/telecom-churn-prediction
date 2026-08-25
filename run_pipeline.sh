#!/bin/bash
set -e

echo "=== Running Pandas Cleaning and Feature Engineering Pipeline ==="
python3 pandas_pipeline.py

echo ""
echo "=== Verifying Output Features File ==="
if [ -f "data/churn_prediction_features.csv" ]; then
  echo "Success: data/churn_prediction_features.csv exists!"
  echo "Checking row and column counts in output file:"
  python3 -c "import pandas as pd; df = pd.read_csv('data/churn_prediction_features.csv'); print(f'Shape: {df.shape}'); print('\nColumns:'); print(list(df.columns)); print('\nMissing values per column:'); print(df.isna().sum())"
else
  echo "Error: data/churn_prediction_features.csv was not created."
  exit 1
fi
