import os
import numpy as np
import pandas as pd

# Set seed for reproducibility
np.random.seed(42)

# Configuration
num_customers = 100000
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

print(f"Generating data for {num_customers} customers...")

# 1. Customer Table: Customer ID, Age, Gender, City
customer_ids = np.arange(1, num_customers + 1)
ages = np.random.randint(18, 81, size=num_customers)
genders = np.random.choice(["Male", "Female", "Non-binary"], size=num_customers, p=[0.485, 0.485, 0.03])
cities = np.random.choice([
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", 
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "San Francisco", "Indianapolis", "Columbus"
], size=num_customers)

df_customer = pd.DataFrame({
    "customer_id": customer_ids,
    "age": ages,
    "gender": genders,
    "city": cities
})

# 2. Subscription Table: Plan, Monthly Charges, Contract Type
plans = np.random.choice(["Basic", "Standard", "Premium"], size=num_customers, p=[0.45, 0.35, 0.20])

# Monthly charges depend on the plan
monthly_charges = np.zeros(num_customers)
for idx, plan in enumerate(plans):
    if plan == "Basic":
        monthly_charges[idx] = round(np.random.uniform(20.00, 45.00), 2)
    elif plan == "Standard":
        monthly_charges[idx] = round(np.random.uniform(50.00, 85.00), 2)
    else:  # Premium
        monthly_charges[idx] = round(np.random.uniform(90.00, 150.00), 2)

contract_types = np.random.choice(["Month-to-month", "One year", "Two year"], size=num_customers, p=[0.50, 0.30, 0.20])

df_subscription = pd.DataFrame({
    "customer_id": customer_ids,
    "plan": plans,
    "monthly_charges": monthly_charges,
    "contract_type": contract_types
})

# 3. Usage Table: Calls, Internet Usage, Login Frequency
# Let's correlate usage loosely with the plan (Premium users tend to use more)
calls = np.zeros(num_customers, dtype=int)
internet_usage = np.zeros(num_customers)
for idx, plan in enumerate(plans):
    if plan == "Basic":
        calls[idx] = np.random.randint(50, 400)
        internet_usage[idx] = round(np.random.uniform(5.0, 50.0), 2)
    elif plan == "Standard":
        calls[idx] = np.random.randint(150, 800)
        internet_usage[idx] = round(np.random.uniform(40.0, 300.0), 2)
    else:  # Premium
        calls[idx] = np.random.randint(300, 1200)
        internet_usage[idx] = round(np.random.uniform(150.0, 1000.0), 2)

login_frequency = np.random.randint(1, 31, size=num_customers)

df_usage = pd.DataFrame({
    "customer_id": customer_ids,
    "calls": calls,
    "internet_usage": internet_usage,
    "login_frequency": login_frequency
})

# 4. Support Table: Complaints, Tickets, Resolution Time
# We'll make most customers have 0 complaints, but some have more
complaints = np.random.choice([0, 1, 2, 3, 4, 5], size=num_customers, p=[0.75, 0.15, 0.06, 0.02, 0.01, 0.01])
# Tickets must be >= complaints
tickets = complaints + np.random.choice([0, 1, 2, 3, 4], size=num_customers, p=[0.60, 0.25, 0.10, 0.03, 0.02])

# Resolution time is 0 if tickets is 0, else positive
resolution_time = np.zeros(num_customers)
for idx, t_count in enumerate(tickets):
    if t_count > 0:
        resolution_time[idx] = round(np.random.exponential(scale=12.0) + 1.0, 2)  # Avg 13 hours
    else:
        resolution_time[idx] = 0.0

df_support = pd.DataFrame({
    "customer_id": customer_ids,
    "complaints": complaints,
    "tickets": tickets,
    "resolution_time": resolution_time
})

# 5. Payment Table: Payment Delay, Outstanding Amount
payment_delay = np.random.choice(
    [0, 1, 2, 3, 4, 5, 10, 15, 20, 25, 30], 
    size=num_customers, 
    p=[0.65, 0.10, 0.05, 0.04, 0.03, 0.03, 0.03, 0.02, 0.02, 0.01, 0.02]
)

outstanding_amount = np.zeros(num_customers)
for idx, delay in enumerate(payment_delay):
    if delay > 0:
        # Delayed payments lead to outstanding amounts
        outstanding_amount[idx] = round(np.random.uniform(10.00, 250.00), 2)
    else:
        # A small fraction of on-time payers might have a tiny outstanding amount
        outstanding_amount[idx] = round(np.random.choice([0.00, np.random.uniform(5.00, 50.00)], p=[0.95, 0.05]), 2)

