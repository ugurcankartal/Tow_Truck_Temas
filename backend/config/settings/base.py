"""
Ortak Django ayarları — dev ve prod modülleri bunu genişletir.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# systemd EnvironmentFile satır içi # yorumlarını değere karıştırabilir; .env dosyası esas alınır.
load_dotenv(BASE_DIR / '.env', override=True)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_prose_editor',
    'localization',
    'core',
    'content',
    'showcase',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# LocMem is per-process; Groq progress/lock must be shared with subprocess.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'cache' / 'django',
        'OPTIONS': {'MAX_ENTRIES': 10000},
    },
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'core.renderers.UnicodeJSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

SITE_URL = os.environ.get('SITE_URL', 'http://localhost:4321')

DEV_PORT = int(os.environ.get('DEV_PORT', '8000'))
PROD_PORT = int(os.environ.get('PROD_PORT', '8000'))
FRONTEND_DEV_PORT = int(os.environ.get('FRONTEND_DEV_PORT', '4321'))

# --- Astro rebuild (admin save → webhook / yerel build) ---
IS_WINDOWS = os.name == 'nt'
FRONTEND_DIR = Path(os.environ.get('FRONTEND_DIR', str(BASE_DIR.parent / 'frontend')))
ASTRO_REBUILD_WEBHOOK_URL = os.environ.get('ASTRO_REBUILD_WEBHOOK_URL', '')
ASTRO_REBUILD_LOCAL = os.environ.get('ASTRO_REBUILD_LOCAL', 'false').lower() in ('true', '1', 'yes')
ASTRO_BUILD_SCRIPT = os.environ.get('ASTRO_BUILD_SCRIPT', 'build')


def env_list(key: str, default: str = '') -> list[str]:
    return [item.strip() for item in os.environ.get(key, default).split(',') if item.strip()]


def env_bool(key: str, default: bool = False) -> bool:
    value = os.environ.get(key)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes')


def mysql_database(
    *,
    name_key: str,
    user_key: str,
    password_key: str,
    host_key: str,
    port_key: str,
    name_default: str,
    user_default: str = 'root',
    password_default: str = '',
    host_default: str = '127.0.0.1',
    port_default: str = '3306',
) -> dict:
    return {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get(name_key, name_default),
        'USER': os.environ.get(user_key, user_default),
        'PASSWORD': os.environ.get(password_key, password_default),
        'HOST': os.environ.get(host_key, host_default),
        'PORT': os.environ.get(port_key, port_default),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
