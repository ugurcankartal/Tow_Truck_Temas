from __future__ import annotations

import hashlib
import ipaddress


def get_client_ip(request) -> str:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
    if forwarded:
        return forwarded
    real_ip = request.META.get('HTTP_X_REAL_IP', '').strip()
    if real_ip:
        return real_ip
    cf_ip = request.META.get('HTTP_CF_CONNECTING_IP', '').strip()
    if cf_ip:
        return cf_ip
    return request.META.get('REMOTE_ADDR', '') or ''


def is_public_ip(ip: str) -> bool:
    if not ip:
        return False
    try:
        return ipaddress.ip_address(ip).is_global
    except ValueError:
        return False


def build_visitor_key(ip: str, user_agent: str, session_key: str = '') -> str:
    raw = f'{ip}|{user_agent}|{session_key}'.encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def header_value(request, name: str, default: str = '') -> str:
    return (request.META.get(name, '') or default).strip()


def get_accept_language(request) -> str:
    return header_value(request, 'HTTP_ACCEPT_LANGUAGE')[:255]