df_payment = pd.DataFrame({
    "customer_id": customer_ids,
    "payment_delay": payment_delay,
    "outstanding_amount": outstanding_amount
})

# 6. Target Variable: Churn (Yes/No)
# We model churn based on risk scores
churn_probs = np.zeros(num_customers)

for idx in range(num_customers):
    prob = 0.03  # Base churn probability
    
    # 1. Contract Type effect
    c_type = contract_types[idx]
    if c_type == "Month-to-month":
        prob += 0.22
    elif c_type == "One year":
        prob += 0.05
    # Two year contract has no added risk
    
    # 2. Monthly Charges effect
    m_charge = monthly_charges[idx]
    if m_charge > 100:
        prob += 0.12
    elif m_charge > 70:
        prob += 0.06
        
    # 3. Complaints effect
    comp_count = complaints[idx]
    if comp_count > 0:
        prob += 0.18 * comp_count
        
    # 4. Payment Delay effect
    p_delay = payment_delay[idx]
    if p_delay > 15:
        prob += 0.20
    elif p_delay > 5:
        prob += 0.08
        
    # 5. Usage / Login Frequency effect
    log_freq = login_frequency[idx]
    if log_freq < 5:
        prob += 0.08
    elif log_freq > 20:
        prob -= 0.03
        
    # Cap probability between 1% and 95%
    prob = max(0.01, min(0.95, prob))
    churn_probs[idx] = prob

# Decide churn based on probabilities
churn_labels = np.where(np.random.rand(num_customers) < churn_probs, "Yes", "No")

df_churn = pd.DataFrame({
    "customer_id": customer_ids,
    "churn": churn_labels
})

# Generate Billing Table (3 months of history for each customer)
billing_dfs = []
bill_months_dates = ['2026-05-01', '2026-06-01', '2026-07-01']
month_nums = [5, 6, 7]
base_dates = ['2026-05-05', '2026-06-05', '2026-07-05']

print("Generating billing data...")
for m_idx in range(3):
    m_num = month_nums[m_idx]
    b_month = bill_months_dates[m_idx]
    base_date = pd.to_datetime(base_dates[m_idx])
    
    # Calculate total amount (charge + 7% tax/fees)
    m_totals = np.round(monthly_charges * 1.07, 2)
    
    # Delays with a bit of noise around the payment delay from the core payment table
    delays = payment_delay + np.random.randint(-2, 3, size=num_customers)
    delays = np.maximum(0, delays)
    p_dates_pd = base_date + pd.to_timedelta(delays, unit='D')
    p_dates = p_dates_pd.strftime('%Y-%m-%d')
    
    billing_dfs.append(pd.DataFrame({
        "customerid": customer_ids,
        "billmonth": b_month,
        "month": m_num,
        "monthlycharge": monthly_charges,
        "totalamount": m_totals,
        "payment": m_totals,
        "paymentdate": p_dates
    }))

df_billing = pd.concat(billing_dfs, ignore_index=True)

# Write datasets to CSV files
df_customer.to_csv(os.path.join(data_dir, "customers.csv"), index=False)
df_subscription.to_csv(os.path.join(data_dir, "subscriptions.csv"), index=False)
df_usage.to_csv(os.path.join(data_dir, "usage.csv"), index=False)
df_support.to_csv(os.path.join(data_dir, "support.csv"), index=False)
df_payment.to_csv(os.path.join(data_dir, "payments.csv"), index=False)
df_churn.to_csv(os.path.join(data_dir, "churn.csv"), index=False)
df_billing.to_csv(os.path.join(data_dir, "billing.csv"), index=False)

print("All CSV files generated and saved to data/ directory:")
print(f" - customers.csv: {df_customer.shape[0]} rows")
print(f" - subscriptions.csv: {df_subscription.shape[0]} rows")
print(f" - usage.csv: {df_usage.shape[0]} rows")
print(f" - support.csv: {df_support.shape[0]} rows")
print(f" - payments.csv: {df_payment.shape[0]} rows")
print(f" - churn.csv: {df_churn.shape[0]} rows")
print(f" - billing.csv: {df_billing.shape[0]} rows")
print(f"Overall Churn Rate: {(df_churn['churn'] == 'Yes').mean() * 100:.2f}%")
