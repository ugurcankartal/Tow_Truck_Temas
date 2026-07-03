from core.translation_utils import localized_field


def get_admin_branding_name() -> str | None:
    """Admin üst bilgi metni: varsayılan dildeki yasal unvan."""
    from core.models import SiteSettings
    from localization.services.language_resolver import resolve_active_language

    try:
        settings = SiteSettings.objects.prefetch_related('translations__language').first()
        if settings is None:
            return None

        default_language = resolve_active_language(None)
        language_code = default_language.code if default_language else None
        legal_name = localized_field(settings, 'legal_name', language_code, fallback='').strip()
        return legal_name or None
    except Exception:
        return None
