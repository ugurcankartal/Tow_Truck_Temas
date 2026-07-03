from django.core.management.base import BaseCommand

from content.models import ContentZone, SiteImage, SiteImagePlacement
from core.models import FAQ, SiteSettings
from showcase.models import ShowcaseService, ShowcaseServiceSection, ShowcaseStat

DEFAULT_ZONES = [
    {
        'code': ContentZone.CODE_HERO,
        'name': 'Hero (Slider)',
        'description': 'Ana sayfa üst bölüm — kaydırmalı slayt alanı',
    },
    {
        'code': ContentZone.CODE_SCROLL_DRAW,
        'name': 'Scroll Draw (Hizmetler)',
        'description': 'İkinci bölüm — üst üste kayan görsel alanı',
    },
]

DEFAULT_IMAGES = [
  # Hero slaytları
  {
    'zones': [(ContentZone.CODE_HERO, 1)],
    'image_url': 'https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?w=1600&q=80&auto=format',
    'title': 'Profesyonel Oto Çekici',
    'subtitle': 'Aracınızı güvenle taşıyoruz',
    'description': '',
    'alt_text': 'Profesyonel oto çekici aracı yolda',
  },
  {
    'zones': [(ContentZone.CODE_HERO, 2)],
    'image_url': 'https://images.unsplash.com/photo-1601362840469-51e4d8d22962?w=1600&q=80&auto=format',
    'title': '7/24 Yol Yardım',
    'subtitle': 'Gece gündüz yanınızdayız',
    'description': '',
    'alt_text': 'Gece yol yardım hizmeti',
  },
  {
    'zones': [(ContentZone.CODE_HERO, 3)],
    'image_url': 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=1600&q=80&auto=format',
    'title': 'Hızlı Müdahale',
    'subtitle': 'Ortalama 15 dakikada yanınızdayız',
    'description': '',
    'alt_text': 'Hızlı çekici müdahale ekibi',
  },
  {
    'zones': [(ContentZone.CODE_HERO, 4)],
    'image_url': 'https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=1600&q=80&auto=format',
    'title': 'Uzman Ekip & Ekipman',
    'subtitle': 'Her araç tipine uygun çözüm',
    'description': '',
    'alt_text': 'Uzman oto kurtarma ekipmanı',
  },
  # Scroll-draw görselleri
  {
    'zones': [(ContentZone.CODE_SCROLL_DRAW, 1)],
    'image_url': 'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&q=80&auto=format',
    'title': 'Oto Çekici',
    'subtitle': '',
    'description': 'Binek ve ticari araçlar için güvenli taşıma',
    'alt_text': 'Oto çekici hizmeti',
  },
  {
    'zones': [(ContentZone.CODE_SCROLL_DRAW, 2)],
    'image_url': 'https://images.unsplash.com/photo-1625047509248-ec889cbff17f?w=1200&q=80&auto=format',
    'title': 'Yol Yardım',
    'subtitle': '',
    'description': 'Yolda kaldığınız her an profesyonel destek',
    'alt_text': 'Yol yardım hizmeti',
  },
  {
    'zones': [(ContentZone.CODE_SCROLL_DRAW, 3)],
    'image_url': 'https://images.unsplash.com/photo-1487754180451-c456f719a1fc?w=1200&q=80&auto=format',
    'title': 'Akü Takviyesi',
    'subtitle': '',
    'description': 'Anında akü takviye ve kontrol hizmeti',
    'alt_text': 'Akü takviye hizmeti',
  },
  {
    'zones': [(ContentZone.CODE_SCROLL_DRAW, 4)],
    'image_url': 'https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=1200&q=80&auto=format',
    'title': 'Lastik Değişimi',
    'subtitle': '',
    'description': 'Mobil lastik değişim ve tamir desteği',
    'alt_text': 'Lastik değişim hizmeti',
  },
]

DEFAULT_FAQS = [
    {
        'question': "İstanbul Anadolu Yakası'nda ne kadar sürede gelirsiniz?",
        'answer': (
            'Kadıköy, Üsküdar, Ataşehir ve çevre ilçelerde ortalama 15 dakika içinde '
            'ekibimiz yanınızda olur. Trafik yoğunluğuna göre süre değişebilir.'
        ),
        'order': 1,
    },
    {
        'question': 'Gece ve hafta sonu hizmet veriyor musunuz?',
        'answer': (
            'Evet. Çekici Pro olarak 7 gün 24 saat kesintisiz oto çekici ve '
            'yol yardım hizmeti sunuyoruz.'
        ),
        'order': 2,
    },
    {
        'question': 'Fiyatlandırma nasıl yapılıyor?',
        'answer': (
            'Mesafe, araç tipi ve hizmet türüne göre şeffaf fiyatlandırma uyguluyoruz. '
            'Telefonla aradığınızda net fiyat bilgisi verilir.'
        ),
        'order': 3,
    },
    {
        'question': 'Hangi araç tiplerini çekebiliyorsunuz?',
        'answer': (
            'Binek otomobil, SUV, hafif ticari araç ve motosiklet taşıma hizmeti veriyoruz. '
            'Ağır vasıta için ayrı ekipmanımız mevcuttur.'
        ),
        'order': 4,
    },
]


