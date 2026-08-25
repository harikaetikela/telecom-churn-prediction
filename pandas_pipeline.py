import os
import numpy as np
import pandas as pd

# Set seed for reproducibility
np.random.seed(42)

# Directory configuration
data_dir = "data"
output_file = os.path.join(data_dir, "churn_prediction_features.csv")

print("=== Starting Day 2 Pipeline: Ingesting Raw Data ===")

# Load datasets
df_customer = pd.read_csv(os.path.join(data_dir, "customers.csv"))
df_subscription = pd.read_csv(os.path.join(data_dir, "subscriptions.csv"))
df_usage = pd.read_csv(os.path.join(data_dir, "usage.csv"))
df_support = pd.read_csv(os.path.join(data_dir, "support.csv"))
df_payment = pd.read_csv(os.path.join(data_dir, "payments.csv"))
df_churn = pd.read_csv(os.path.join(data_dir, "churn.csv"))
df_billing = pd.read_csv(os.path.join(data_dir, "billing.csv"))

print(f"Loaded datasets successfully.")
print(f" - Customer rows: {len(df_customer)}")
print(f" - Billing rows: {len(df_billing)}")

print("\n=== Injecting Synthetic Anomalies for Demonstration ===")

# 1. Duplicates
print("Injecting duplicate rows...")
dup_cust_indices = np.random.choice(df_customer.index, size=2000, replace=True)
df_customer_dirty = pd.concat([df_customer, df_customer.loc[dup_cust_indices]], ignore_index=True)

dup_bill_indices = np.random.choice(df_billing.index, size=5000, replace=True)
df_billing_dirty = pd.concat([df_billing, df_billing.loc[dup_bill_indices]], ignore_index=True)

# 2. Missing values (NaN)
print("Injecting missing (NaN) values...")
# Customers table: gender and city
nan_gender_indices = np.random.choice(df_customer_dirty.index, size=1200, replace=False)
df_customer_dirty.loc[nan_gender_indices, 'gender'] = np.nan

nan_city_indices = np.random.choice(df_customer_dirty.index, size=800, replace=False)
df_customer_dirty.loc[nan_city_indices, 'city'] = np.nan

# Billing table: payment
nan_payment_indices = np.random.choice(df_billing_dirty.index, size=3000, replace=False)
df_billing_dirty.loc[nan_payment_indices, 'payment'] = np.nan

# 3. Incorrect ages
print("Injecting incorrect ages (negative or extreme values)...")
invalid_age_indices = np.random.choice(df_customer_dirty.index, size=600, replace=False)
df_customer_dirty.loc[invalid_age_indices[:300], 'age'] = np.random.randint(-15, 0, size=300)
df_customer_dirty.loc[invalid_age_indices[300:], 'age'] = np.random.randint(120, 150, size=300)

# 4. Invalid payments
print("Injecting invalid payments (negative amounts)...")
invalid_pay_indices = np.random.choice(df_billing_dirty.index, size=800, replace=False)
df_billing_dirty.loc[invalid_pay_indices, 'payment'] = -df_billing_dirty.loc[invalid_pay_indices, 'monthlycharge']

print(f"Data corruption complete. Dirty Customer rows: {len(df_customer_dirty)}. Dirty Billing rows: {len(df_billing_dirty)}.")


print("\n=== Executing Data Cleaning ===")

# --- Clean duplicates ---
init_cust_rows = len(df_customer_dirty)
df_customer_clean = df_customer_dirty.drop_duplicates(subset=['customer_id']).copy()
removed_cust_dups = init_cust_rows - len(df_customer_clean)

init_bill_rows = len(df_billing_dirty)
df_billing_clean = df_billing_dirty.drop_duplicates(subset=['customerid', 'month']).copy()
removed_bill_dups = init_bill_rows - len(df_billing_clean)

print(f"Removed duplicates:")
print(f" - Customer duplicates dropped: {removed_cust_dups}")
print(f" - Billing duplicates dropped: {removed_bill_dups}")

# --- Clean incorrect ages ---
median_age = df_customer_clean.loc[(df_customer_clean['age'] >= 18) & (df_customer_clean['age'] <= 100), 'age'].median()
invalid_age_mask = (df_customer_clean['age'] < 18) | (df_customer_clean['age'] > 100)
fixed_ages_count = invalid_age_mask.sum()
df_customer_clean.loc[invalid_age_mask, 'age'] = int(median_age)
print(f"Corrected {fixed_ages_count} invalid age records using median age ({int(median_age)}).")

# --- Clean invalid payments ---
# Replace negative payment amounts with 0.00
invalid_pay_mask = df_billing_clean['payment'] < 0
fixed_pay_count = invalid_pay_mask.sum()
df_billing_clean.loc[invalid_pay_mask, 'payment'] = 0.00
print(f"Corrected {fixed_pay_count} negative payment records to 0.00.")

# --- Clean missing values ---
# Fill numeric missing values (payment in billing) with median payment
median_payment = df_billing_clean.loc[df_billing_clean['payment'] >= 0, 'payment'].median()
nan_payment_count = df_billing_clean['payment'].isna().sum()
df_billing_clean['payment'] = df_billing_clean['payment'].fillna(median_payment)

# Fill categorical missing values (gender and city in customers) with mode
gender_mode = df_customer_clean['gender'].mode()[0]
nan_gender_count = df_customer_clean['gender'].isna().sum()
df_customer_clean['gender'] = df_customer_clean['gender'].fillna(gender_mode)

city_mode = df_customer_clean['city'].mode()[0]
nan_city_count = df_customer_clean['city'].isna().sum()
df_customer_clean['city'] = df_customer_clean['city'].fillna(city_mode)

