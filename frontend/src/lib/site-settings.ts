import { getBuildApiUrl, getPublicApiUrl, getPublicSiteUrl } from '@/lib/env';
import { business as fallbackBusiness, faqs as fallbackFaqs, scrollImages as fallbackScrollImages, slides as fallbackSlides, stats as fallbackStats, services as fallbackServices } from '@/data/business';
import type { Locale } from '@/i18n';

const CLIENT_API_URL = getPublicApiUrl();

export interface SiteSeo {
  title: string;
  description: string;
  keywords: string;
  canonical_url: string;
  og_image_url: string;
  favicon_url: string;
  robots: string;
  site_url: string;
}

export interface SiteContact {
  id: number;
  label: string;
  value: string;
  href: string;
  contact_type: string;
  is_primary: boolean;
  order: number;
}

export interface SiteBusiness {
  name: string;
  legal_name: string;
  tagline: string;
  contacts: SiteContact[];
  phone: string;
  phone_href: string;
  email: string;
  address: {
    street: string;
    district: string;
    city: string;
    region: string;
    postal_code: string;
    country: string;
  };
  coordinates: {
    latitude: number;
    longitude: number;
  };
  opening_hours: string;
  price_range: string;
  area_served: string[];
  social: {
    instagram: string;
    facebook: string;
  };
  footer_copyright: string;
  logo_url: string;
}

export interface SiteFaq {
  id: number;
  question: string;
  answer: string;
  order: number;
}

export interface HeroSlide {
  id: number;
  image: string;
  title: string;
  subtitle: string;
  alt: string;
  order: number;
}

export interface HeroIntro {
  badge: string;
  title_html: string;
  body_html: string;
}

export interface ShowcaseStat {
  id: number;
  value: string;
  label: string;
  order: number;
}

export interface ShowcaseServiceItem {
  id: number;
  icon: string;
  title: string;
  description: string;
  order: number;
}

export interface ShowcaseServices {
  badge: string;
  title: string;
  description_html: string;
  items: ShowcaseServiceItem[];
}

export interface ScrollDrawImage {
  id: number;
  src: string;
  title: string;
  desc: string;
  alt: string;
  order: number;
}

export interface SiteSettingsResponse {
  seo: SiteSeo;
  business: SiteBusiness;
  faqs: SiteFaq[];
  hero_slides: HeroSlide[];
  scroll_draw_images: ScrollDrawImage[];
  hero_intro: HeroIntro;
  showcase_stats: ShowcaseStat[];
  showcase_services: ShowcaseServices;
  json_ld: Record<string, unknown>;
  updated_at: string;
  language?: string;
}

/** Bileşenlerde kullanılan camelCase iletişim tipi */
export interface ContactView {
  id: number;
  label: string;
  value: string;
  href: string;
  contactType: string;
  isPrimary: boolean;
  order: number;
}

/** Bileşenlerde kullanılan camelCase işletme tipi */
export interface BusinessView {
  name: string;
  legalName: string;
  tagline: string;
  contacts: ContactView[];
  phone: string;
  phoneHref: string;
  email: string;
  address: {
    street: string;
    district: string;
    city: string;
    region: string;
    postalCode: string;
    country: string;
  };
  coordinates: {
    latitude: number;
    longitude: number;
  };
  openingHours: string;
  priceRange: string;
  areaServed: readonly string[];
  social: {
    instagram: string;
    facebook: string;
  };
  footerCopyright: string;
  logoUrl: string;
}

export function getFaviconMimeType(url: string): string {
  const path = url.split('?')[0].toLowerCase();
  if (path.endsWith('.svg')) return 'image/svg+xml';
  if (path.endsWith('.ico')) return 'image/x-icon';
  if (path.endsWith('.jpg') || path.endsWith('.jpeg')) return 'image/jpeg';
  if (path.endsWith('.webp')) return 'image/webp';
  return 'image/png';
}

export function renderFooterCopyright(template: string, legalName: string): string {
  return template
    .replaceAll('{year}', String(new Date().getFullYear()))
    .replaceAll('{legal_name}', legalName);
}

