export type Locale = string;

export interface LanguageInfo {
  id: number;
  code: string;
  name_native: string;
  flag_url: string | null;
  is_active: boolean;
  is_default: boolean;
  sort_order: number;
}

export interface UiMessages {
  nav: {
    home: string;
    services: string;
    faq: string;
    contact: string;
    aria: string;
    menuOpen: string;
    menuClose: string;
    callNow: string;
  };
  hero: {
    aria: string;
    slideSelect: string;
    slideN: string;
    callNow: string;
  };
  scrollDraw: {
    aria: string;
  };
  services: {
    sectionAria: string;
    faqBadge: string;
    faqTitle: string;
    contactBadge: string;
    contactTitle: string;
    phone: string;
    email: string;
    hours: string;
    address: string;
    phoneHint: string;
    name: string;
    namePlaceholder: string;
    phonePlaceholder: string;
    message: string;
    messagePlaceholder: string;
    submit: string;
    sending: string;
    success: string;
    error: string;
    errorFallback: string;
  };
  footer: {
    blurb: string;
    areasTitle: string;
    contactTitle: string;
    phone: string;
    email: string;
    address: string;
    hours: string;
    ctaTitle: string;
    ctaSubtitle: string;
  };
}

/** Yerel fallback — API erişilemezse kullanılır */
export const tr: UiMessages = {
  nav: {
    home: 'Ana Sayfa',
    services: 'Hizmetler',
    faq: 'SSS',
    contact: 'İletişim',
    aria: 'Ana navigasyon',
    menuOpen: 'Menüyü aç',
    menuClose: 'Menüyü kapat',
    callNow: 'Hemen Ara',
  },
  hero: {
    aria: 'Ana tanıtım',
    slideSelect: 'Slayt seçimi',
    slideN: 'Slayt',
    callNow: 'Hemen Arayın',
  },
  scrollDraw: {
    aria: 'Hizmetler görsel sunum',
  },
  services: {
    sectionAria: 'Hizmetler, SSS ve iletişim',
    faqBadge: 'Sık Sorulan Sorular',
    faqTitle: 'Merak Edilenler',
    contactBadge: 'Bize Ulaşın',
    contactTitle: 'İletişim Bilgileri',
    phone: 'Telefon',
    email: 'E-posta',
    hours: 'Çalışma Saatleri',
    address: 'Adres',
    phoneHint: '7/24 acil hat — bekletmeden yanıt',
    name: 'Ad Soyad',
    namePlaceholder: 'Adınız Soyadınız',
    phonePlaceholder: '05XX XXX XX XX',
    message: 'Mesajınız',
    messagePlaceholder: 'Konum ve araç bilgilerinizi yazın...',
    submit: 'Mesaj Gönder',
    sending: 'Gönderiliyor...',
    success: 'Mesajınız alındı. En kısa sürede dönüş yapacağız.',
    error: 'Form gönderilemedi',
    errorFallback: 'Şu an gönderilemedi. Lütfen doğrudan arayın:',
  },
  footer: {
    blurb: 'Güvenilir oto çekici ve yol yardım hizmeti. 7/24 hizmetinizdeyiz.',
    areasTitle: 'Hizmet Bölgeleri',
    contactTitle: 'İletişim',
    phone: 'Telefon',
    email: 'E-posta',
    address: 'Adres',
    hours: 'Çalışma Saatleri',
    ctaTitle: 'Acil çekici mi lazım?',
    ctaSubtitle: 'Hemen arayın, ekibimiz yola çıksın.',
  },
};

export const en: UiMessages = {
  nav: {
    home: 'Home',
    services: 'Services',
    faq: 'FAQ',
    contact: 'Contact',
    aria: 'Main navigation',
    menuOpen: 'Open menu',
    menuClose: 'Close menu',
    callNow: 'Call Now',
  },
  hero: {
    aria: 'Hero section',
    slideSelect: 'Slide selection',
    slideN: 'Slide',
    callNow: 'Call Now',
  },
  scrollDraw: {
    aria: 'Services visual showcase',
  },
  services: {
    sectionAria: 'Services, FAQ and contact',
    faqBadge: 'Frequently Asked Questions',
    faqTitle: 'Common Questions',
    contactBadge: 'Get in Touch',
    contactTitle: 'Contact Information',
    phone: 'Phone',
    email: 'Email',
    hours: 'Opening Hours',
    address: 'Address',
    phoneHint: '24/7 emergency line — no waiting',
    name: 'Full Name',
    namePlaceholder: 'Your full name',
    phonePlaceholder: '+90 5XX XXX XX XX',
    message: 'Your Message',
    messagePlaceholder: 'Location and vehicle details...',
    submit: 'Send Message',
    sending: 'Sending...',
    success: 'Your message has been received. We will get back to you shortly.',
    error: 'Could not send the form',
    errorFallback: 'Could not send right now. Please call directly:',
  },
  footer: {
    blurb: 'Reliable tow truck and roadside assistance. Available 24/7.',
    areasTitle: 'Service Areas',
    contactTitle: 'Contact',
    phone: 'Phone',
    email: 'Email',
    address: 'Address',
    hours: 'Opening Hours',
    ctaTitle: 'Need emergency towing?',
    ctaSubtitle: 'Call now and our team will be on the way.',
  },
};

