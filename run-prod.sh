#!/bin/sh

python manage.py wait_for_db &&
python manage.py makemigrations &&
python manage.py migrate &&
gunicorn --bind 0.0.0.0:8080 find_your_gap_api.wsgi
