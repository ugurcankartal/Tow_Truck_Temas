from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


class TranslationAdminMixin:
    """Çeviri modelleri için ortak admin ayarları."""

    list_filter = ('language',)
    autocomplete_fields = ('language',)


def _admin_changelist_url(name: str) -> str:
    view_name = name if name.startswith('admin:') else f'admin:{name}'
    return reverse(view_name)


def translation_list_link(
    obj,
    *,
    changelist_name: str,
    filter_param: str,
    label: str = 'Çevirileri',
):
    """Ana kayıt listesinde filtrelenmiş çeviri changelist linki."""
    if not obj or not obj.pk:
        return '—'
    url = f'{_admin_changelist_url(changelist_name)}?{filter_param}={obj.pk}'
    return format_html('<a href="{}">{}</a>', url, label)


def all_translations_link(*, changelist_name: str, label: str = 'Tüm çevirileri'):
    """Uygulama geneli çeviri listesine link (singleton / üst bilgi)."""
    url = _admin_changelist_url(changelist_name)
    return format_html('<a href="{}">{}</a>', url, label)
