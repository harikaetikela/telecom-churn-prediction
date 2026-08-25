#!/bin/bash
set -e

CONTAINER_NAME="customer_churn_db"
DB_NAME="churn_db"
DB_USER="postgres"
OUTPUT_DIR="query_outputs"

mkdir -p $OUTPUT_DIR

echo "=== Running Window Functions Analysis and Exporting Full Datasets ==="

# 1. Total Monthly Spending
echo "Executing Query 1: Total Monthly Spending..."
docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "
  COPY (
    SELECT CustomerID, SUM(MonthlyCharge) AS TotalSpending
    FROM Billing 
    GROUP BY CustomerID
    ORDER BY CustomerID
  ) TO '/tmp/query1_total_spending.csv' WITH CSV HEADER;
"
docker cp $CONTAINER_NAME:/tmp/query1_total_spending.csv $OUTPUT_DIR/query1_total_spending.csv

# 2. Average spending over previous three months
echo "Executing Query 2: Moving Average spending (3 months)..."
docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "
  COPY (
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
    ORDER BY CustomerID, BillMonth
  ) TO '/tmp/query2_avg_spending_3months.csv' WITH CSV HEADER;
"
docker cp $CONTAINER_NAME:/tmp/query2_avg_spending_3months.csv $OUTPUT_DIR/query2_avg_spending_3months.csv

# 3. Rank Highest Paying Customers
echo "Executing Query 3: Rank Highest Paying Customers..."
docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "
  COPY (
    SELECT 
        CustomerID,
        BillMonth,
        TotalAmount,
        RANK() OVER(
            ORDER BY TotalAmount DESC
        ) as SpendRank
    FROM Billing
    ORDER BY SpendRank, CustomerID
  ) TO '/tmp/query3_rank_highest_paying.csv' WITH CSV HEADER;
"
docker cp $CONTAINER_NAME:/tmp/query3_rank_highest_paying.csv $OUTPUT_DIR/query3_rank_highest_paying.csv

# 4. Running Total
echo "Executing Query 4: Running Total Payments..."
docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "
  COPY (
    SELECT 
        CustomerID,
        PaymentDate,
        Payment,
        SUM(Payment) OVER(
            ORDER BY PaymentDate
        ) as RunningTotal
    FROM Billing
    ORDER BY PaymentDate, CustomerID
  ) TO '/tmp/query4_running_total.csv' WITH CSV HEADER;
"
docker cp $CONTAINER_NAME:/tmp/query4_running_total.csv $OUTPUT_DIR/query4_running_total.csv

# 5. Previous Month Payment
echo "Executing Query 5: Previous Month Payment..."
docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "
  COPY (
    SELECT 
        CustomerID,
        Month,
        Payment,
        LAG(Payment) OVER(
            PARTITION BY CustomerID 
            ORDER BY Month
        ) as PrevMonthPayment
    FROM Billing
    ORDER BY CustomerID, Month
  ) TO '/tmp/query5_prev_month_payment.csv' WITH CSV HEADER;
"
docker cp $CONTAINER_NAME:/tmp/query5_prev_month_payment.csv $OUTPUT_DIR/query5_prev_month_payment.csv

# 6. Next Month Payment
echo "Executing Query 6: Next Month Payment..."
docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "
  COPY (
    SELECT 
        CustomerID,
        Month,
        Payment,
        LEAD(Payment) OVER(
            PARTITION BY CustomerID 
            ORDER BY Month
        ) as NextMonthPayment
    FROM Billing
    ORDER BY CustomerID, Month
  ) TO '/tmp/query6_next_month_payment.csv' WITH CSV HEADER;
"
docker cp $CONTAINER_NAME:/tmp/query6_next_month_payment.csv $OUTPUT_DIR/query6_next_month_payment.csv

echo "=== Export Completed! CSVs saved to /$OUTPUT_DIR/ ==="
ls -lh $OUTPUT_DIR

echo ""
echo "=== Displaying Previews ==="
echo ""

echo "--- Query 1 Preview: Total Monthly Spending (First 5 customers) ---"
head -n 6 $OUTPUT_DIR/query1_total_spending.csv
echo ""

echo "--- Query 2 Preview: Average Spending 3 Months (First 2 customers) ---"
head -n 8 $OUTPUT_DIR/query2_avg_spending_3months.csv
echo ""

echo "--- Query 3 Preview: Rank Highest Paying Customers (Top 5 records) ---"
head -n 6 $OUTPUT_DIR/query3_rank_highest_paying.csv
echo ""

echo "--- Query 4 Preview: Running Total Payments (First 5 records) ---"
head -n 6 $OUTPUT_DIR/query4_running_total.csv
echo ""

echo "--- Query 5 Preview: Previous Month Payment (First 2 customers) ---"
head -n 8 $OUTPUT_DIR/query5_prev_month_payment.csv
echo ""

echo "--- Query 6 Preview: Next Month Payment (First 2 customers) ---"
head -n 8 $OUTPUT_DIR/query6_next_month_payment.csv
echo ""
