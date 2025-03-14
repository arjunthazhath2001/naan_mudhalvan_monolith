#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Show commands as they're executed
set -x

# Wait for database to be ready
echo "Waiting for database to be ready..."

# Try to connect to PostgreSQL, retry until connected
until python -c "import psycopg2; psycopg2.connect(dbname='naan_mudhalvan', user='postgres', password='postgres', host='db', port='5432')" 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing migrations"

# Make migrations for all apps
python manage.py makemigrations placement_team
python manage.py makemigrations students
python manage.py makemigrations recruiters
python manage.py makemigrations program_managers

# Apply migrations
python manage.py migrate

# Create program managers for all districts
python manage.py create_program_managers

echo "Migrations complete!"