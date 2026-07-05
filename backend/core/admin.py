from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from localization.admin_helpers import (
    TranslationAdminMixin,
    all_translations_link,
    translation_list_link,
)
from localization.admin_mixins import GroqTranslateAdminMixin

from .forms import SiteSettingsAdminForm
from .models import (
    ContactMessage,
    FAQ,
    FAQTranslation,
    SiteContact,
    SiteContactTranslation,
    SiteSettings,
    SiteSettingsTranslation,
)


class SiteContactTranslationInline(admin.TabularInline):
    model = SiteContactTranslation
    extra = 0
    fields = ('language', 'label')


class SiteContactInline(admin.TabularInline):
    model = SiteContact
    fk_name = 'settings'
    extra = 1
    min_num = 0
    verbose_name = 'İletişim'
    verbose_name_plural = 'İletişim bilgileri'
    fields = ('label', 'contact_type', 'value', 'order', 'is_active', 'is_primary')
    ordering = ('order', 'id')
    show_change_link = True


class SiteSettingsTranslationInline(admin.StackedInline):
    model = SiteSettingsTranslation
    extra = 0
    fields = (
        'language',
        'meta_title',
        'meta_description',
        'meta_keywords',
        'business_name',
        'legal_name',
        'tagline',
        'street',
        'district',
        'city',
        'region',
        'footer_copyright',
        'hero_intro_badge',
        'hero_intro_title',
        'hero_intro_body',
        'area_served',
    )


@admin.register(SiteContact)
class SiteContactAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'contact_type', 'order', 'is_active', 'is_primary', 'settings')
    list_editable = ('order', 'is_active', 'is_primary')
    list_filter = ('contact_type', 'is_active', 'is_primary')
    search_fields = ('label', 'value')
    inlines = [SiteContactTranslationInline]


@admin.register(SiteContactTranslation)
class SiteContactTranslationAdmin(GroqTranslateAdminMixin, TranslationAdminMixin, admin.ModelAdmin):
    groq_translation_handler = 'site_contact'
    list_display = ('contact', 'language', 'label')
    search_fields = ('label', 'contact__label', 'contact__value')
    autocomplete_fields = ('contact', 'language')


