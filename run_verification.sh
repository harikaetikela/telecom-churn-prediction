#!/bin/bash
set -e

CONTAINER_NAME="customer_churn_db"
DB_NAME="churn_db"
DB_USER="postgres"

echo "=== Running Database Verification Queries ==="
docker cp queries.sql $CONTAINER_NAME:/tmp/queries.sql
docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -f /tmp/queries.sql
