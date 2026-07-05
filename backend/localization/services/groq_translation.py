from __future__ import annotations

import json
import os
import time
from typing import Any

from django.db import transaction

from core.groq_client import GroqAPIError, GroqRateLimitError, chat_completion, parse_json_response
from localization.models import Language, UiString
from localization.services.groq_translation_progress import GroqTranslationProgress

SITE_CONTEXT = (
    'Content for a professional tow truck and roadside assistance business website. '
    'Preserve brand names, phone numbers, emails, URLs, and placeholders like '
    '{business_name}, {region}, {year}, {legal_name}, {accent}...{/accent} unchanged.'
)


def get_default_language() -> Language | None:
    return (
        Language.objects.filter(is_active=True, is_default=True).first()
        or Language.objects.filter(is_active=True, code='tr').first()
        or Language.objects.filter(is_active=True).order_by('sort_order', 'code').first()
    )


def get_target_languages(default_language: Language) -> list[Language]:
    return list(
        Language.objects.filter(is_active=True)
        .exclude(pk=default_language.pk)
        .order_by('sort_order', 'code'),
    )


def resolve_source_translations(model, preferred: Language) -> tuple[Language, Any]:
    from django.db.models import Count

    qs = model.objects.filter(language=preferred)
    if qs.exists():
        return preferred, qs

    tried = {preferred.pk}
    for code in ('tr', 'en'):
        lang = Language.objects.filter(code=code, is_active=True).exclude(pk__in=tried).first()
        if lang:
            tried.add(lang.pk)
            qs = model.objects.filter(language=lang)
            if qs.exists():
                return lang, qs

    lang_id = (
        model.objects.values('language_id')
        .annotate(c=Count('pk'))
        .order_by('-c')
        .values_list('language_id', flat=True)
        .first()
    )
    if lang_id:
        lang = Language.objects.filter(pk=lang_id).first()
        if lang:
            return lang, model.objects.filter(language=lang)

    return preferred, model.objects.none()


def _merge_parent_source(parent_attr: str):
    """Çeviri satırı boşsa FK üzerindeki ana model alanlarını kaynak olarak kullan."""

    def merge(row, payload: dict[str, Any]) -> dict[str, Any]:
        parent = getattr(row, parent_attr)
        merged: dict[str, Any] = {}
        for field, value in payload.items():
            if value in (None, '', [], {}):
                value = getattr(parent, field, None)
            if value not in (None, '', [], {}):
                merged[field] = value
        return merged

    return merge


def _bootstrap_translation_sources(
    translation_model,
    parent_attr: str,
    fields: list[str],
    source_language: Language,
    *,
    parent_queryset=None,
) -> None:
    """Varsayılan dil çeviri satırlarını ana model kayıtlarından oluşturur."""
    parent_model = translation_model._meta.get_field(parent_attr).related_model
    if parent_queryset is None:
        if parent_model.__name__ in ('SiteSettings', 'ShowcaseServiceSection'):
            parents = [parent_model.load()]
        else:
            parents = parent_model.objects.all()
            if any(getattr(f, 'name', None) == 'is_active' for f in parent_model._meta.fields):
                parents = parents.filter(is_active=True)
    else:
        parents = parent_queryset

    for parent in parents:
        defaults: dict[str, Any] = {}
        for field in fields:
            value = getattr(parent, field, None)
            if value not in (None, '', [], {}):
                defaults[field] = value
        obj, created = translation_model.objects.get_or_create(
            **{parent_attr: parent, 'language': source_language},
            defaults=defaults,
        )
        if not created:
            updates: dict[str, Any] = {}
            for field in fields:
                current = getattr(obj, field, None)
                if current not in (None, '', [], {}):
                    continue
                value = getattr(parent, field, None)
                if value not in (None, '', [], {}):
                    updates[field] = value
            if updates:
                translation_model.objects.filter(pk=obj.pk).update(**updates)


def _non_empty_fields(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if value not in (None, '', [], {})}


