"""
Admin kaydı sonrası Astro frontend rebuild tetikleyicisi.

Prod: ASTRO_REBUILD_WEBHOOK_URL → CI / build sunucusu
Lokal: ASTRO_REBUILD_LOCAL=true → npm run build (subprocess)
"""

from __future__ import annotations

import json
import logging
import subprocess
import threading
import urllib.error
import urllib.request
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


def _post_webhook(source: str, updated_at: str | None = None) -> bool:
    url = getattr(settings, 'ASTRO_REBUILD_WEBHOOK_URL', '')
    if not url:
        return False

    payload = {
        'event': 'astro_rebuild',
        'source': source,
        'updated_at': updated_at,
    }
    data = json.dumps(payload).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    secret = getattr(settings, 'ASTRO_REBUILD_WEBHOOK_SECRET', '')
    if secret:
        headers['X-Webhook-Secret'] = secret

    request = urllib.request.Request(url, data=data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            logger.info('Astro rebuild webhook OK (%s): %s', response.status, source)
            return True
    except urllib.error.URLError as exc:
        logger.error('Astro rebuild webhook hatası: %s', exc)
        return False


def _run_local_build() -> bool:
    if not getattr(settings, 'ASTRO_REBUILD_LOCAL', False):
        return False

    frontend_dir: Path = settings.FRONTEND_DIR
    if not (frontend_dir / 'package.json').exists():
        logger.error('Frontend dizini bulunamadı: %s', frontend_dir)
        return False

    npm_cmd = 'npm.cmd' if settings.IS_WINDOWS else 'npm'
    build_script = getattr(settings, 'ASTRO_BUILD_SCRIPT', 'build')

    logger.info('Yerel Astro rebuild başlatılıyor: %s run %s', frontend_dir, build_script)

    try:
        result = subprocess.run(
            [npm_cmd, 'run', build_script],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            check=False,
            shell=settings.IS_WINDOWS,
        )
        if result.returncode != 0:
            logger.error('Astro build başarısız:\n%s', result.stderr)
            return False
        logger.info('Astro build tamamlandı')
        return True
    except OSError as exc:
        logger.error('Astro build çalıştırılamadı: %s', exc)
        return False


def _execute_rebuild(source: str, updated_at: str | None = None) -> None:
    webhook_ok = _post_webhook(source, updated_at)
    local_ok = _run_local_build()

    if not webhook_ok and not local_ok:
        if not getattr(settings, 'ASTRO_REBUILD_WEBHOOK_URL', '') and not getattr(
            settings, 'ASTRO_REBUILD_LOCAL', False
        ):
            logger.debug(
                'Astro rebuild atlandı (ASTRO_REBUILD_WEBHOOK_URL ve ASTRO_REBUILD_LOCAL kapalı): %s',
                source,
            )


def trigger_astro_rebuild(source: str, updated_at: str | None = None, *, async_run: bool = True) -> None:
    """
    İçerik değişikliğinde Astro rebuild tetikler.
    Varsayılan: debounce + arka plan thread (admin kaydını bloklamaz).
    """
    if not async_run:
        _execute_rebuild(source, updated_at)
        return

    _schedule_debounced_rebuild(source, updated_at)


_DEBOUNCE_SECONDS = 8.0
_rebuild_lock = threading.Lock()
_rebuild_timer: threading.Timer | None = None
_pending_source = 'model_change'
_pending_updated_at: str | None = None


def _fire_debounced_rebuild() -> None:
    global _pending_source, _pending_updated_at
    with _rebuild_lock:
        source = _pending_source
        updated_at = _pending_updated_at
    _execute_rebuild(source, updated_at)


def _schedule_debounced_rebuild(source: str, updated_at: str | None) -> None:
    global _rebuild_timer, _pending_source, _pending_updated_at

    with _rebuild_lock:
        _pending_source = source
        if updated_at:
            _pending_updated_at = updated_at
        if _rebuild_timer is not None:
            _rebuild_timer.cancel()
        _rebuild_timer = threading.Timer(_DEBOUNCE_SECONDS, _fire_debounced_rebuild)
        _rebuild_timer.daemon = True
        _rebuild_timer.start()
