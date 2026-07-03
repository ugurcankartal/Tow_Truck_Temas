"""
Yerel geliştirme ayarları.
"""

import os

from .base import *  # noqa: F403

DEBUG = env_bool('DEV_DEBUG', default=True)

SECRET_KEY = os.environ.get(
    'DEV_SECRET_KEY',
    'django-insecure-dev-only-change-in-production',
)

ASTRO_REBUILD_WEBHOOK_SECRET = os.environ.get('DEV_ASTRO_REBUILD_WEBHOOK_SECRET', '')

SITE_URL = os.environ.get(
    'DEV_SITE_URL',
    os.environ.get('SITE_URL', f'http://localhost:{FRONTEND_DEV_PORT}'),
)

ALLOWED_HOSTS = env_list('DEV_ALLOWED_HOSTS') or env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')

DATABASES = {  # noqa: F811
    'default': mysql_database(
        name_key='DEV_DB_NAME',
        user_key='DEV_DB_USER',
        password_key='DEV_DB_PASSWORD',
        host_key='DEV_DB_HOST',
        port_key='DEV_DB_PORT',
        name_default='tow_truck_temas',
    ),
}

def _merge_origins(*origin_lists: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for origins in origin_lists:
        for origin in origins:
            if origin and origin not in seen:
                seen.add(origin)
                merged.append(origin)
    return merged


CORS_ALLOWED_ORIGINS = _merge_origins(
    env_list('DEV_CORS_ALLOWED_ORIGINS') or env_list('CORS_ALLOWED_ORIGINS', ''),
    [
        f'http://localhost:{FRONTEND_DEV_PORT}',
        f'http://127.0.0.1:{FRONTEND_DEV_PORT}',
    ],
)