def translate_record_batch(
    batch: dict[str, dict[str, Any]],
    *,
    source_language: Language,
    target_language: Language,
    html_fields: frozenset[str] = frozenset(),
    list_fields: frozenset[str] = frozenset(),
    preserve_fields: frozenset[str] = frozenset(),
    context: str = '',
) -> dict[str, dict[str, Any]]:
    if not batch:
        return {}

    rules = [
        'Return ONLY valid JSON.',
        'Top-level keys must exactly match the input record IDs.',
        'Each record must keep the same field names as the input.',
        'Do not add or remove fields.',
        'Preserve brand names, proper nouns, URLs, emails, phone numbers, and @handles unchanged.',
    ]
    if html_fields:
        rules.append(
            f'Preserve HTML tags and attributes in these fields: {", ".join(sorted(html_fields))}.',
        )
    if list_fields:
        rules.append(
            f'These fields are JSON arrays; return translated arrays with the same length: '
            f'{", ".join(sorted(list_fields))}.',
        )
    if preserve_fields:
        rules.append(
            f'Copy these fields unchanged from input: {", ".join(sorted(preserve_fields))}.',
        )
    if context:
        rules.append(context)

    system_prompt = (
        f'You are a professional translator. '
        f'Translate from {source_language.name_native} ({source_language.code}) '
        f'to {target_language.name_native} ({target_language.code}). '
        + ' '.join(rules)
    )

    user_prompt = json.dumps(batch, ensure_ascii=False, indent=2)
    content = chat_completion(
        [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
    )
    translated = parse_json_response(content)

    if not isinstance(translated, dict):
        raise GroqAPIError('Groq çeviri yanıtı geçerli bir JSON nesnesi değil.')

    for record_id, fields in batch.items():
        if record_id not in translated:
            raise GroqAPIError(f"Groq yanıtında '{record_id}' kaydı eksik.")
        result_fields = translated[record_id]
        if not isinstance(result_fields, dict):
            raise GroqAPIError(f"Groq yanıtında '{record_id}' alanları geçersiz.")
        for field in preserve_fields:
            if field in fields:
                result_fields[field] = fields[field]

    return translated


def _new_stats() -> dict[str, int]:
    return {'created': 0, 'updated': 0, 'skipped': 0, 'languages': 0, 'failed': 0}


def _groq_batch_pause_seconds() -> float:
    raw = os.getenv('GROQ_BATCH_PAUSE_SECONDS', '1')
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 1.0


def _groq_aborted(stats: dict[str, int]) -> bool:
    return bool(stats.get('_abort'))


def public_groq_stats(stats: dict[str, int]) -> dict[str, int]:
    return {key: value for key, value in stats.items() if not str(key).startswith('_')}


def _record_groq_failure(
    exc: Exception,
    *,
    stats: dict[str, int],
    progress: GroqTranslationProgress | None,
    label: str,
) -> None:
    stats['failed'] += 1
    message = str(exc)
    if progress:
        progress.advance(label=label, error=message)
    if isinstance(exc, GroqRateLimitError) and exc.is_daily_limit:
        stats['_abort'] = True
        stats['_abort_message'] = message


def _field_value_for_compare(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value


def _needs_groq_translation(
    source_row,
    target_row,
    fields: list[str],
    preserve_fields: frozenset[str] = frozenset(),
    *,
    source_payload: dict[str, Any] | None = None,
) -> bool:
    if target_row is None:
        return True

    needs_work = False
    for field in fields:
        if field in preserve_fields:
            continue
        if source_payload is not None:
            source_val = _field_value_for_compare(source_payload.get(field, '') or '')
        else:
            source_val = _field_value_for_compare(getattr(source_row, field, None) or '')
        if source_val in (None, '', [], {}):
            continue
        target_val = _field_value_for_compare(getattr(target_row, field, None) or '')
        if target_val in (None, '', [], {}):
            needs_work = True
        elif target_val == source_val:
            needs_work = True
    return needs_work


def _collect_pending_records(
    *,
    source_rows,
    parent_attr: str,
    fields: list[str],
    model,
    target_language: Language,
    stats: dict[str, int],
    row_transform=None,
    preserve_fields: frozenset[str] = frozenset(),
) -> list[tuple[Any, str, dict[str, Any]]]:
    pending: list[tuple[Any, str, dict[str, Any]]] = []

    for row in source_rows:
        parent_id = getattr(row, parent_attr + '_id')
        existing = model.objects.filter(
            **{f'{parent_attr}_id': parent_id, 'language': target_language},
        ).first()

        payload = {field: getattr(row, field) for field in fields}
        if row_transform:
            payload = row_transform(row, payload)

        if existing and not _needs_groq_translation(
            row,
            existing,
            fields,
            preserve_fields,
            source_payload=payload,
        ):
            stats['skipped'] += 1
            continue

        record_id = str(parent_id)
        payload = _non_empty_fields(payload)
        if not payload:
            stats['skipped'] += 1
            continue
        pending.append((row, record_id, payload))

    return pending


def _translate_pending_records(
    *,
    pending: list[tuple[Any, str, dict[str, Any]]],
    parent_attr: str,
    fields: list[str],
    model,
    unique_attrs: dict[str, Any],
    stats: dict[str, int],
    source_language: Language,
    target_language: Language,
    html_fields: frozenset[str] = frozenset(),
    list_fields: frozenset[str] = frozenset(),
    preserve_fields: frozenset[str] = frozenset(),
    context: str = '',
    progress: GroqTranslationProgress | None = None,
    progress_label: str = '',
) -> None:
    if not pending:
        return

    stats['languages'] += 1
    pause_seconds = _groq_batch_pause_seconds()

    for index, (source_row, record_id, payload) in enumerate(pending):
        if _groq_aborted(stats):
            return
        label = f'{progress_label} → {target_language.code} (#{record_id})'
        try:
            translated = translate_record_batch(
                {record_id: payload},
                source_language=source_language,
                target_language=target_language,
                html_fields=html_fields,
                list_fields=list_fields,
                preserve_fields=preserve_fields,
                context=context,
            )
            field_values = translated[record_id]
            with transaction.atomic():
                parent_id = getattr(source_row, parent_attr + '_id')
                lookup = {
                    **unique_attrs,
                    parent_attr + '_id': parent_id,
                    'language': target_language,
                }
                defaults = {field: field_values.get(field, '') for field in fields}
                for field in preserve_fields:
                    if field in payload:
                        defaults[field] = payload[field]
                _, created = model.objects.update_or_create(**lookup, defaults=defaults)
                if created:
                    stats['created'] += 1
                else:
                    stats['updated'] += 1
            if progress:
                progress.advance(label=label)
        except (GroqAPIError, ValueError, TypeError, KeyError) as exc:
            _record_groq_failure(exc, stats=stats, progress=progress, label=label)
            if _groq_aborted(stats):
                return

        if pause_seconds and index < len(pending) - 1 and not _groq_aborted(stats):
            time.sleep(pause_seconds)


def _translate_model_batch(
    *,
    source_rows,
    parent_attr: str,
    fields: list[str],
    model,
    unique_attrs: dict[str, Any],
    stats: dict[str, int],
    source_language: Language,
    target_language: Language,
    html_fields: frozenset[str] = frozenset(),
    list_fields: frozenset[str] = frozenset(),
    preserve_fields: frozenset[str] = frozenset(),
    context: str = '',
    row_transform=None,
    progress: GroqTranslationProgress | None = None,
    progress_label: str = '',
    dry_run: bool = False,
) -> int:
    if stats.get('_abort'):
        return 0

    pending = _collect_pending_records(
        source_rows=source_rows,
        parent_attr=parent_attr,
        fields=fields,
        model=model,
        target_language=target_language,
        stats=stats if not dry_run else _new_stats(),
        row_transform=row_transform,
        preserve_fields=preserve_fields,
    )
    if dry_run:
        return len(pending)

    _translate_pending_records(
        pending=pending,
        parent_attr=parent_attr,
        fields=fields,
        model=model,
        unique_attrs=unique_attrs,
        stats=stats,
        source_language=source_language,
        target_language=target_language,
        html_fields=html_fields,
        list_fields=list_fields,
        preserve_fields=preserve_fields,
        context=context,
        progress=progress,
        progress_label=progress_label,
    )
    return 0


def _run_model_handler(
    model,
    parent_attr: str,
    fields: list[str],
    *,
    source_language: Language,
    target_languages: list[Language],
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
    html_fields: frozenset[str] = frozenset(),
    list_fields: frozenset[str] = frozenset(),
    preserve_fields: frozenset[str] = frozenset(),
    context: str = SITE_CONTEXT,
    progress_label: str = '',
    row_transform=None,
    parent_queryset=None,
    bootstrap_sources: bool = True,
) -> dict[str, int] | int:
    stats = stats or _new_stats()

    if bootstrap_sources:
        _bootstrap_translation_sources(
            model,
            parent_attr,
            fields,
            source_language,
            parent_queryset=parent_queryset,
        )

    if row_transform is None:
        row_transform = _merge_parent_source(parent_attr)

    source_language, source_rows = resolve_source_translations(model, source_language)
    if not source_rows.exists():
        stats['_abort_message'] = (
            'Kaynak dilde çevrilecek içerik bulunamadı. '
            'Ana kayıtlarda metin olduğundan emin olun.'
        )
        return 0 if dry_run else stats

    source_rows = source_rows.select_related(parent_attr)
    total = 0
    for target_language in target_languages:
        if _groq_aborted(stats):
            break
        total += _translate_model_batch(
            source_rows=source_rows,
            parent_attr=parent_attr,
            fields=fields,
            model=model,
            unique_attrs={},
            stats=stats,
            source_language=source_language,
            target_language=target_language,
            html_fields=html_fields,
            list_fields=list_fields,
            preserve_fields=preserve_fields,
            context=context,
            progress=progress,
            progress_label=progress_label,
            dry_run=dry_run,
            row_transform=row_transform,
        )
    return total if dry_run else stats


SITE_SETTINGS_GROQ_FIELDS = [
    'meta_title', 'meta_description', 'meta_keywords',
    'business_name', 'legal_name', 'tagline',
    'street', 'district', 'city', 'region',
    'footer_copyright', 'hero_intro_badge',
    'hero_intro_title', 'hero_intro_body',
    'area_served',
]


def translate_site_settings(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from core.models import SiteSettingsTranslation

    return _run_model_handler(
        SiteSettingsTranslation,
        'settings',
        SITE_SETTINGS_GROQ_FIELDS,
        source_language=source_language,
        target_languages=target_languages,
        stats=stats,
        progress=progress,
        dry_run=dry_run,
        html_fields=frozenset({'hero_intro_title', 'hero_intro_body'}),
        list_fields=frozenset({'area_served'}),
        context=SITE_CONTEXT,
        progress_label='Site ayarı',
    )


def translate_faq(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from core.models import FAQTranslation

    return _run_model_handler(
        FAQTranslation,
        'faq',
        ['question', 'answer'],
        source_language=source_language,
        target_languages=target_languages,
        stats=stats,
        progress=progress,
        dry_run=dry_run,
        context=SITE_CONTEXT + ' FAQ questions and answers for customers.',
        progress_label='SSS',
    )


def translate_content_zone(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from content.models import ContentZoneTranslation

    return _run_model_handler(
        ContentZoneTranslation,
        'zone',
        ['name', 'description'],
        source_language=source_language,
        target_languages=target_languages,
        stats=stats,
        progress=progress,
        dry_run=dry_run,
        context=SITE_CONTEXT,
        progress_label='İçerik bölgesi',
    )


def translate_site_image(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from content.models import SiteImageTranslation

    return _run_model_handler(
        SiteImageTranslation,
        'site_image',
        ['title', 'subtitle', 'description', 'alt_text'],
        source_language=source_language,
        target_languages=target_languages,
        stats=stats,
        progress=progress,
        dry_run=dry_run,
        context=SITE_CONTEXT + ' Image captions and SEO alt text.',
        progress_label='Site görseli',
    )


def translate_showcase_stat(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from showcase.models import ShowcaseStatTranslation

    return _run_model_handler(
        ShowcaseStatTranslation,
        'stat',
        ['value', 'label'],
        source_language=source_language,
        target_languages=target_languages,
        stats=stats,
        progress=progress,
        dry_run=dry_run,
        preserve_fields=frozenset({'value'}),
        context=SITE_CONTEXT + ' Stat values like 7/24 or 15 min should stay in value field.',
        progress_label='Vitrin istatistiği',
    )


def translate_showcase_section(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from showcase.models import ShowcaseServiceSectionTranslation

    return _run_model_handler(
        ShowcaseServiceSectionTranslation,
        'section',
        ['badge', 'title', 'description'],
        source_language=source_language,
        target_languages=target_languages,
        stats=stats,
        progress=progress,
        dry_run=dry_run,
        html_fields=frozenset({'description'}),
        context=SITE_CONTEXT,
        progress_label='Hizmetler bölümü',
    )


def translate_showcase_service(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from showcase.models import ShowcaseServiceTranslation

    return _run_model_handler(
        ShowcaseServiceTranslation,
        'service',
        ['title', 'description'],
        source_language=source_language,
        target_languages=target_languages,
        stats=stats,
        progress=progress,
        dry_run=dry_run,
        context=SITE_CONTEXT + ' Service cards for towing and roadside assistance.',
        progress_label='Hizmet kartı',
    )


def translate_ui_strings(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    stats = stats or _new_stats()
    source_language, source_qs = resolve_source_translations(UiString, source_language)
    source_rows = list(source_qs.select_related('key').order_by('key__key'))
    if not source_rows:
        return 0 if dry_run else stats
    total = 0

    for target_language in target_languages:
        if _groq_aborted(stats):
            break
        pending: list[tuple[Any, str, dict[str, Any]]] = []
        key_map = {}
        for row in source_rows:
            existing = UiString.objects.filter(language=target_language, key=row.key).first()
            if existing and not _needs_groq_translation(row, existing, ['text']):
                stats['skipped'] += 1
                continue
            if not row.text:
                stats['skipped'] += 1
                continue
            pending.append((row, row.key.key, {'text': row.text}))
            key_map[row.key.key] = row.key

        if dry_run:
            total += len(pending)
            continue

        if not pending:
            continue

        stats['languages'] += 1
        pause_seconds = _groq_batch_pause_seconds()
        for index, (row, key_name, payload) in enumerate(pending):
            if _groq_aborted(stats):
                break
            label = f'UI metni → {target_language.code} ({key_name})'
            try:
                translated = translate_record_batch(
                    {key_name: payload},
                    source_language=source_language,
                    target_language=target_language,
                    context=(
                        'Short UI labels for a tow truck business website. '
                        'Translate only the text values; keep tone concise.'
                    ),
                )
                text = translated[key_name].get('text', '')
                with transaction.atomic():
                    _, created = UiString.objects.update_or_create(
                        language=target_language,
                        key=key_map[key_name],
                        defaults={'text': text},
                    )
                    if created:
                        stats['created'] += 1
                    else:
                        stats['updated'] += 1
                if progress:
                    progress.advance(label=label)
            except (GroqAPIError, ValueError, TypeError, KeyError) as exc:
                _record_groq_failure(exc, stats=stats, progress=progress, label=label)
                if _groq_aborted(stats):
                    break

            if pause_seconds and index < len(pending) - 1 and not _groq_aborted(stats):
                time.sleep(pause_seconds)

        if _groq_aborted(stats):
            break

    return total if dry_run else stats


def translate_site_contact(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from core.models import SiteContactTranslation

    return _run_model_handler(
        SiteContactTranslation,
        'contact',
        ['label'],
        source_language=source_language,
        target_languages=target_languages,
        stats=stats,
        progress=progress,
        dry_run=dry_run,
        context=SITE_CONTEXT + ' Short contact field labels (Phone, WhatsApp, Emergency line).',
        progress_label='İletişim etiketi',
        row_transform=_merge_parent_source('contact'),
    )


HANDLERS = {
    'site_settings': translate_site_settings,
    'site_contact': translate_site_contact,
    'faq': translate_faq,
    'content_zone': translate_content_zone,
    'site_image': translate_site_image,
    'showcase_stat': translate_showcase_stat,
    'showcase_section': translate_showcase_section,
    'showcase_service': translate_showcase_service,
    'ui_string': translate_ui_strings,
}


def count_handler_work(
    handler_name: str,
    source_language: Language,
    target_languages: list[Language],
) -> int:
    handler = HANDLERS[handler_name]
    result = handler(source_language, target_languages, dry_run=True)
    return int(result) if isinstance(result, int) else 0


def run_groq_translation(
    handler_name: str,
    *,
    progress: GroqTranslationProgress | None = None,
) -> dict[str, int]:
    handler = HANDLERS.get(handler_name)
    if handler is None:
        raise ValueError(f'Bilinmeyen çeviri işleyicisi: {handler_name}')

    default_language = get_default_language()
    if default_language is None:
        raise GroqAPIError('Varsayılan dil bulunamadı.')

    target_languages = get_target_languages(default_language)
    if not target_languages:
        raise GroqAPIError('Çevrilecek hedef dil yok.')

    if progress:
        total = count_handler_work(handler_name, default_language, target_languages)
        progress.init(total)

    stats = _new_stats()
    handler(
        default_language,
        target_languages,
        stats=stats,
        progress=progress,
        dry_run=False,
    )
    public = public_groq_stats(stats)
    if not any(public.values()) and not stats.get('_abort'):
        if stats.get('skipped', 0) > 0:
            stats['_abort_message'] = (
                f'Tüm kayıtlar zaten çevrilmiş görünüyor ({stats["skipped"]} atlandı).'
            )
        elif not stats.get('_abort_message'):
            stats['_abort_message'] = (
                'İşlenecek çeviri bulunamadı. '
                'Kaynak dilde metin olduğundan ve hedef dil kayıtlarının eksik/boş olduğundan emin olun.'
            )
    return stats
