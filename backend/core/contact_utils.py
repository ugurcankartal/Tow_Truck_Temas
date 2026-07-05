import re


def contact_href(contact_type: str, value: str) -> str:
    value = (value or '').strip()
    if not value:
        return ''

    if contact_type == 'phone':
        digits = re.sub(r'\D', '', value)
        return f'tel:+{digits}' if digits else ''
    if contact_type == 'email':
        return f'mailto:{value}'
    if contact_type == 'url':
        if value.startswith(('http://', 'https://', 'tel:', 'mailto:')):
            return value
        return f'https://{value}'
    return ''


def serialize_site_contacts(settings, language_code: str) -> list[dict]:
    from core.translation_utils import localized_field
    from localization.models import Language

    default_code = (
        Language.objects.filter(is_active=True, is_default=True)
        .values_list('code', flat=True)
        .first()
        or 'tr'
    )

    contacts = []
    qs = (
        settings.contacts.filter(is_active=True)
        .prefetch_related('translations__language')
        .order_by('order', 'id')
    )
    for contact in qs:
        if language_code == default_code:
            label = contact.label
        else:
            label = localized_field(contact, 'label', language_code) or contact.label
        value = contact.value
        contacts.append(
            {
                'id': contact.id,
                'label': label,
                'value': value,
                'href': contact_href(contact.contact_type, value),
                'contact_type': contact.contact_type,
                'is_primary': contact.is_primary,
                'order': contact.order,
            },
        )
    return contacts


def primary_contact(contacts: list[dict]) -> dict | None:
    for contact in contacts:
        if contact.get('is_primary'):
            return contact
    for contact in contacts:
        if contact.get('contact_type') == 'phone':
            return contact
    return contacts[0] if contacts else None