DEFAULT_SHOWCASE_STATS = [
    {'value': '7/24', 'label': 'Kesintisiz Hizmet', 'order': 1},
    {'value': '15 dk', 'label': 'Ortalama Varış', 'order': 2},
    {'value': '5000+', 'label': 'Mutlu Müşteri', 'order': 3},
    {'value': '12+', 'label': 'Yıllık Deneyim', 'order': 4},
]

DEFAULT_SHOWCASE_SERVICE_SECTION = {
    'badge': 'Neden Çekici Pro?',
    'title': 'Kapsamlı Yol Yardım Hizmetleri',
    'description': (
        '<p>{region} bölgesinde oto çekici, acil yol yardım ve mobil tamir '
        'hizmetleri sunuyoruz. Her hizmetimiz lisanslı ekip ve sigortalı taşıma '
        'garantisiyle sunulur.</p>'
    ),
}

DEFAULT_SHOWCASE_SERVICES = [
    {
        'icon': '🚗',
        'title': 'Oto Çekici',
        'description': (
            'Arızalı veya kaza yapmış aracınızı en yakın servise veya istediğiniz '
            'adrese güvenle taşıyoruz.'
        ),
        'order': 1,
    },
    {
        'icon': '🛟',
        'title': 'Acil Yol Yardım',
        'description': (
            'Yolda kaldığınızda 7/24 ulaşabileceğiniz profesyonel yol yardım '
            'ekibimiz hazır.'
        ),
        'order': 2,
    },
    {
        'icon': '🔋',
        'title': 'Akü Takviyesi',
        'description': (
            'Bitmiş akünüz için hızlı takviye ve gerekirse yeni akü montajı yapıyoruz.'
        ),
        'order': 3,
    },
    {
        'icon': '🛞',
        'title': 'Lastik Değişimi',
        'description': (
            'Patlak veya hasarlı lastiğinizi yerinde değiştiriyor, yola devam '
            'etmenizi sağlıyoruz.'
        ),
        'order': 4,
    },
]


DEFAULT_SITE_SETTINGS = {
    'meta_title': 'Çekici Pro | İstanbul Anadolu Yakası 7/24 Oto Çekici & Yol Yardım',
    'meta_description': (
        'İstanbul Anadolu Yakası 7/24 oto çekici ve yol yardım hizmeti. '
        'Kadıköy, Üsküdar, Ataşehir ve çevresinde ortalama 15 dakikada yanınızdayız.'
    ),
    'meta_keywords': (
        'oto çekici, yol yardım, istanbul çekici, anadolu yakası çekici, '
        'kadıköy çekici, 7/24 çekici'
    ),
    'canonical_url': 'https://cekicipro.com/',
    'business_name': 'Çekici Pro',
    'legal_name': 'Çekici Pro Oto Kurtarma Ltd. Şti.',
    'tagline': '7/24 Oto Çekici & Yol Yardım',
    'phone': '+90 555 123 45 67',
    'email': 'info@cekicipro.com',
    'street': 'Atatürk Cad. No: 142',
    'district': 'Kadıköy',
    'city': 'İstanbul',
    'region': 'Anadolu Yakası',
    'postal_code': '34710',
    'latitude': 40.990100,
    'longitude': 29.029200,
    'area_served': [
        'Kadıköy', 'Üsküdar', 'Ataşehir', 'Maltepe', 'Kartal', 'Pendik',
        'İstanbul Anadolu Yakası',
    ],
    'instagram_url': 'https://instagram.com/cekicipro',
    'facebook_url': 'https://facebook.com/cekicipro',
    'site_url': 'https://cekicipro.com',
    'footer_copyright': '© {year} {legal_name}. Tüm hakları saklıdır.',
    'hero_intro_badge': 'Aktif Hizmet',
    'hero_intro_title': (
        '<p>İstanbul Anadolu Yakası 7/24 Oto Çekici &amp; '
        '{accent}Yol Yardım{/accent}</p>'
    ),
    'hero_intro_body': (
        '<p><strong>{business_name}</strong> olarak {region} genelinde '
        '7 gün 24 saat profesyonel oto çekici ve yol yardım hizmeti sunuyoruz. '
        'Deneyimli ekibimiz ve modern ekipmanlarımızla aracınızı en kısa sürede '
        'güvenle taşıyoruz.</p>'
        '<p>Oto kurtarma, akü takviyesi, lastik değişimi ve acil yol yardım '
        'ihtiyaçlarınız için tek numara — hızlı, şeffaf fiyatlandırma ve müşteri '
        'memnuniyeti odaklı hizmet.</p>'
    ),
}


