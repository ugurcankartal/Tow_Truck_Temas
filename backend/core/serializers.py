import re

from rest_framework import serializers

from content.models import ContentZone, SiteImage, SiteImagePlacement
from showcase.models import ShowcaseService, ShowcaseServiceSection, ShowcaseStat

from .hero_content import hero_body_html, hero_title_html
from .i18n import localized_text
from .models import ContactMessage, FAQ, SiteSettings
from .translation_utils import localized_field


class FAQSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()

    class Meta:
        model = FAQ
        fields = ('id', 'question', 'answer', 'order')

    def _lang(self):
        return self.context.get('language_code')

    def get_question(self, obj):
        return localized_field(obj, 'question', self._lang())

    def get_answer(self, obj):
        return localized_field(obj, 'answer', self._lang())


class ShowcaseStatSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    class Meta:
        model = ShowcaseStat
        fields = ('id', 'value', 'label', 'order')

    def _lang(self):
        return self.context.get('language_code')

    def get_value(self, obj):
        return localized_field(obj, 'value', self._lang())

    def get_label(self, obj):
        return localized_field(obj, 'label', self._lang())


class ShowcaseServiceSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = ShowcaseService
        fields = ('id', 'icon', 'title', 'description', 'order')

    def _lang(self):
        return self.context.get('language_code')

    def get_title(self, obj):
        return localized_field(obj, 'title', self._lang())

    def get_description(self, obj):
        return localized_field(obj, 'description', self._lang())


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ('name', 'phone', 'message')

    def validate_phone(self, value):
        digits = re.sub(r'\D', '', value)
        if len(digits) < 10:
            lang = self.context.get('language_code', 'tr')
            raise serializers.ValidationError(
                localized_text('phone_invalid', lang),
            )
        return value.strip()


def _placements_queryset(zone_code: str):
    return SiteImagePlacement.objects.filter(
        zone__code=zone_code,
        is_active=True,
        site_image__is_active=True,
    ).select_related('site_image', 'zone').prefetch_related(
        'site_image__translations__language',
    )


def _serialize_hero_placement(placement: SiteImagePlacement, request=None, language_code=None) -> dict:
    image = placement.site_image
    return {
        'id': placement.id,
        'image': image.get_resolved_url(request),
        'title': localized_field(image, 'title', language_code),
        'subtitle': localized_field(image, 'subtitle', language_code),
        'alt': localized_field(image, 'alt_text', language_code),
        'order': placement.order,
    }


def _serialize_scroll_placement(placement: SiteImagePlacement, request=None, language_code=None) -> dict:
    image = placement.site_image
    desc = localized_field(image, 'description', language_code)
    subtitle = localized_field(image, 'subtitle', language_code)
    return {
        'id': placement.id,
        'src': image.get_resolved_url(request),
        'title': localized_field(image, 'title', language_code),
        'desc': desc or subtitle,
        'alt': localized_field(image, 'alt_text', language_code),
        'order': placement.order,
    }


