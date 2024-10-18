import os
import sys
import traceback

# Añade el directorio padre al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dreamphish.settings_private')

if __name__ == "__main__":
    try:
        from django.core.management import execute_from_command_line
        port = os.environ.get('PRIVATE_PORT', '8001')
        execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])
    except Exception as e:
        with open('/home/dreamphish_user/dreamphish/logs/private_error.log', 'w') as f:
            f.write(f"Error: {str(e)}\n")
            f.write(traceback.format_exc())
        raise
