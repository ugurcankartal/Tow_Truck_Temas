"""
Gunicorn yapılandırması — Ubuntu prod (temasotoyolyardim.com)

Kurulum:
  sudo cp deploy/systemd/temasotoyolyardim-gunicorn.service.example \\
      /etc/systemd/system/temasotoyolyardim-gunicorn.service
  sudo systemctl daemon-reload
  sudo systemctl enable --now temasotoyolyardim-gunicorn

Yolları sunucudaki gerçek dizinlere göre düzenleyin.
"""

from __future__ import annotations

import multiprocessing
import os
from pathlib import Path

# /home/ubuntu/Tow_Truck_Temas — proje kökü (git pull)
APP_ROOT = Path(os.environ.get('APP_ROOT', '/home/ubuntu/Tow_Truck_Temas'))
BACKEND_DIR = APP_ROOT / 'backend'

chdir = str(BACKEND_DIR)
wsgi_app = 'config.wsgi:application'

# systemd RuntimeDirectory=temasotoyolyardim ile oluşur; nginx aynı sokete bağlanır
bind = os.environ.get(
    'GUNICORN_BIND',
    'unix:/run/temasotoyolyardim/gunicorn.sock',
)
umask = 0o007

workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
threads = int(os.environ.get('GUNICORN_THREADS', '1'))
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'sync')

timeout = int(os.environ.get('GUNICORN_TIMEOUT', '300'))
graceful_timeout = int(os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', '30'))
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', '5'))

max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', '1000'))
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', '50'))

accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
capture_output = True

# preload_app=True + MySQL: master process DB bağlantısı fork sonrası bozulabilir.
preload_app = os.environ.get('GUNICORN_PRELOAD', 'false').lower() in ('true', '1', 'yes')


def post_fork(server, worker):
    """Fork sonrası miras kalan DB bağlantılarını kapat."""
    try:
        from django.db import connections

        connections.close_all()
    except Exception:
        pass
