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
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

_CACHE_LATEST = 'astro_rebuild:latest'
_CACHE_SCHEDULER = 'astro_rebuild:scheduler'
_DEBOUNCE_SECONDS = 8.0
_SCHEDULER_TTL = 30


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
    logger.info('Astro rebuild çalıştırılıyor: %s', source)
    webhook_ok = _post_webhook(source, updated_at)
    local_ok = _run_local_build()

    if not webhook_ok and not local_ok:
        if not getattr(settings, 'ASTRO_REBUILD_WEBHOOK_URL', '') and not getattr(
            settings, 'ASTRO_REBUILD_LOCAL', False
        ):
            logger.warning(
                'Astro rebuild atlandı (ASTRO_REBUILD_WEBHOOK_URL ve ASTRO_REBUILD_LOCAL kapalı): %s',
                source,
            )


def _cache_set(key: str, value: Any, timeout: int) -> None:
    try:
        cache.set(key, value, timeout)
    except Exception:
        pass


def _cache_add(key: str, value: Any, timeout: int) -> bool:
    try:
        return cache.add(key, value, timeout)
    except Exception:
        return True


def _cache_get(key: str, default=None):
    try:
        return cache.get(key, default)
    except Exception:
        return default


def _cache_delete(key: str) -> None:
    try:
        cache.delete(key)
    except Exception:
        pass


def _debounced_worker(initial_source: str, initial_updated_at: str | None) -> None:
    try:
        time.sleep(_DEBOUNCE_SECONDS)
        payload = _cache_get(_CACHE_LATEST) or {}
        source = payload.get('source') or initial_source
        updated_at = payload.get('updated_at', initial_updated_at)
        _execute_rebuild(source, updated_at)
    finally:
        _cache_delete(_CACHE_SCHEDULER)


def trigger_astro_rebuild(source: str, updated_at: str | None = None, *, async_run: bool = True) -> None:
    """
    İçerik değişikliğinde Astro rebuild tetikler.
    Varsayılan: paylaşımlı cache ile debounce + daemon thread (Gunicorn uyumlu).
    """
    if not async_run:
        _execute_rebuild(source, updated_at)
        return

    _cache_set(
        _CACHE_LATEST,
        {'source': source, 'updated_at': updated_at},
        300,
    )

    if not _cache_add(_CACHE_SCHEDULER, source, _SCHEDULER_TTL):
        logger.debug('Astro rebuild debounce: mevcut zamanlayıcı kullanılıyor (%s)', source)
        return

    thread = threading.Thread(
        target=_debounced_worker,
        args=(source, updated_at),
        daemon=True,
        name='astro-rebuild-worker',
    )
    thread.start()
