#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python app/initalize_db/backend_pre_start.py

# Create the database if it doesn't exist
alembic revision --autogenerate -m "autoupdate"
if [ $? -ne 0 ]; then
    echo "No changes detected in the database schema."
else
    echo "Database schema updated successfully."
fi
# Run migrations
alembic upgrade head

# Create initial data in DB
python app/initalize_db/initial_data.py
