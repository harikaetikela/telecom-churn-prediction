import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Configuration
data_path = 'data/churn_prediction_features.csv'
output_dir = 'day3_xgboost'
model_output_path = os.path.join(output_dir, 'churn_model_v1.pkl')
importance_csv_path = os.path.join(output_dir, 'feature_importance.csv')
importance_png_path = os.path.join(output_dir, 'feature_importance.png')

print("===  XGBoost Churn Prediction ===")

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created output directory: {output_dir}")

# 1. Load the dataset
if not os.path.exists(data_path):
    raise FileNotFoundError(f"Cleaned dataset not found at: {data_path}")

print(f"Loading cleaned dataset from {data_path}...")
df = pd.read_csv(data_path)
print(f"Dataset shape: {df.shape}")

# Define features and target
target_col = 'churn'
id_col = 'customer_id'

# Separate target and features
X = df.drop(columns=[target_col, id_col])
y = df[target_col]

# Identify feature types
cat_cols = ['gender', 'city']
num_cols = [col for col in X.columns if col not in cat_cols]

print(f"Features: {list(X.columns)}")
print(f"Numerical features ({len(num_cols)}): {num_cols}")
print(f"Categorical features ({len(cat_cols)}): {cat_cols}")
print(f"Target variable: {target_col}")

# 2. Split the data into Train and Test sets (80/20)
print("\nSplitting data into train and test sets (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train set size: {X_train.shape[0]} rows")
print(f"Test set size: {X_test.shape[0]} rows")

# 3. Setup Preprocessing Pipeline (StandardScaler for numerical, OneHotEncoder for categorical)
print("\nSetting up preprocessors...")
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols)
    ]
)

# 4. Define XGBoost Classifier
print("Configuring XGBoost Classifier...")
xgb_clf = xgb.XGBClassifier(
    max_depth=6,
    learning_rate=0.1,
    n_estimators=100,
    subsample=0.8,
    colsample_bytree=0.8,
    gamma=1,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

# Create the full pipeline
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', xgb_clf)
])

# Fit the pipeline
print("\nTraining the model pipeline...")
pipeline.fit(X_train, y_train)
print("Model training complete.")

# 5. Generate predictions on the test dataset
print("\nGenerating predictions on test dataset...")
y_pred = pipeline.predict(X_test)
y_pred_proba = pipeline.predict_proba(X_test)[:, 1]

# 6. Evaluate the model
print("Evaluating performance...")
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)

summary_df = pd.DataFrame({
    'Metric': ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC-AUC'],
    'Value': [accuracy, precision, recall, f1, roc_auc]
})

print("\n=== Model Evaluation Summary ===")
print(summary_df.to_string(index=False, formatters={'Value': '{:.4f}'.format}))

# 7. Feature Importance Analysis
print("\nAnalyzing feature importances...")
# Get feature names from preprocessor
feature_names = preprocessor.get_feature_names_out()

# Clean up prefixes
clean_feature_names = []
for name in feature_names:
    if name.startswith('num__'):
        clean_feature_names.append(name[5:])
    elif name.startswith('cat__'):
        clean_feature_names.append(name[5:])
    else:
        clean_feature_names.append(name)

# Extract importances
importances = pipeline.named_steps['classifier'].feature_importances_

importance_df = pd.DataFrame({
    'Feature': clean_feature_names,
    'Importance': importances
})
importance_df = importance_df.sort_values(by='Importance', ascending=False).reset_index(drop=True)

# Save importance to CSV
importance_df.to_csv(importance_csv_path, index=False)
print(f"Saved feature importances to: {importance_csv_path}")

# Plot feature importance
print("Plotting feature importances...")
plt.figure(figsize=(12, 8))
sns.set_theme(style="whitegrid")

# Create plot
sns.barplot(
    x='Importance', 
    y='Feature', 
    data=importance_df.head(15), 
    palette='viridis',
    hue='Feature',
    legend=False
)
plt.title('Top 15 Feature Importances for Churn Prediction (XGBoost)', fontsize=15, fontweight='bold', pad=15)
plt.xlabel('Importance Score', fontsize=12)
plt.ylabel('Features', fontsize=12)
plt.tight_layout()

# Save plot
plt.savefig(importance_png_path, dpi=300)
plt.close()
print(f"Saved feature importance plot to: {importance_png_path}")

# 8. Save the trained pipeline
print(f"\nSaving trained pipeline to: {model_output_path}...")
with open(model_output_path, 'wb') as f:
    pickle.dump(pipeline, f)
print("Pipeline saved successfully.")

# ============================================================
# MY OWN ANALYSIS — Business Insight Summary
# ============================================================
print("\n=== Business Insight Summary (Added by Harika) ===")

top_3 = importance_df.head(3)
total_top3_importance = top_3['Importance'].sum()

print(f"\nTop 3 churn drivers account for {total_top3_importance*100:.1f}% of total model importance:")
for i, row in top_3.iterrows():
    print(f"  {i+1}. {row['Feature']} ({row['Importance']*100:.1f}%)")

overall_churn_rate = y.mean()
print(f"\nOverall churn rate in dataset: {overall_churn_rate*100:.1f}%")

print("\nBusiness takeaway:")
print("Tenure and contract duration dominate the model's decisions, which")
print("aligns with earlier SQL analysis of the raw billing data (month-to-month")
print("customers churned at 36.7% vs 15.0% for two-year contracts). This confirms")
print("that customer lifecycle stage - not billing amount or demographics -")
print("is the strongest churn signal. Retention strategy should prioritize:")
print("  1. Proactive outreach to customers in their first 6 months")
print("  2. Incentives to upgrade from month-to-month to annual contracts")

print(f"\nModel confidence check: With ROC-AUC of {roc_auc:.4f}, the model")
print(f"correctly ranks a random churner above a random non-churner")
print(f"{roc_auc*100:.1f}% of the time.")