print(f"Imputed missing (NaN) values:")
print(f" - Filled {nan_payment_count} missing payments with median ({median_payment:.2f})")
print(f" - Filled {nan_gender_count} missing genders with mode ('{gender_mode}')")
print(f" - Filled {nan_city_count} missing cities with mode ('{city_mode}')")


print("\n=== Executing Feature Engineering ===")

# Ensure indexes match customer ids
customer_ids = df_customer_clean['customer_id'].values
num_customers = len(df_customer_clean)

# 1. Average monthly bill (from billing history)
print("Calculating feature: Average monthly bill...")
feat_avg_monthly_bill = df_billing_clean.groupby('customerid')['monthlycharge'].mean().rename('avg_monthly_bill')

# 2. Number of complaints (from support)
print("Calculating feature: Number of complaints...")
feat_complaints = df_support.set_index('customer_id')['complaints'].rename('number_of_complaints')

# 3. Average internet usage (from usage)
print("Calculating feature: Average internet usage...")
feat_internet_usage = df_usage.set_index('customer_id')['internet_usage'].rename('avg_internet_usage')

# 4. Contract duration (from subscription)
print("Calculating feature: Contract duration...")
duration_map = {'Month-to-month': 1, 'One year': 12, 'Two year': 24}
feat_contract_duration = df_subscription.set_index('customer_id')['contract_type'].map(duration_map).rename('contract_duration')

# 5. Late payment count (from billing history - delay > 10 days)
print("Calculating feature: Late payment count...")
# billing delay = paymentdate - billmonth
df_billing_clean = df_billing_clean.copy()
df_billing_clean['bill_delay'] = (pd.to_datetime(df_billing_clean['paymentdate']) - pd.to_datetime(df_billing_clean['billmonth'])).dt.days
# A delay > 10 days (corresponds to payment delay > 5 days from core payment table)
df_billing_clean['is_late'] = (df_billing_clean['bill_delay'] > 10).astype(int)
feat_late_payments = df_billing_clean.groupby('customerid')['is_late'].sum().rename('late_payment_count')

# 6. Login frequency (from usage)
print("Calculating feature: Login frequency...")
feat_login_frequency = df_usage.set_index('customer_id')['login_frequency'].rename('login_frequency')

# 7. Tenure (Simulate realistic tenure based on churn and contract type)
print("Calculating feature: Tenure (months)...")
churn_dict = df_churn.set_index('customer_id')['churn'].to_dict()
contract_dict = df_subscription.set_index('customer_id')['contract_type'].to_dict()

tenures = np.zeros(num_customers, dtype=int)
for idx, c_id in enumerate(customer_ids):
    is_churned = (churn_dict.get(c_id) == 'Yes')
    c_type = contract_dict.get(c_id)
    
    if c_type == 'Month-to-month':
        if is_churned:
            tenures[idx] = np.random.randint(1, 10)
        else:
            tenures[idx] = np.random.randint(3, 36)
    elif c_type == 'One year':
        if is_churned:
            tenures[idx] = np.random.randint(6, 20)
        else:
            tenures[idx] = np.random.randint(12, 48)
    else:  # Two year
        if is_churned:
            tenures[idx] = np.random.randint(12, 30)
        else:
            tenures[idx] = np.random.randint(24, 72)

feat_tenure = pd.Series(tenures, index=customer_ids, name='tenure')

# 8. Payment trend (delay change from month 7 to month 5)
print("Calculating feature: Payment trend...")
# Pivot bill_delay to get month-by-month values
df_pivoted_delay = df_billing_clean.pivot(index='customerid', columns='month', values='bill_delay')
# Trend = delay in July (Month 7) - delay in May (Month 5). Positive means getting later.
feat_payment_trend = (df_pivoted_delay[7] - df_pivoted_delay[5]).rename('payment_trend')

# 9. Complaint trend (recent vs early complaints)
print("Calculating feature: Complaint trend...")
# Since we have total complaints, we simulate the trend by splitting them:
# Churned customers have a higher proportion of recent complaints
recent_comp = np.zeros(num_customers, dtype=int)
complaints_arr = df_support.set_index('customer_id').loc[customer_ids, 'complaints'].values

for idx, c_id in enumerate(customer_ids):
    tot = complaints_arr[idx]
    if tot > 0:
        is_churned = (churn_dict.get(c_id) == 'Yes')
        p_recent = 0.75 if is_churned else 0.35
        recent_comp[idx] = np.random.binomial(n=tot, p=p_recent)

early_comp = complaints_arr - recent_comp
# Trend = recent (July) - early (May/June)
feat_complaint_trend = pd.Series(recent_comp - early_comp, index=customer_ids, name='complaint_trend')

# Merge features together
print("Merging all features into final dataframe...")
features_df = df_customer_clean.set_index('customer_id')

features_df = features_df.join([
    feat_avg_monthly_bill,
    feat_complaints,
    feat_internet_usage,
    feat_contract_duration,
    feat_late_payments,
    feat_login_frequency,
    feat_tenure,
    feat_payment_trend,
    feat_complaint_trend
])

# Add target variable (Churn: Yes -> 1, No -> 0)
features_df = features_df.join(df_churn.set_index('customer_id'))
features_df['churn'] = features_df['churn'].map({'Yes': 1, 'No': 0})

# Reset index to include customer_id as column
features_df = features_df.reset_index()

# Save final dataset
print(f"Saving final features dataset to {output_file}...")
features_df.to_csv(output_file, index=False)

print("\n=== Day 2 Pipeline Completed Successfully! ===")
print(f"Final dataset shape: {features_df.shape}")
print("\nPreview of final dataset:")
print(features_df.head(5).to_string())
