-- Drop tables if they exist to allow clean recreations
DROP TABLE IF EXISTS billing CASCADE;
DROP TABLE IF EXISTS churn_target CASCADE;
DROP TABLE IF EXISTS payment CASCADE;
DROP TABLE IF EXISTS support CASCADE;
DROP TABLE IF EXISTS usage CASCADE;
DROP TABLE IF EXISTS subscription CASCADE;
DROP TABLE IF EXISTS customer CASCADE;

-- 1. Customer Table: Customer ID, Age, Gender, City
CREATE TABLE customer (
    customer_id INT PRIMARY KEY,
    age INT NOT NULL,
    gender VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL
);

-- 2. Subscription Table: Plan, Monthly Charges, Contract Type
CREATE TABLE subscription (
    customer_id INT PRIMARY KEY REFERENCES customer(customer_id) ON DELETE CASCADE,
    plan VARCHAR(50) NOT NULL,
    monthly_charges DECIMAL(10, 2) NOT NULL,
    contract_type VARCHAR(50) NOT NULL
);

-- 3. Usage Table: Calls, Internet Usage, Login Frequency
CREATE TABLE usage (
    customer_id INT PRIMARY KEY REFERENCES customer(customer_id) ON DELETE CASCADE,
    calls INT NOT NULL,
    internet_usage DECIMAL(10, 2) NOT NULL,
    login_frequency INT NOT NULL
);

-- 4. Support Table: Complaints, Tickets, Resolution Time
CREATE TABLE support (
    customer_id INT PRIMARY KEY REFERENCES customer(customer_id) ON DELETE CASCADE,
    complaints INT NOT NULL,
    tickets INT NOT NULL,
    resolution_time DECIMAL(10, 2) NOT NULL
);

-- 5. Payment Table: Payment Delay, Outstanding Amount
CREATE TABLE payment (
    customer_id INT PRIMARY KEY REFERENCES customer(customer_id) ON DELETE CASCADE,
    payment_delay INT NOT NULL,
    outstanding_amount DECIMAL(10, 2) NOT NULL
);

-- 6. Target Variable: Churn (Yes/No)
CREATE TABLE churn_target (
    customer_id INT PRIMARY KEY REFERENCES customer(customer_id) ON DELETE CASCADE,
    churn VARCHAR(3) NOT NULL CHECK (churn IN ('Yes', 'No'))
);

-- 7. Billing Table for Window Analysis
CREATE TABLE billing (
    customerid INT REFERENCES customer(customer_id) ON DELETE CASCADE,
    billmonth DATE NOT NULL,
    month INT NOT NULL,
    monthlycharge DECIMAL(10, 2) NOT NULL,
    totalamount DECIMAL(10, 2) NOT NULL,
    payment DECIMAL(10, 2) NOT NULL,
    paymentdate DATE NOT NULL
);
