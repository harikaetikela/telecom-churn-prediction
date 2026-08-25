-- SQL Window Functions Analysis for Telecom Billing History

-- 1. Total Monthly Spending:
-- Calculates the sum of all monthly charges grouped by each customer.
SELECT CustomerID, SUM(MonthlyCharge) AS TotalSpending
FROM Billing 
GROUP BY CustomerID
ORDER BY CustomerID;

-- 2. Average spending over previous three months:
-- Calculates a moving average of the MonthlyCharge for each customer over the current month and the prior 2 months.
SELECT 
    CustomerID,
    BillMonth,
    MonthlyCharge,
    AVG(MonthlyCharge) OVER(
        PARTITION BY CustomerID 
        ORDER BY BillMonth 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as AvgSpending3Months
FROM Billing
ORDER BY CustomerID, BillMonth;

-- 3. Rank Highest Paying Customers:
-- Ranks all billings based on the total amount invoiced in descending order.
SELECT 
    CustomerID,
    BillMonth,
    TotalAmount,
    RANK() OVER(
        ORDER BY TotalAmount DESC
    ) as SpendRank
FROM Billing
ORDER BY SpendRank, CustomerID;

-- 4. Running Total:
-- Computes the running cumulative total of all payments in the database sorted by payment date.
SELECT 
    CustomerID,
    PaymentDate,
    Payment,
    SUM(Payment) OVER(
        ORDER BY PaymentDate
    ) as RunningTotal
FROM Billing
ORDER BY PaymentDate, CustomerID;

-- 5. Previous Month Payment:
-- Grabs the payment amount from the previous month for the same customer.
SELECT 
    CustomerID,
    Month,
    Payment,
    LAG(Payment) OVER(
        PARTITION BY CustomerID 
        ORDER BY Month
    ) as PrevMonthPayment
FROM Billing
ORDER BY CustomerID, Month;

-- 6. Next Month Payment:
-- Grabs the payment amount for the next month for the same customer.
SELECT 
    CustomerID,
    Month,
    Payment,
    LEAD(Payment) OVER(
        PARTITION BY CustomerID 
        ORDER BY Month
    ) as NextMonthPayment
FROM Billing
ORDER BY CustomerID, Month;
