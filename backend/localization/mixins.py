class TranslatableMixin:
    """Çeviri tablosu olan modeller için ortak get_translation."""

    def get_translation(self, language_code=None):
        from localization.services.language_resolver import resolve_active_language

        translations = self.translations.select_related('language')
        if language_code:
            translation = translations.filter(
                language__code=language_code,
                language__is_active=True,
            ).first()
            if translation:
                return translation

        language = resolve_active_language(language_code)
        if language:
            translation = translations.filter(language_id=language.pk).first()
            if translation:
                return translation

        return (
            translations.filter(language__is_default=True).first()
            or translations.order_by('language__sort_order', 'language__code').first()
        )