function buildFallbackJsonLd(): Record<string, unknown> {
  const b = fallbackBusiness;
  const siteId = getPublicSiteUrl();
  const primary = b.contacts.find((c) => c.isPrimary) ?? b.contacts[0];

  return {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'LocalBusiness',
        '@id': `${siteId}/#business`,
        name: b.name,
        telephone: primary?.value ?? b.phone,
        email: b.email,
        url: siteId,
      },
      {
        '@type': 'FAQPage',
        '@id': `${siteId}/#faq`,
        mainEntity: fallbackFaqs.map((faq) => ({
          '@type': 'Question',
          name: faq.question,
          acceptedAnswer: { '@type': 'Answer', text: faq.answer },
        })),
      },
    ],
  };
}

function getFallbackSettings(locale: Locale = 'tr'): SiteSettingsResponse {
  const b = fallbackBusiness;
  const siteUrl = getPublicSiteUrl();

  return {
    seo: {
      title: 'Çekici Pro | İstanbul Anadolu Yakası 7/24 Oto Çekici & Yol Yardım',
      description:
        'İstanbul Anadolu Yakası 7/24 oto çekici ve yol yardım hizmeti. Kadıköy, Üsküdar, Ataşehir ve çevresinde ortalama 15 dakikada yanınızdayız.',
      keywords: 'oto çekici, yol yardım, istanbul çekici',
      canonical_url: `${siteUrl}/`,
      og_image_url: '',
      favicon_url: '',
      robots: 'index, follow',
      site_url: siteUrl,
    },
    business: {
      name: b.name,
      legal_name: b.legalName,
      tagline: b.tagline,
      contacts: b.contacts.map((c) => ({
        id: c.id,
        label: c.label,
        value: c.value,
        href: c.href,
        contact_type: c.contactType,
        is_primary: c.isPrimary,
        order: c.order,
      })),
      phone: b.phone,
      phone_href: b.phoneHref,
      email: b.email,
      address: {
        street: b.address.street,
        district: b.address.district,
        city: b.address.city,
        region: b.address.region,
        postal_code: b.address.postalCode,
        country: b.address.country,
      },
      coordinates: {
        latitude: b.coordinates.latitude,
        longitude: b.coordinates.longitude,
      },
      opening_hours: b.openingHours,
      price_range: b.priceRange,
      area_served: [...b.areaServed],
      social: { ...b.social },
      footer_copyright: '© {year} {legal_name}. Tüm hakları saklıdır.',
      logo_url: '',
    },
    faqs: fallbackFaqs.map((faq, i) => ({
      id: i + 1,
      question: faq.question,
      answer: faq.answer,
      order: i + 1,
    })),
    hero_slides: fallbackSlides.map((slide, i) => ({
      id: i + 1,
      image: slide.image,
      title: slide.title,
      subtitle: slide.subtitle,
      alt: slide.alt,
      order: i + 1,
    })),
    scroll_draw_images: fallbackScrollImages.map((item, i) => ({
      id: i + 1,
      src: item.src,
      title: item.title,
      desc: item.desc,
      alt: item.alt,
      order: i + 1,
    })),
    hero_intro: {
      badge: 'Aktif Hizmet',
      title_html:
        'İstanbul Anadolu Yakası 7/24 Oto Çekici &amp; <span class="bg-gradient-to-r from-amber-500 to-amber-600 bg-clip-text text-transparent">Yol Yardım</span>',
      body_html: `<p><strong>${b.name}</strong> olarak ${b.address.region} genelinde 7 gün 24 saat profesyonel oto çekici ve yol yardım hizmeti sunuyoruz. Deneyimli ekibimiz ve modern ekipmanlarımızla aracınızı en kısa sürede güvenle taşıyoruz.</p><p>Oto kurtarma, akü takviyesi, lastik değişimi ve acil yol yardım ihtiyaçlarınız için tek numara — hızlı, şeffaf fiyatlandırma ve müşteri memnuniyeti odaklı hizmet.</p>`,
    },
    showcase_stats: fallbackStats.map((stat, i) => ({
      id: i + 1,
      value: stat.value,
      label: stat.label,
      order: i + 1,
    })),
    showcase_services: {
      badge: 'Neden Çekici Pro?',
      title: 'Kapsamlı Yol Yardım Hizmetleri',
      description_html: `<p>${b.address.region} bölgesinde oto çekici, acil yol yardım ve mobil tamir hizmetleri sunuyoruz. Her hizmetimiz lisanslı ekip ve sigortalı taşıma garantisiyle sunulur.</p>`,
      items: fallbackServices.map((service, i) => ({
        id: i + 1,
        icon: service.icon,
        title: service.title,
        description: service.description,
        order: i + 1,
      })),
    },
    json_ld: buildFallbackJsonLd(),
    updated_at: new Date().toISOString(),
    language: locale,
  };
}