class SiteSettingsSerializer(serializers.ModelSerializer):
    seo = serializers.SerializerMethodField()
    business = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    hero_slides = serializers.SerializerMethodField()
    scroll_draw_images = serializers.SerializerMethodField()
    hero_intro = serializers.SerializerMethodField()
    showcase_stats = serializers.SerializerMethodField()
    showcase_services = serializers.SerializerMethodField()
    json_ld = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = (
            'seo', 'business', 'faqs', 'hero_slides',
            'scroll_draw_images', 'hero_intro', 'showcase_stats',
            'showcase_services', 'json_ld', 'updated_at',
        )

    def _lang(self):
        return self.context.get('language_code')

    def _settings_text(self, obj, field):
        return localized_field(obj, field, self._lang())

    def get_seo(self, obj):
        request = self.context.get('request')
        return {
            'title': self._settings_text(obj, 'meta_title'),
            'description': self._settings_text(obj, 'meta_description'),
            'keywords': self._settings_text(obj, 'meta_keywords'),
            'canonical_url': obj.canonical_url,
            'og_image_url': obj.og_image_url,
            'favicon_url': obj.get_resolved_favicon_url(request),
            'robots': obj.robots,
            'site_url': obj.site_url,
        }

    def get_business(self, obj):
        request = self.context.get('request')
        phone_digits = re.sub(r'\D', '', obj.phone)
        trans = obj.get_translation(self._lang())
        area_served = (
            trans.area_served if trans and trans.area_served
            else obj.area_served or []
        )
        return {
            'name': self._settings_text(obj, 'business_name'),
            'legal_name': self._settings_text(obj, 'legal_name'),
            'tagline': self._settings_text(obj, 'tagline'),
            'logo_url': obj.get_resolved_logo_url(request),
            'phone': obj.phone,
            'phone_href': f'tel:+{phone_digits}' if phone_digits else '',
            'email': obj.email,
            'address': {
                'street': self._settings_text(obj, 'street'),
                'district': self._settings_text(obj, 'district'),
                'city': self._settings_text(obj, 'city'),
                'region': self._settings_text(obj, 'region'),
                'postal_code': obj.postal_code,
                'country': obj.country,
            },
            'coordinates': {
                'latitude': float(obj.latitude),
                'longitude': float(obj.longitude),
            },
            'opening_hours': obj.opening_hours,
            'price_range': obj.price_range,
            'area_served': area_served,
            'social': {
                'instagram': obj.instagram_url,
                'facebook': obj.facebook_url,
            },
            'footer_copyright': self._settings_text(obj, 'footer_copyright'),
        }

    def get_faqs(self, obj):
        qs = FAQ.objects.filter(is_active=True).prefetch_related('translations__language')
        return FAQSerializer(qs, many=True, context=self.context).data

    def get_hero_slides(self, obj):
        request = self.context.get('request')
        lang = self._lang()
        placements = _placements_queryset(ContentZone.CODE_HERO)
        return [_serialize_hero_placement(p, request, lang) for p in placements]

    def get_scroll_draw_images(self, obj):
        request = self.context.get('request')
        lang = self._lang()
        placements = _placements_queryset(ContentZone.CODE_SCROLL_DRAW)
        return [_serialize_scroll_placement(p, request, lang) for p in placements]

    def get_hero_intro(self, obj):
        lang = self._lang()
        business_name = self._settings_text(obj, 'business_name')
        region = self._settings_text(obj, 'region')
        badge = self._settings_text(obj, 'hero_intro_badge') or localized_text('hero_badge_default', lang)
        title_raw = self._settings_text(obj, 'hero_intro_title')
        body_raw = self._settings_text(obj, 'hero_intro_body')
        return {
            'badge': badge,
            'title_html': hero_title_html(title_raw, business_name=business_name, region=region),
            'body_html': hero_body_html(body_raw, business_name=business_name, region=region),
        }

    def get_showcase_stats(self, obj):
        qs = ShowcaseStat.objects.filter(is_active=True).prefetch_related('translations__language')
        return ShowcaseStatSerializer(qs, many=True, context=self.context).data

    def get_showcase_services(self, obj):
        section = ShowcaseServiceSection.load()
        items = ShowcaseService.objects.filter(is_active=True).prefetch_related('translations__language')
        business_name = self._settings_text(obj, 'business_name')
        region = self._settings_text(obj, 'region')
        section_desc = localized_field(section, 'description', self._lang())
        return {
            'badge': localized_field(section, 'badge', self._lang()),
            'title': localized_field(section, 'title', self._lang()),
            'description_html': hero_body_html(
                section_desc,
                business_name=business_name,
                region=region,
            ),
            'items': ShowcaseServiceSerializer(items, many=True, context=self.context).data,
        }

    def get_json_ld(self, obj):
        faqs = FAQ.objects.filter(is_active=True).prefetch_related('translations__language')
        lang = self._lang()
        site_id = obj.site_url.rstrip('/')
        faq_data = FAQSerializer(faqs, many=True, context={'language_code': lang}).data

        return {
            '@context': 'https://schema.org',
            '@graph': [
                {
                    '@type': 'LocalBusiness',
                    '@id': f'{site_id}/#business',
                    'name': self._settings_text(obj, 'business_name'),
                    'legalName': self._settings_text(obj, 'legal_name'),
                    'description': self._settings_text(obj, 'meta_description'),
                    'url': obj.site_url,
                    'telephone': obj.phone,
                    'email': obj.email,
                    'image': obj.og_image_url or f'{site_id}/og-image.jpg',
                    'priceRange': obj.price_range,
                    'address': {
                        '@type': 'PostalAddress',
                        'streetAddress': self._settings_text(obj, 'street'),
                        'addressLocality': self._settings_text(obj, 'district'),
                        'addressRegion': self._settings_text(obj, 'city'),
                        'postalCode': obj.postal_code,
                        'addressCountry': obj.country,
                    },
                    'geo': {
                        '@type': 'GeoCoordinates',
                        'latitude': float(obj.latitude),
                        'longitude': float(obj.longitude),
                    },
                    'areaServed': [
                        {'@type': 'City', 'name': area}
                        for area in (
                            (obj.get_translation(lang).area_served if obj.get_translation(lang) else None)
                            or obj.area_served or []
                        )
                    ],
                    'sameAs': [
                        url for url in (obj.instagram_url, obj.facebook_url) if url
                    ],
                },
                {
                    '@type': 'FAQPage',
                    '@id': f'{site_id}/#faq',
                    'mainEntity': [
                        {
                            '@type': 'Question',
                            'name': faq['question'],
                            'acceptedAnswer': {
                                '@type': 'Answer',
                                'text': faq['answer'],
                            },
                        }
                        for faq in faq_data
                    ],
                },
            ],
        }
