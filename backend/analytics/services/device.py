from __future__ import annotations

from dataclasses import dataclass

from user_agents import parse

from analytics.models import SiteVisit


@dataclass(frozen=True)
class DeviceInfo:
    device_type: str
    device_brand: str
    device_model: str
    browser: str
    browser_version: str
    os_name: str
    os_version: str
    is_bot: bool


def parse_device_info(user_agent: str) -> DeviceInfo:
    ua = parse(user_agent or '')

    if ua.is_bot:
        device_type = SiteVisit.DeviceType.BOT
    elif ua.is_tablet:
        device_type = SiteVisit.DeviceType.TABLET
    elif ua.is_mobile:
        device_type = SiteVisit.DeviceType.MOBILE
    elif ua.is_pc:
        device_type = SiteVisit.DeviceType.DESKTOP
    else:
        device_type = SiteVisit.DeviceType.OTHER

    return DeviceInfo(
        device_type=device_type,
        device_brand=(ua.device.brand or '')[:64],
        device_model=(ua.device.model or '')[:128],
        browser=(ua.browser.family or '')[:64],
        browser_version=(ua.browser.version_string or '')[:32],
        os_name=(ua.os.family or '')[:64],
        os_version=(ua.os.version_string or '')[:32],
        is_bot=bool(ua.is_bot),
    )
