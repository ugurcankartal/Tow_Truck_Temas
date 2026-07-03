"""Çeviri tablosundan alan okuma; yoksa ana modeldeki alana düşer."""


def localized_field(obj, field: str, language_code: str | None, fallback=''):
    translation = obj.get_translation(language_code)
    if translation is not None:
        value = getattr(translation, field, None)
        if value not in (None, ''):
            return value
    return getattr(obj, field, fallback) or fallback