const dictionaries: Record<string, UiMessages> = { tr, en };

export function getUi(locale: Locale): UiMessages {
  return dictionaries[locale] ?? dictionaries.tr ?? tr;
}

/** API bundle (düz anahtar) → UiMessages */
export function bundleToUi(strings: Record<string, string>, fallback: UiMessages = tr): UiMessages {
  const pick = (key: string, fb: string) => strings[key] ?? fb;
  return {
    nav: {
      home: pick('nav.home', fallback.nav.home),
      services: pick('nav.services', fallback.nav.services),
      faq: pick('nav.faq', fallback.nav.faq),
      contact: pick('nav.contact', fallback.nav.contact),
      aria: pick('nav.aria', fallback.nav.aria),
      menuOpen: pick('nav.menu_open', fallback.nav.menuOpen),
      menuClose: pick('nav.menu_close', fallback.nav.menuClose),
      callNow: pick('nav.call_now', fallback.nav.callNow),
    },
    hero: {
      aria: pick('hero.aria', fallback.hero.aria),
      slideSelect: pick('hero.slide_select', fallback.hero.slideSelect),
      slideN: pick('hero.slide_n', fallback.hero.slideN),
      callNow: pick('hero.call_now', fallback.hero.callNow),
    },
    scrollDraw: {
      aria: pick('scroll_draw.aria', fallback.scrollDraw.aria),
    },
    services: {
      sectionAria: pick('services.section_aria', fallback.services.sectionAria),
      faqBadge: pick('services.faq_badge', fallback.services.faqBadge),
      faqTitle: pick('services.faq_title', fallback.services.faqTitle),
      contactBadge: pick('services.contact_badge', fallback.services.contactBadge),
      contactTitle: pick('services.contact_title', fallback.services.contactTitle),
      phone: pick('services.phone', fallback.services.phone),
      email: pick('services.email', fallback.services.email),
      hours: pick('services.hours', fallback.services.hours),
      address: pick('services.address', fallback.services.address),
      phoneHint: pick('services.phone_hint', fallback.services.phoneHint),
      name: pick('services.name', fallback.services.name),
      namePlaceholder: pick('services.name_placeholder', fallback.services.namePlaceholder),
      phonePlaceholder: pick('services.phone_placeholder', fallback.services.phonePlaceholder),
      message: pick('services.message', fallback.services.message),
      messagePlaceholder: pick('services.message_placeholder', fallback.services.messagePlaceholder),
      submit: pick('services.submit', fallback.services.submit),
      sending: pick('services.sending', fallback.services.sending),
      success: pick('services.success', fallback.services.success),
      error: pick('services.error', fallback.services.error),
      errorFallback: pick('services.error_fallback', fallback.services.errorFallback),
    },
    footer: {
      blurb: pick('footer.blurb', fallback.footer.blurb),
      areasTitle: pick('footer.areas_title', fallback.footer.areasTitle),
      contactTitle: pick('footer.contact_title', fallback.footer.contactTitle),
      phone: pick('footer.phone', fallback.footer.phone),
      email: pick('footer.email', fallback.footer.email),
      address: pick('footer.address', fallback.footer.address),
      hours: pick('footer.hours', fallback.footer.hours),
      ctaTitle: pick('footer.cta_title', fallback.footer.ctaTitle),
      ctaSubtitle: pick('footer.cta_subtitle', fallback.footer.ctaSubtitle),
    },
  };
}

export function getNavLinks(ui: UiMessages) {
  return [
    { href: '#hero', label: ui.nav.home },
    { href: '#hizmetler', label: ui.nav.services },
    { href: '#sss', label: ui.nav.faq },
    { href: '#iletisim', label: ui.nav.contact },
  ];
}

export function localePath(locale: Locale, defaultLocale: Locale, path = '/'): string {
  if (locale === defaultLocale) return path;
  const normalized = path === '/' ? '' : path;
  return `/${locale}${normalized}`;
}

export const ogLocales: Record<string, string> = {
  tr: 'tr_TR',
  en: 'en_US',
};

export function ogLocaleFor(code: Locale): string {
  return ogLocales[code] ?? code.replace('-', '_');
}
