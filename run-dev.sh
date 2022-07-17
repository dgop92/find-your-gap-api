#!/bin/sh

python manage.py wait_for_db &&
python manage.py makemigrations &&
python manage.py migrate &&
python manage.py runserver 127.0.0.1:8080
