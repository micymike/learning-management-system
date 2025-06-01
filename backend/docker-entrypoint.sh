#!/bin/sh
set -e

# Run migrations
echo "Running migrations..."
python migrations/add_numeric_id.py

# Start the application
echo "Starting application..."
exec "$@"