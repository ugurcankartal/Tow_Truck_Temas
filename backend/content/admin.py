from django.contrib import admin
from django.utils.html import format_html

from localization.admin_helpers import TranslationAdminMixin, translation_list_link
from localization.admin_mixins import GroqTranslateAdminMixin

from .models import ContentZone, ContentZoneTranslation, SiteImage, SiteImagePlacement, SiteImageTranslation


class ContentZoneTranslationInline(admin.TabularInline):
    model = ContentZoneTranslation
    extra = 0
    fields = ('language', 'name', 'description')


@admin.register(ContentZoneTranslation)
class ContentZoneTranslationAdmin(GroqTranslateAdminMixin, TranslationAdminMixin, admin.ModelAdmin):
    groq_translation_handler = 'content_zone'
    list_display = ('zone', 'language', 'name')
    search_fields = ('name', 'description', 'zone__code', 'zone__name')
    autocomplete_fields = ('zone', 'language')


@admin.register(ContentZone)
class ContentZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'translations_link')
    readonly_fields = ('code',)
    search_fields = ('name', 'code')
    inlines = [ContentZoneTranslationInline]

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description='Çevirileri')
    def translations_link(self, obj):
        return translation_list_link(
            obj,
            changelist_name='content_contentzonetranslation_changelist',
            filter_param='zone__id__exact',
        )


class SiteImagePlacementInline(admin.TabularInline):
    model = SiteImagePlacement
    extra = 1
    fields = ('zone', 'order', 'is_active')


class SiteImageTranslationInline(admin.TabularInline):
    model = SiteImageTranslation
    extra = 0
    fields = ('language', 'title', 'subtitle', 'description', 'alt_text')


@admin.register(SiteImageTranslation)
class SiteImageTranslationAdmin(GroqTranslateAdminMixin, TranslationAdminMixin, admin.ModelAdmin):
    groq_translation_handler = 'site_image'
    list_display = ('site_image', 'language', 'title')
    search_fields = ('title', 'subtitle', 'description', 'alt_text', 'site_image__title')
    autocomplete_fields = ('site_image', 'language')


@admin.register(SiteImage)
class SiteImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'zone_labels', 'is_active', 'translations_link')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'description', 'alt_text')
    inlines = [SiteImagePlacementInline, SiteImageTranslationInline]
    readonly_fields = ('image_preview_large',)
    fieldsets = (
        ('Görsel', {
            'fields': (
                'image',
                'image_url',
                'image_preview_large',
            ),
            'description': 'Yüklü görsel varsa o kullanılır; yoksa Görsel URL.',
        }),
        ('Metin (varsayılan)', {
            'fields': ('title', 'subtitle', 'description', 'alt_text', 'is_active'),
            'description': 'Dil çevirileri için alttaki satırları veya Site görseli çevirileri listesini kullanın.',
        }),
    )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        self._request = request
        return super().changeform_view(request, object_id, form_url, extra_context)

    def _preview_url(self, obj):
        if obj.image:
            url = obj.image.url
            request = getattr(self, '_request', None)
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return obj.image_url or ''

    @admin.display(description='Önizleme')
    def image_preview(self, obj):
        url = self._preview_url(obj)
        if not url:
            return '—'
        return format_html(
            '<img src="{}" style="max-height:48px;max-width:80px;object-fit:cover;border-radius:4px;" />',
            url,
        )

    @admin.display(description='Önizleme')
    def image_preview_large(self, obj):
        if not obj.pk:
            return 'Kayıt sonrası önizleme görünür.'
        url = self._preview_url(obj)
        if not url:
            return '—'
        return format_html(
            '<img src="{}" style="max-height:200px;max-width:400px;object-fit:contain;border-radius:8px;" />',
            url,
        )

    @admin.display(description='Çevirileri')
    def translations_link(self, obj):
        return translation_list_link(
            obj,
            changelist_name='content_siteimagetranslation_changelist',
            filter_param='site_image__id__exact',
        )


@admin.register(SiteImagePlacement)
class SiteImagePlacementAdmin(admin.ModelAdmin):
    list_display = ('site_image', 'zone', 'order', 'is_active')
    list_filter = ('zone', 'is_active')
    list_editable = ('zone', 'order', 'is_active')
    search_fields = ('site_image__title', 'zone__name')
    autocomplete_fields = ('site_image', 'zone')