@admin.register(SiteSettingsTranslation)
class SiteSettingsTranslationAdmin(GroqTranslateAdminMixin, TranslationAdminMixin, admin.ModelAdmin):
    groq_translation_handler = 'site_settings'
    list_display = ('settings', 'language', 'business_name', 'meta_title')
    search_fields = (
        'business_name',
        'meta_title',
        'meta_description',
        'legal_name',
        'tagline',
    )
    autocomplete_fields = ('settings', 'language')
    fieldsets = (
        (None, {'fields': ('settings', 'language')}),
        ('SEO', {'fields': ('meta_title', 'meta_description', 'meta_keywords')}),
        ('İşletme', {'fields': ('business_name', 'legal_name', 'tagline')}),
        ('Adres', {'fields': ('street', 'district', 'city', 'region', 'area_served')}),
        ('Hero', {'fields': ('hero_intro_badge', 'hero_intro_title', 'hero_intro_body')}),
        ('Footer', {'fields': ('footer_copyright',)}),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsAdminForm
    change_form_template = 'admin/core/sitesettings/change_form.html'
    inlines = [SiteContactInline, SiteSettingsTranslationInline]
    search_fields = ('business_name', 'legal_name', 'meta_title')
    readonly_fields = ('updated_at', 'logo_preview', 'favicon_preview', 'translations_admin_link', 'contacts_admin_link')
    fieldsets = (
        ('Çeviriler', {
            'fields': ('translations_admin_link',),
            'description': 'Tüm dil çevirilerini ayrı listeden de yönetebilirsiniz.',
        }),
        ('SEO / GEO', {
            'fields': (
                'meta_title', 'meta_description', 'meta_keywords',
                'canonical_url', 'og_image_url', 'robots', 'site_url',
            ),
        }),
        ('İşletme', {
            'fields': ('business_name', 'legal_name', 'tagline', 'email', 'contacts_admin_link'),
            'description': (
                'Hemen altındaki “İletişim bilgileri” tablosundan telefon, WhatsApp vb. '
                'satırları ekleyin. Tablo görünmüyorsa “İletişim kayıtları” linkini kullanın.'
            ),
        }),
        ('Hero Giriş Metni', {
            'fields': ('hero_intro_badge', 'hero_intro_title', 'hero_intro_body'),
            'description': (
                'Slider altındaki başlık ve açıklama. TipTap editörü kullanılır. '
                'Yer tutucular: {business_name}, {region}. '
                'Gradient vurgu: {accent}metin{/accent}'
            ),
        }),
        ('Logo & Favicon', {
            'fields': (
                'logo', 'logo_preview', 'logo_url',
                'favicon', 'favicon_preview', 'favicon_url',
            ),
            'description': 'Yüklü dosya varsa o kullanılır; yoksa URL alanı.',
        }),
        ('Adres (NAP)', {
            'fields': (
                'street', 'district', 'city', 'region',
                'postal_code', 'country',
            ),
        }),
        ('Konum & Hizmet', {
            'fields': (
                'latitude', 'longitude', 'opening_hours',
                'price_range', 'area_served',
            ),
        }),
        ('Sosyal Medya', {
            'fields': ('instagram_url', 'facebook_url'),
        }),
        ('Footer', {
            'fields': ('footer_copyright',),
            'description': 'Alt bilgi çubuğundaki telif satırı ({year}, {legal_name} kullanılabilir)',
        }),
        ('Sistem', {
            'fields': ('updated_at',),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        self._request = request
        return super().changeform_view(request, object_id, form_url, extra_context)

    @admin.display(description='Site ayarı çevirileri')
    def translations_admin_link(self, obj):
        if not obj or not obj.pk:
            return '—'
        filtered = translation_list_link(
            obj,
            changelist_name='core_sitesettingstranslation_changelist',
            filter_param='settings__id__exact',
        )
        all_link = all_translations_link(
            changelist_name='core_sitesettingstranslation_changelist',
            label='Tümünü gör',
        )
        return format_html('{} · {}', filtered, all_link)

    @admin.display(description='İletişim kayıtları')
    def contacts_admin_link(self, obj):
        if not obj or not obj.pk:
            return '—'
        list_url = reverse('admin:core_sitecontact_changelist') + f'?settings__id__exact={obj.pk}'
        add_url = reverse('admin:core_sitecontact_add') + f'?settings={obj.pk}'
        return format_html(
            '<a href="{}">Kayıtları yönet</a> · <a href="{}">Yeni iletişim ekle</a>',
            list_url,
            add_url,
        )

    @admin.display(description='Önizleme')
    def logo_preview(self, obj):
        if not obj.pk:
            return 'Kayıt sonrası önizleme görünür.'
        url = obj.get_resolved_logo_url(getattr(self, '_request', None))
        if not url:
            return '—'
        return format_html(
            '<img src="{}" style="max-height:80px;max-width:160px;object-fit:contain;border-radius:8px;" />',
            url,
        )

    @admin.display(description='Favicon önizleme')
    def favicon_preview(self, obj):
        if not obj.pk:
            return 'Kayıt sonrası önizleme görünür.'
        url = obj.get_resolved_favicon_url(getattr(self, '_request', None))
        if not url:
            return '—'
        return format_html(
            '<img src="{}" style="max-height:32px;max-width:32px;object-fit:contain;" />',
            url,
        )


class FAQTranslationInline(admin.TabularInline):
    model = FAQTranslation
    extra = 0
    fields = ('language', 'question', 'answer')


@admin.register(FAQTranslation)
class FAQTranslationAdmin(GroqTranslateAdminMixin, TranslationAdminMixin, admin.ModelAdmin):
    groq_translation_handler = 'faq'
    list_display = ('faq', 'language', 'question')
    search_fields = ('question', 'answer', 'faq__question')
    autocomplete_fields = ('faq', 'language')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active', 'translations_link')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer')
    inlines = [FAQTranslationInline]

    @admin.display(description='Çevirileri')
    def translations_link(self, obj):
        return translation_list_link(
            obj,
            changelist_name='core_faqtranslation_changelist',
            filter_param='faq__id__exact',
        )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'phone', 'message')
    readonly_fields = ('name', 'phone', 'message', 'created_at')
    list_editable = ('is_read',)

    def has_add_permission(self, request):
        return False
