-- 1. Row Count Verification
SELECT 'customer' as table_name, COUNT(*) as row_count FROM customer
UNION ALL
SELECT 'subscription', COUNT(*) FROM subscription
UNION ALL
SELECT 'usage', COUNT(*) FROM usage
UNION ALL
SELECT 'support', COUNT(*) FROM support
UNION ALL
SELECT 'payment', COUNT(*) FROM payment
UNION ALL
SELECT 'churn_target', COUNT(*) FROM churn_target;

-- 2. Overall Churn Count and Rate
SELECT 
    churn,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM churn_target
GROUP BY churn;

-- 3. Churn Rate by Contract Type
SELECT 
    s.contract_type,
    COUNT(c.customer_id) as total_customers,
    SUM(CASE WHEN c.churn = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
    ROUND(SUM(CASE WHEN c.churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(c.customer_id), 2) as churn_rate_percentage
FROM subscription s
JOIN churn_target c ON s.customer_id = c.customer_id
GROUP BY s.contract_type
ORDER BY churn_rate_percentage DESC;

-- 4. Churn Rate by Complaints count
SELECT 
    sup.complaints,
    COUNT(c.customer_id) as total_customers,
    SUM(CASE WHEN c.churn = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
    ROUND(SUM(CASE WHEN c.churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(c.customer_id), 2) as churn_rate_percentage
FROM support sup
JOIN churn_target c ON sup.customer_id = c.customer_id
GROUP BY sup.complaints
ORDER BY sup.complaints ASC;

-- 5. Average Charges, Payment Delay, and Outstanding Amount by Churn Status
SELECT 
    c.churn,
    ROUND(AVG(s.monthly_charges), 2) as avg_monthly_charges,
    ROUND(AVG(p.payment_delay), 2) as avg_payment_delay_days,
    ROUND(AVG(p.outstanding_amount), 2) as avg_outstanding_amount
FROM churn_target c
JOIN subscription s ON c.customer_id = s.customer_id
JOIN payment p ON c.customer_id = p.customer_id
GROUP BY c.churn;

-- 6. Top 5 Cities with Highest Churn Rate (minimum 1000 customers in the city)
SELECT 
    cust.city,
    COUNT(cust.customer_id) as total_customers,
    SUM(CASE WHEN c.churn = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
    ROUND(SUM(CASE WHEN c.churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(cust.customer_id), 2) as churn_rate_percentage
FROM customer cust
JOIN churn_target c ON cust.customer_id = c.customer_id
GROUP BY cust.city
HAVING COUNT(cust.customer_id) >= 1000
ORDER BY churn_rate_percentage DESC
LIMIT 5;

-- 7. Usage Metrics for Churned vs Non-Churned Customers
SELECT 
    c.churn,
    ROUND(AVG(u.calls), 0) as avg_calls,
    ROUND(AVG(u.internet_usage), 2) as avg_internet_usage_gb,
    ROUND(AVG(u.login_frequency), 1) as avg_login_frequency
FROM churn_target c
JOIN usage u ON c.customer_id = u.customer_id
GROUP BY c.churn;