export function mapContact(api: SiteContact): ContactView {
  return {
    id: api.id,
    label: api.label,
    value: api.value,
    href: api.href,
    contactType: api.contact_type,
    isPrimary: api.is_primary,
    order: api.order,
  };
}

function buildPhoneHref(phone: string, phoneHref: string): string {
  if (phoneHref) return phoneHref;
  const digits = phone.replace(/\D/g, '');
  return digits ? `tel:+${digits}` : '';
}

/** API contacts boş ama phone alanları doluysa (eski build / geçiş dönemi). */
function fallbackContactsFromPhone(api: SiteBusiness): ContactView[] {
  const phone = (api.phone ?? '').trim();
  if (!phone) return [];
  return [
    {
      id: 0,
      label: 'Telefon',
      value: phone,
      href: buildPhoneHref(phone, api.phone_href ?? ''),
      contactType: 'phone',
      isPrimary: true,
      order: 0,
    },
  ];
}

function pickPrimaryContact(contacts: ContactView[]): ContactView | undefined {
  return (
    contacts.find((c) => c.isPrimary) ??
    contacts.find((c) => c.contactType === 'phone') ??
    contacts[0]
  );
}

export function getPrimaryContact(business: BusinessView): ContactView | undefined {
  return pickPrimaryContact(business.contacts);
}

export function mapBusiness(api: SiteBusiness): BusinessView {
  const mapped = (api.contacts ?? []).map(mapContact);
  const contacts = mapped.length > 0 ? mapped : fallbackContactsFromPhone(api);
  const primary = pickPrimaryContact(contacts);
  return {
    name: api.name,
    legalName: api.legal_name,
    tagline: api.tagline,
    contacts,
    phone: primary?.value ?? api.phone ?? '',
    phoneHref: primary?.href ?? api.phone_href ?? '',
    email: api.email,
    address: {
      street: api.address.street,
      district: api.address.district,
      city: api.address.city,
      region: api.address.region,
      postalCode: api.address.postal_code,
      country: api.address.country,
    },
    coordinates: api.coordinates,
    openingHours: api.opening_hours,
    priceRange: api.price_range,
    areaServed: api.area_served,
    social: api.social,
    footerCopyright: api.footer_copyright,
    logoUrl: api.logo_url,
  };
}

export const API_V1_PREFIX = '/api/v1';

export function getApiBaseUrl(): string {
  return CLIENT_API_URL.replace(/\/$/, '');
}

/** `site-settings/` gibi yol parçası alır; tam API URL döner. */
export function apiUrl(path: string): string {
  const segment = path.replace(/^\/+/, '');
  return `${getApiBaseUrl()}${API_V1_PREFIX}/${segment}`;
}

/**
 * Django REST API'den site ayarlarını çeker.
 * Dev / SSR: her istekte güncel veri (cache yok).
 * Static build: build anındaki veri gömülür.
 */
export async function getSiteSettings(locale: Locale = 'tr'): Promise<SiteSettingsResponse> {
  const noCache = import.meta.env.DEV || import.meta.env.SSR;
  const buildBase = getBuildApiUrl();
  const settingsUrl = `${buildBase}${API_V1_PREFIX}/site-settings/?lang=${locale}`;
  try {
    const res = await fetch(settingsUrl, {
      headers: { Accept: 'application/json' },
      cache: noCache ? 'no-store' : 'default',
    });

    if (!res.ok) {
      throw new Error(`API ${res.status}`);
    }

    return (await res.json()) as SiteSettingsResponse;
  } catch (error) {
    console.warn('[site-settings] API erişilemedi, fallback kullanılıyor:', error);
    return getFallbackSettings(locale);
  }
}
