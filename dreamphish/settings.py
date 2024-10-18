# Importaciones
from pathlib import Path
import os
import pymysql
pymysql.install_as_MySQLdb()
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Configuración básica
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-secret-key')
DEBUG = False if os.environ.get('ENV') == 'production' else True
ALLOWED_HOSTS = [
                 '127.0.0.1',
                 'localhost',
                 '0.0.0.0',
                 'limon.h4d.cl'
                ]
CSRF_TRUSTED_ORIGINS = ['https://limon.h4d.cl']

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'dashboard',
    'campaigns',
    'landing_pages',
    'smtp',
    'email_templates',
    'tinymce',
    'webhooks',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# Configuración de URLs y plantillas
ROOT_URLCONF = 'dreamphish.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'core' / 'templates',
            BASE_DIR / 'dashboard' / 'templates',
            BASE_DIR / 'campaigns' / 'templates',
            BASE_DIR / 'landing_pages' / 'templates',
            BASE_DIR / 'smtp' / 'templates',
            BASE_DIR / 'groups' / 'templates',
            BASE_DIR / 'webhooks' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'dreamphish.wsgi.application'

# Configuracin de la base de datos
if os.environ.get('ENV') == 'production':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('MYSQLDATABASE'),
            'USER': os.getenv('MYSQLUSER'),
            'PASSWORD': os.getenv('MYSQLPASSWORD'),
            'HOST': os.getenv('MYSQLHOST'),
            'PORT': os.getenv('MYSQLPORT'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Validadores de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configuración de internacionalización
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración adicional
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'core.User'
LOGIN_URL = '/login/'
PORT = int(os.environ.get('PORT', 8000))
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Configuración para servir archivos media en producción
SERVE_MEDIA_IN_PRODUCTION = True

PUBLIC_PORT = int(os.environ.get('PUBLIC_PORT', 8000))
PRIVATE_PORT = int(os.environ.get('PRIVATE_PORT', 8001))


# Configuración para TinyMCE
TINYMCE_API_KEY = os.environ.get('TINYMCE_API_KEY')
TINYMCE_JS_URL = 'https://cdn.tiny.cloud/1/{}/tinymce/7/tinymce.min.js'.format(TINYMCE_API_KEY)
TINYMCE_COMPRESSOR = False
TINYMCE_DEFAULT_CONFIG = {
    'height': 360,
    'width': 'auto',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'silver',
    'plugins': '''
            advlist autolink lists link image charmap print preview anchor
            searchreplace visualblocks code fullscreen
            insertdatetime media table paste code help wordcount
            ''',
    'toolbar': 'undo redo | formatselect | '
               'bold italic backcolor | alignleft aligncenter '
               'alignright alignjustify | bullist numlist outdent indent | '
               'removeformat | help',
    'content_css': 'default',
    'language': 'es',
    'branding': False,
    'autosave_ask_before_unload': True,
    'autosave_interval': '30s',
    'autosave_prefix': '{path}{query}-{id}-',
    'autosave_restore_when_empty': False,
    'autosave_retention': '2m',
    'image_advtab': True,
    'importcss_append': True,
    'image_caption': True,
    'quickbars_selection_toolbar': 'bold italic | quicklink h2 h3 blockquote quickimage quicktable',
    'noneditable_noneditable_class': 'mceNonEditable',
    'toolbar_mode': 'sliding',
    'contextmenu': 'link image imagetools table',
    'entity_encoding': 'raw',
}

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/dreamphish_user/Dreamphish/logs/django.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}
