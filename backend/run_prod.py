#!/usr/bin/env python
"""
Üretim ayarlarıyla Django sunucusunu PROD_PORT üzerinde başlatır.

Kullanım:
    python run_prod.py
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod'

port = os.environ.get('PROD_PORT', '8000')

if __name__ == '__main__':
    from django.core.management import execute_from_command_line

    execute_from_command_line([sys.argv[0], 'runserver', f'0.0.0.0:{port}'])
