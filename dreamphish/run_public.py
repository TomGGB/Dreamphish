import os
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dreamphish.settings_public')
execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{os.environ.get("PUBLIC_PORT", 8000)}'])
