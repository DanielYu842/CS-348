#!/bin/bash

# Exit on error
set -e

# Configuration
DB_HOST=${DATABASE_HOST:-"localhost"}
DB_PORT=${DATABASE_PORT:-"5432"}
DB_NAME=${DATABASE_NAME:-"test_db"}
DB_USER=${DATABASE_USER:-"postgres"}
DB_PASSWORD=${DATABASE_PASSWORD:-"passcode"}

# Function to seed data into the PostgreSQL database
seed_database() {
  echo "Seeding the PostgreSQL database..."
  PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME <<EOF
CREATE TABLE IF NOT EXISTS sample_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    value INTEGER NOT NULL
);

INSERT INTO sample_table (name, value) VALUES
('Sample1', 100),
('Sample2', 200),
('Sample3', 300)
ON CONFLICT DO NOTHING;
EOF
  echo "Database seeded successfully!"
}

# Main script execution
echo "Starting setup and seeding process..."


seed_database