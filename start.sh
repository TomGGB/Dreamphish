#!/bin/bash
python manage.py wait_for_db
python manage.py migrate
python manage.py collectstatic --noinput
python dreamphish/run_public.py &
python dreamphish/run_private.py