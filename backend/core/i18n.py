from localization.services.language_resolver import resolve_active_language

# API mesajları — UiString bundle'a taşınana kadar sabit sözlük
TEXTS = {
    'contact_success': {
        'tr': 'Mesajınız alındı. En kısa sürede dönüş yapacağız.',
        'en': 'Your message has been received. We will get back to you shortly.',
    },
    'phone_invalid': {
        'tr': 'Geçerli bir telefon numarası girin.',
        'en': 'Please enter a valid phone number.',
    },
    'name_required': {
        'tr': 'Ad soyad alanı zorunludur.',
        'en': 'Name is required.',
    },
    'message_required': {
        'tr': 'Mesaj alanı zorunludur.',
        'en': 'Message is required.',
    },
    'hero_badge_default': {
        'tr': 'Aktif Hizmet',
        'en': 'Active Service',
    },
}


def resolve_request_language(request) -> str:
    """?lang= veya Accept-Language ile aktif dil kodunu döner."""
    query_lang = (request.GET.get('lang') or '').strip()
    if query_lang:
        language = resolve_active_language(query_lang)
        if language:
            return language.code
    accept = (request.headers.get('Accept-Language') or '').strip()
    if accept:
        first = accept.split(',')[0].strip().split(';')[0].strip()
        language = resolve_active_language(first)
        if language:
            return language.code
    language = resolve_active_language(None)
    return language.code if language else 'tr'


def localized_text(key: str, lang: str) -> str:
    entry = TEXTS.get(key, {})
    return entry.get(lang) or entry.get('tr', '')
