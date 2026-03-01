#!/bin/bash
set -e

echo "Creating migrations..."
python manage.py makemigrations

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
