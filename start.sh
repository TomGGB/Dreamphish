#!/bin/bash
python manage.py wait_for_db
python manage.py migrate
python manage.py collectstatic --noinput
python run.py runserver 0.0.0.0:$PORT