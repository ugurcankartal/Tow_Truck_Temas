#!/usr/bin/env python
"""
backend/.env için güvenli anahtar üretir:

  DEV_SECRET_KEY / PROD_SECRET_KEY
  DEV_ASTRO_REBUILD_WEBHOOK_SECRET / PROD_ASTRO_REBUILD_WEBHOOK_SECRET

Kullanım:
  python generate_env_secrets.py
  python generate_env_secrets.py --write
"""

from __future__ import annotations

import argparse
import secrets
import string
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / 'backend' / '.env'

SECRET_KEY_CHARS = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
ENV_KEYS = (
    'DEV_SECRET_KEY',
    'PROD_SECRET_KEY',
    'DEV_ASTRO_REBUILD_WEBHOOK_SECRET',
    'PROD_ASTRO_REBUILD_WEBHOOK_SECRET',
)


def generate_django_secret_key(length: int = 50) -> str:
    return ''.join(secrets.choice(SECRET_KEY_CHARS) for _ in range(length))


def generate_webhook_secret(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def generate_all() -> dict[str, str]:
    return {
        'DEV_SECRET_KEY': generate_django_secret_key(),
        'PROD_SECRET_KEY': generate_django_secret_key(),
        'DEV_ASTRO_REBUILD_WEBHOOK_SECRET': generate_webhook_secret(),
        'PROD_ASTRO_REBUILD_WEBHOOK_SECRET': generate_webhook_secret(),
    }


def format_env_block(values: dict[str, str]) -> str:
    lines = ['# generate_env_secrets.py tarafından üretildi']
    lines.extend(f'{key}={values[key]}' for key in ENV_KEYS)
    return '\n'.join(lines)


def write_env(values: dict[str, str]) -> None:
    if not ENV_PATH.exists():
        raise FileNotFoundError(f'.env bulunamadı: {ENV_PATH}')

    lines = ENV_PATH.read_text(encoding='utf-8').splitlines()
    updated = dict(values)
    output: list[str] = []

    for line in lines:
        key = line.split('=', 1)[0].strip() if '=' in line and not line.lstrip().startswith('#') else ''
        if key in updated:
            output.append(f'{key}={updated.pop(key)}')
        else:
            output.append(line)

    for key in ENV_KEYS:
        if key in updated:
            output.append(f'{key}={updated[key]}')

    ENV_PATH.write_text('\n'.join(output) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Django SECRET_KEY ve Astro webhook secret değerleri üretir.',
    )
    parser.add_argument(
        '--write',
        action='store_true',
        help=f'Üretilen değerleri {ENV_PATH.relative_to(ROOT_DIR)} dosyasına yazar.',
    )
    args = parser.parse_args()

    values = generate_all()
    print(format_env_block(values))
    print()

    if args.write:
        write_env(values)
        print(f'Yazıldı: {ENV_PATH}')
        print('Webhook sunucusundaki secret ile PROD/DEV webhook secret eşleşmeli.')
    else:
        print('Dosyaya yazmak için: python generate_env_secrets.py --write')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
