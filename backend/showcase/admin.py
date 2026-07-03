from django.contrib import admin
from django.utils.html import format_html

from localization.admin_helpers import (
    TranslationAdminMixin,
    all_translations_link,
    translation_list_link,
)
from localization.admin_mixins import GroqTranslateAdminMixin

from .models import (
    ShowcaseService,
    ShowcaseServiceSection,
    ShowcaseServiceSectionTranslation,
    ShowcaseServiceTranslation,
    ShowcaseStat,
    ShowcaseStatTranslation,
)


class ShowcaseStatTranslationInline(admin.TabularInline):
    model = ShowcaseStatTranslation
    extra = 0
    fields = ('language', 'value', 'label')


@admin.register(ShowcaseStatTranslation)
class ShowcaseStatTranslationAdmin(GroqTranslateAdminMixin, TranslationAdminMixin, admin.ModelAdmin):
    groq_translation_handler = 'showcase_stat'
    list_display = ('stat', 'language', 'value', 'label')
    search_fields = ('value', 'label', 'stat__value', 'stat__label')
    autocomplete_fields = ('stat', 'language')


@admin.register(ShowcaseStat)
class ShowcaseStatAdmin(admin.ModelAdmin):
    list_display = ('value', 'label', 'order', 'is_active', 'translations_link')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('value', 'label')
    ordering = ('order', 'id')
    inlines = [ShowcaseStatTranslationInline]

    @admin.display(description='Çevirileri')
    def translations_link(self, obj):
        return translation_list_link(
            obj,
            changelist_name='showcase_showcasestattranslation_changelist',
            filter_param='stat__id__exact',
        )


class ShowcaseServiceSectionTranslationInline(admin.StackedInline):
    model = ShowcaseServiceSectionTranslation
    extra = 0
    fields = ('language', 'badge', 'title', 'description')


@admin.register(ShowcaseServiceSectionTranslation)
class ShowcaseServiceSectionTranslationAdmin(GroqTranslateAdminMixin, TranslationAdminMixin, admin.ModelAdmin):
    groq_translation_handler = 'showcase_section'
    list_display = ('section', 'language', 'title', 'badge')
    search_fields = ('title', 'badge', 'description')
    autocomplete_fields = ('section', 'language')


@admin.register(ShowcaseServiceSection)
class ShowcaseServiceSectionAdmin(admin.ModelAdmin):
    inlines = [ShowcaseServiceSectionTranslationInline]
    search_fields = ('title', 'badge')
    readonly_fields = ('translations_admin_link',)
    fieldsets = (
        ('Çeviriler', {
            'fields': ('translations_admin_link',),
        }),
        ('Hizmetler başlığı (varsayılan)', {
            'fields': ('badge', 'title', 'description'),
            'description': (
                'Ana sayfa #hizmetler bölümü. Dil çevirileri için alttaki satırları veya '
                'Hizmetler bölümü çevirileri listesini kullanın.'
            ),
        }),
    )

    def has_add_permission(self, request):
        return not ShowcaseServiceSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description='Hizmetler bölümü çevirileri')
    def translations_admin_link(self, obj):
        if not obj or not obj.pk:
            return all_translations_link(
                changelist_name='showcase_showcaseservicesectiontranslation_changelist',
            )
        filtered = translation_list_link(
            obj,
            changelist_name='showcase_showcaseservicesectiontranslation_changelist',
            filter_param='section__id__exact',
        )
        all_link = all_translations_link(
            changelist_name='showcase_showcaseservicesectiontranslation_changelist',
            label='Tümünü gör',
        )
        return format_html('{} · {}', filtered, all_link)


class ShowcaseServiceTranslationInline(admin.TabularInline):
    model = ShowcaseServiceTranslation
    extra = 0
    fields = ('language', 'title', 'description')


@admin.register(ShowcaseServiceTranslation)
class ShowcaseServiceTranslationAdmin(GroqTranslateAdminMixin, TranslationAdminMixin, admin.ModelAdmin):
    groq_translation_handler = 'showcase_service'
    list_display = ('service', 'language', 'title')
    search_fields = ('title', 'description', 'service__title')
    autocomplete_fields = ('service', 'language')


@admin.register(ShowcaseService)
class ShowcaseServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_active', 'translations_link')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    ordering = ('order', 'id')
    inlines = [ShowcaseServiceTranslationInline]

    @admin.display(description='Çevirileri')
    def translations_link(self, obj):
        return translation_list_link(
            obj,
            changelist_name='showcase_showcaseservicetranslation_changelist',
            filter_param='service__id__exact',
        )
