import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.cache import cache

LOCK_TTL = 7200
RESULT_TTL = 86400
STALE_STARTING_SECONDS = 120
LOCK_VALUE_STARTING = 'starting'
LOCK_VALUE_RUNNING = 'running'


def groq_lock_key(handler: str) -> str:
    return f'groq_translate_lock:{handler}'


def groq_lock_since_key(handler: str) -> str:
    return f'groq_translate_lock_since:{handler}'


def groq_result_key(handler: str) -> str:
    return f'groq_translate_result:{handler}'


def release_groq_lock(handler: str) -> None:
    cache.delete(groq_lock_key(handler))
    cache.delete(groq_lock_since_key(handler))


def release_stale_groq_lock(handler: str, max_starting_seconds: int = STALE_STARTING_SECONDS) -> bool:
    """Yarım kalan 'starting' kilidini temizler (FileBasedCache gunicorn restart sonrası kalır)."""
    from localization.services.groq_translation_progress import get_groq_translation_progress

    lock = cache.get(groq_lock_key(handler))
    if lock != LOCK_VALUE_STARTING:
        return False

    progress = get_groq_translation_progress(handler)
    if progress and int(progress.get('current', 0)) > 0:
        return False

    since = cache.get(groq_lock_since_key(handler))
    stale = since is None or (time.time() - float(since)) > max_starting_seconds
    if not stale:
        return False

    release_groq_lock(handler)
    if progress:
        from localization.services.groq_translation_progress import GroqTranslationProgress

        GroqTranslationProgress(handler).clear()
    save_groq_translation_result(
        handler,
        error='Önceki Groq çevirisi başlatılamadı veya yarım kaldı. Tekrar deneyin.',
    )
    return True


def is_groq_translation_running(handler: str) -> bool:
    release_stale_groq_lock(handler)
    lock = cache.get(groq_lock_key(handler))
    if lock in (LOCK_VALUE_STARTING, LOCK_VALUE_RUNNING, '1', 'web', 'cli'):
        return True
    from localization.services.groq_translation_progress import get_groq_translation_progress

    progress = get_groq_translation_progress(handler)
    return isinstance(progress, dict) and progress.get('status') == 'running'


def get_groq_translation_status(handler: str) -> dict[str, Any] | None:
    payload = cache.get(groq_result_key(handler))
    return payload if isinstance(payload, dict) else None


def save_groq_translation_result(
    handler: str,
    *,
    stats: dict[str, int] | None = None,
    error: str | None = None,
) -> None:
    cache.set(
        groq_result_key(handler),
        {'stats': stats, 'error': error},
        RESULT_TTL,
    )


def acquire_groq_lock(handler: str, *, source: str = 'cli') -> bool:
    lock_key = groq_lock_key(handler)
    if cache.add(lock_key, source, LOCK_TTL):
        cache.set(groq_lock_since_key(handler), time.time(), LOCK_TTL)
        return True
    return cache.get(lock_key) == LOCK_VALUE_STARTING and source == LOCK_VALUE_RUNNING


def promote_groq_lock_to_running(handler: str) -> None:
    lock_key = groq_lock_key(handler)
    if cache.get(lock_key) == LOCK_VALUE_STARTING:
        cache.set(lock_key, LOCK_VALUE_RUNNING, LOCK_TTL)
        cache.set(groq_lock_since_key(handler), time.time(), LOCK_TTL)


def _resolve_python(backend_dir: Path) -> str:
    project_root = backend_dir.parent
    if os.name == 'nt':
        candidates = [
            project_root / 'venv' / 'Scripts' / 'python.exe',
            backend_dir / 'venv' / 'Scripts' / 'python.exe',
            backend_dir / '.venv' / 'Scripts' / 'python.exe',
        ]
    else:
        candidates = [
            project_root / 'venv' / 'bin' / 'python',
            backend_dir / 'venv' / 'bin' / 'python',
            backend_dir / '.venv' / 'bin' / 'python',
        ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def _resolve_manage_script(backend_dir: Path) -> Path:
    module = os.environ.get('DJANGO_SETTINGS_MODULE', '')
    if module.endswith('.prod'):
        prod_manage = backend_dir / 'manage_prod.py'
        if prod_manage.is_file():
            return prod_manage
    return backend_dir / 'manage.py'


def start_groq_translation_background(handler: str) -> str:
    if is_groq_translation_running(handler):
        return 'already_running'

    lock_key = groq_lock_key(handler)
    if not cache.add(lock_key, LOCK_VALUE_STARTING, LOCK_TTL):
        return 'already_running'
    cache.set(groq_lock_since_key(handler), time.time(), LOCK_TTL)

    backend_dir = Path(settings.BASE_DIR)
    manage_py = _resolve_manage_script(backend_dir)
    logs_dir = backend_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    log_path = logs_dir / f'groq-{handler}.log'

    env = os.environ.copy()
    env.setdefault(
        'DJANGO_SETTINGS_MODULE',
        os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.dev'),
    )

    python = _resolve_python(backend_dir)

    try:
        log_file = open(log_path, 'a', encoding='utf-8')
        log_file.write(
            f'\n--- spawn {time.strftime("%Y-%m-%d %H:%M:%S")} '
            f'python={python} manage={manage_py} handler={handler} ---\n',
        )
        log_file.flush()
        subprocess.Popen(
            [python, str(manage_py), 'groq_translate', handler],
            cwd=str(backend_dir),
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except OSError:
        release_groq_lock(handler)
        save_groq_translation_result(
            handler,
            error='Groq çevirisi başlatılamadı. Sunucu loglarını kontrol edin.',
        )
        return 'spawn_error'

    return 'started'
