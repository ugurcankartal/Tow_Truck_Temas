from localization.models import UiString
from localization.services.language_resolver import resolve_active_language


class DatabaseI18nBundleProvider:
    """UI metinlerini veritabanından yükler."""

    def build_bundle(self, language_code: str | None) -> tuple[str | None, dict[str, str]]:
        language = resolve_active_language(language_code)
        if language is None:
            return None, {}
        rows = UiString.objects.filter(language=language).select_related('key')
        return language.code, {row.key.key: row.text for row in rows}


default_i18n_bundle_provider = DatabaseI18nBundleProvider()
