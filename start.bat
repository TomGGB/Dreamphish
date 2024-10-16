@echo off
python manage.py wait_for_db
python manage.py migrate
python manage.py collectstatic --noinput
start python dreamphish/run_public.py
start python dreamphish/run_private.py

