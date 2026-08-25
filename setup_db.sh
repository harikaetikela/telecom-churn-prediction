#!/bin/bash
set -e

CONTAINER_NAME="customer_churn_db"
DB_NAME="churn_db"
DB_USER="postgres"
DB_PASS="postgres"

echo "=== Step 1: Cleaning up existing Postgres container ==="
docker rm -f $CONTAINER_NAME 2>/dev/null || true

echo "=== Step 2: Spinning up new PostgreSQL container ==="
docker run --name $CONTAINER_NAME \
  -e POSTGRES_PASSWORD=$DB_PASS \
  -e POSTGRES_DB=$DB_NAME \
  -p 5432:5432 \
  -d postgres:latest

echo "=== Step 3: Waiting for PostgreSQL to be ready ==="
until docker exec -i $CONTAINER_NAME pg_isready -U $DB_USER -d $DB_NAME >/dev/null 2>&1; do
  echo "Postgres is initializing, waiting 2 seconds..."
  sleep 2
done
echo "Postgres is ready to accept connections!"

echo "=== Step 4: Transferring schema and data files to container ==="
docker cp schema.sql $CONTAINER_NAME:/tmp/schema.sql
docker cp data $CONTAINER_NAME:/tmp/data

echo "=== Step 5: Creating database tables using schema.sql ==="
docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -f /tmp/schema.sql

echo "=== Step 6: Importing datasets using COPY command ==="
docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME <<EOF
\echo 'Importing customer data...'
COPY customer FROM '/tmp/data/customers.csv' DELIMITER ',' CSV HEADER;

\echo 'Importing subscription data...'
COPY subscription FROM '/tmp/data/subscriptions.csv' DELIMITER ',' CSV HEADER;

\echo 'Importing usage data...'
COPY usage FROM '/tmp/data/usage.csv' DELIMITER ',' CSV HEADER;

\echo 'Importing support data...'
COPY support FROM '/tmp/data/support.csv' DELIMITER ',' CSV HEADER;

\echo 'Importing payment data...'
COPY payment FROM '/tmp/data/payments.csv' DELIMITER ',' CSV HEADER;

\echo 'Importing churn data...'
COPY churn_target FROM '/tmp/data/churn.csv' DELIMITER ',' CSV HEADER;

\echo 'Importing billing data...'
COPY billing FROM '/tmp/data/billing.csv' DELIMITER ',' CSV HEADER;
EOF

echo "=== Database Setup and Data Import Completed Successfully! ==="
