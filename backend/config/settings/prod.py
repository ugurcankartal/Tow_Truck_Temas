"""
Üretim ortamı ayarları.
"""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

DEBUG = env_bool('PROD_DEBUG', default=False)

SECRET_KEY = os.environ.get('PROD_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('PROD_SECRET_KEY ortam değişkeni prod için zorunludur.')

ASTRO_REBUILD_WEBHOOK_SECRET = os.environ.get('PROD_ASTRO_REBUILD_WEBHOOK_SECRET', '')

SITE_URL = os.environ.get('PROD_SITE_URL', '').strip()
if not SITE_URL:
    raise ImproperlyConfigured('PROD_SITE_URL ortam değişkeni prod için zorunludur.')

ALLOWED_HOSTS = env_list('PROD_ALLOWED_HOSTS')
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured('PROD_ALLOWED_HOSTS ortam değişkeni prod için zorunludur.')

DATABASES = {  # noqa: F811
    'default': mysql_database(
        name_key='DB_NAME',
        user_key='DB_USER',
        password_key='DB_PASSWORD',
        host_key='DB_HOST',
        port_key='DB_PORT',
        name_default='tow_truck_temas',
        user_default='',
        password_default='',
        host_default='127.0.0.1',
        port_default='3306',
    ),
}

CORS_ALLOWED_ORIGINS = env_list('PROD_CORS_ALLOWED_ORIGINS')
if not CORS_ALLOWED_ORIGINS:
    raise ImproperlyConfigured('PROD_CORS_ALLOWED_ORIGINS ortam değişkeni prod için zorunludur.')

CSRF_TRUSTED_ORIGINS = env_list('PROD_CSRF_TRUSTED_ORIGINS') or CORS_ALLOWED_ORIGINS

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'true').lower() in ('true', '1', 'yes')

_max_upload_mb = int(os.environ.get('PROD_MAX_UPLOAD_MB', '250'))
_max_upload_bytes = _max_upload_mb * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = _max_upload_bytes
FILE_UPLOAD_MAX_MEMORY_SIZE = _max_upload_bytes
