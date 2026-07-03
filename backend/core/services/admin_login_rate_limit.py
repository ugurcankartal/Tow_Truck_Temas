from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

from core.login_security_models import (
    AdminLoginDeviceLock,
    AdminLoginFailedAttempt,
    AdminLoginSecuritySettings,
    AdminLoginUsernameLock,
)


@dataclass(frozen=True)
class AdminLoginCheckResult:
    allowed: bool
    message: str = ''
    retry_after_seconds: int = 0
    lock_type: str = ''


def normalize_username(username: str) -> str:
    return username.strip().lower()


def get_client_ip(request) -> str:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
    if forwarded:
        return forwarded
    return request.META.get('REMOTE_ADDR', '') or ''


def get_device_key(request) -> tuple[str, str, str]:
    ip = get_client_ip(request)
    user_agent = (request.META.get('HTTP_USER_AGENT', '') or '')[:500]
    raw = f'{ip}|{user_agent}'
    device_key = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    return device_key, ip, user_agent


def _retry_message(lockout_minutes: int, retry_after_seconds: int) -> str:
    minutes = max(1, (retry_after_seconds + 59) // 60, lockout_minutes)
    return (
        f'Çok fazla hatalı giriş denemesi. '
        f'Lütfen {minutes} dakika sonra tekrar deneyin.'
    )


def _expired_lock_qs(model, now):
    return model.objects.filter(locked_until__lte=now)


def check_admin_login_allowed(username: str, device_key: str) -> AdminLoginCheckResult:
    settings = AdminLoginSecuritySettings.load()
    now = timezone.now()
    normalized = normalize_username(username)

    _expired_lock_qs(AdminLoginUsernameLock, now).delete()
    _expired_lock_qs(AdminLoginDeviceLock, now).delete()

    if normalized:
        user_lock = AdminLoginUsernameLock.objects.filter(username=normalized).first()
        if user_lock and user_lock.locked_until > now:
            retry = int((user_lock.locked_until - now).total_seconds())
            return AdminLoginCheckResult(
                allowed=False,
                message=_retry_message(settings.lockout_minutes, retry),
                retry_after_seconds=max(retry, 1),
                lock_type='username',
            )

    if device_key:
        device_lock = AdminLoginDeviceLock.objects.filter(device_key=device_key).first()
        if device_lock and device_lock.locked_until > now:
            retry = int((device_lock.locked_until - now).total_seconds())
            return AdminLoginCheckResult(
                allowed=False,
                message=_retry_message(settings.lockout_minutes, retry),
                retry_after_seconds=max(retry, 1),
                lock_type='device',
            )

    return AdminLoginCheckResult(allowed=True)


def record_admin_login_failure(
    username: str,
    *,
    device_key: str,
    ip_address: str = '',
    user_agent: str = '',
) -> AdminLoginCheckResult:
    settings = AdminLoginSecuritySettings.load()
    now = timezone.now()
    window_start = now - timedelta(minutes=settings.window_minutes)
    normalized = normalize_username(username)
    lockout = timedelta(minutes=settings.lockout_minutes)

    if normalized or device_key:
        AdminLoginFailedAttempt.objects.create(
            username=normalized,
            device_key=device_key,
            ip_address=ip_address or None,
            user_agent=user_agent[:500],
        )

    if normalized:
        username_failures = AdminLoginFailedAttempt.objects.filter(
            username=normalized,
            created_at__gte=window_start,
        ).count()
        if username_failures >= settings.max_attempts:
            AdminLoginUsernameLock.objects.update_or_create(
                username=normalized,
                defaults={'locked_until': now + lockout},
            )

    if device_key:
        distinct_usernames = (
            AdminLoginFailedAttempt.objects.filter(
                device_key=device_key,
                created_at__gte=window_start,
            )
            .values('username')
            .distinct()
            .count()
        )
        if distinct_usernames >= settings.max_attempts:
            AdminLoginDeviceLock.objects.update_or_create(
                device_key=device_key,
                defaults={
                    'locked_until': now + lockout,
                    'ip_address': ip_address or None,
                    'user_agent': user_agent[:500],
                },
            )

    return check_admin_login_allowed(normalized, device_key)


def clear_admin_login_success(username: str, device_key: str) -> None:
    normalized = normalize_username(username)
    if normalized:
        AdminLoginFailedAttempt.objects.filter(username=normalized).delete()
        AdminLoginUsernameLock.objects.filter(username=normalized).delete()


def reset_username_lock(username: str) -> None:
    normalized = normalize_username(username)
    if not normalized:
        return
    AdminLoginUsernameLock.objects.filter(username=normalized).delete()
    AdminLoginFailedAttempt.objects.filter(username=normalized).delete()


def reset_device_lock(device_key: str) -> None:
    if not device_key:
        return
    AdminLoginDeviceLock.objects.filter(device_key=device_key).delete()
    AdminLoginFailedAttempt.objects.filter(device_key=device_key).delete()


def prune_old_attempts() -> None:
    settings = AdminLoginSecuritySettings.load()
    cutoff = timezone.now() - timedelta(minutes=max(settings.window_minutes, settings.lockout_minutes) * 2)
    AdminLoginFailedAttempt.objects.filter(created_at__lt=cutoff).delete()
