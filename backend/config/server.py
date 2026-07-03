#!/usr/bin/env python
"""runserver için DEV_PORT enjeksiyonu ve ayar modülü seçimi."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def ensure_dev_settings() -> None:
    """Yerel geliştirmede varsayılan modül; DJANGO_SETTINGS_MODULE zaten set ise dokunma."""
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.dev'


def inject_runserver_port(argv: list[str]) -> None:
    """Port verilmediyse backend/.env içindeki DEV_PORT kullanılır."""
    if 'runserver' not in argv:
        return

    runserver_idx = argv.index('runserver')
    trailing = argv[runserver_idx + 1:]

    for arg in trailing:
        if arg.startswith('-'):
            continue
        if arg.isdigit() or ':' in arg:
            return

    dev_port = os.environ.get('DEV_PORT', '8000')
    argv.append(f'127.0.0.1:{dev_port}')