def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, dict, tuple, set)) and len(value) == 0:
        return True
    return False


def fill_empty_fields(instance, defaults: dict) -> list[str]:
    """Yalnızca boş alanları varsayılan değerlerle doldurur."""
    filled = []
    for field, default_value in defaults.items():
        if _is_empty(getattr(instance, field)):
            setattr(instance, field, default_value)
            filled.append(field)
    return filled


class Command(BaseCommand):
    help = 'Eksik site ayarları, bölgeler, görseller ve SSS verilerini doldurur (mevcut veriyi ezmez)'

    def handle(self, *args, **options):
        settings = SiteSettings.load()
        filled_settings = fill_empty_fields(settings, DEFAULT_SITE_SETTINGS)
        if filled_settings:
            settings.save(update_fields=filled_settings + ['updated_at'])
            self.stdout.write(
                self.style.SUCCESS(
                    f'Site ayarları güncellendi ({len(filled_settings)} boş alan dolduruldu)'
                )
            )
        else:
            self.stdout.write('Site ayarları zaten dolu, atlandı')

        zones_created = 0
        for zone_data in DEFAULT_ZONES:
            _, created = ContentZone.objects.get_or_create(
                code=zone_data['code'],
                defaults=zone_data,
            )
            if created:
                zones_created += 1
        if zones_created:
            self.stdout.write(self.style.SUCCESS(f'{zones_created} içerik bölgesi eklendi'))
        else:
            self.stdout.write('İçerik bölgeleri zaten mevcut, atlandı')

        if not SiteImage.objects.exists():
            for item in DEFAULT_IMAGES:
                data = {**item}
                zones = data.pop('zones')
                image = SiteImage.objects.create(**data)
                for zone_code, order in zones:
                    zone = ContentZone.objects.get(code=zone_code)
                    SiteImagePlacement.objects.create(
                        site_image=image,
                        zone=zone,
                        order=order,
                    )
            self.stdout.write(self.style.SUCCESS(f'{len(DEFAULT_IMAGES)} site görseli eklendi'))
        else:
            self.stdout.write('Site görselleri zaten mevcut, atlandı')

        if not FAQ.objects.exists():
            FAQ.objects.bulk_create([FAQ(**faq) for faq in DEFAULT_FAQS])
            self.stdout.write(self.style.SUCCESS(f'{len(DEFAULT_FAQS)} SSS eklendi'))
        else:
            self.stdout.write('SSS zaten mevcut, atlandı')

        if not ShowcaseStat.objects.exists():
            ShowcaseStat.objects.bulk_create(
                [ShowcaseStat(**item) for item in DEFAULT_SHOWCASE_STATS]
            )
            self.stdout.write(
                self.style.SUCCESS(f'{len(DEFAULT_SHOWCASE_STATS)} vitrin istatistiği eklendi')
            )
        else:
            self.stdout.write('Vitrin istatistikleri zaten mevcut, atlandı')

        section = ShowcaseServiceSection.load()
        filled_section = fill_empty_fields(section, DEFAULT_SHOWCASE_SERVICE_SECTION)
        if filled_section:
            section.save(update_fields=filled_section)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Hizmetler bölümü güncellendi ({len(filled_section)} boş alan dolduruldu)'
                )
            )
        else:
            self.stdout.write('Hizmetler bölümü zaten dolu, atlandı')

        if not ShowcaseService.objects.exists():
            ShowcaseService.objects.bulk_create(
                [ShowcaseService(**item) for item in DEFAULT_SHOWCASE_SERVICES]
            )
            self.stdout.write(
                self.style.SUCCESS(f'{len(DEFAULT_SHOWCASE_SERVICES)} hizmet kartı eklendi')
            )
        else:
            self.stdout.write('Hizmet kartları zaten mevcut, atlandı')

        self.stdout.write(self.style.SUCCESS('Seed tamamlandı'))
