web: python manage.py wait_for_db && python manage.py migrate && python manage.py collectstatic --noinput && (gunicorn dreamphish.wsgi:application --bind 0.0.0.0:$PORT --env DJANGO_SETTINGS_MODULE=dreamphish.settings_public & gunicorn dreamphish.wsgi:application --bind 0.0.0.0:$PRIVATE_PORT --env DJANGO_SETTINGS_MODULE=dreamphish.settings_private)


