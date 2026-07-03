export const business = {
  name: 'Çekici Pro',
  legalName: 'Çekici Pro Oto Kurtarma Ltd. Şti.',
  tagline: '7/24 Oto Çekici & Yol Yardım',
  phone: '+90 555 123 45 67',
  phoneHref: 'tel:+905551234567',
  email: 'info@cekicipro.com',
  address: {
    street: 'Atatürk Cad. No: 142',
    district: 'Kadıköy',
    city: 'İstanbul',
    region: 'Anadolu Yakası',
    postalCode: '34710',
    country: 'TR',
  },
  coordinates: {
    latitude: 40.9901,
    longitude: 29.0292,
  },
  openingHours: 'Mo-Su 00:00-23:59',
  priceRange: '₺₺',
  areaServed: [
    'Kadıköy',
    'Üsküdar',
    'Ataşehir',
    'Maltepe',
    'Kartal',
    'Pendik',
    'İstanbul Anadolu Yakası',
  ],
  social: {
    instagram: 'https://instagram.com/cekicipro',
    facebook: 'https://facebook.com/cekicipro',
  },
} as const;

export const slides = [
  {
    image: 'https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?w=1600&q=80&auto=format',
    title: 'Profesyonel Oto Çekici',
    subtitle: 'Aracınızı güvenle taşıyoruz',
    alt: 'Profesyonel oto çekici aracı yolda',
  },
  {
    image: 'https://images.unsplash.com/photo-1601362840469-51e4d8d22962?w=1600&q=80&auto=format',
    title: '7/24 Yol Yardım',
    subtitle: 'Gece gündüz yanınızdayız',
    alt: 'Gece yol yardım hizmeti',
  },
  {
    image: 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=1600&q=80&auto=format',
    title: 'Hızlı Müdahale',
    subtitle: 'Ortalama 15 dakikada yanınızdayız',
    alt: 'Hızlı çekici müdahale ekibi',
  },
  {
    image: 'https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=1600&q=80&auto=format',
    title: 'Uzman Ekip & Ekipman',
    subtitle: 'Her araç tipine uygun çözüm',
    alt: 'Uzman oto kurtarma ekipmanı',
  },
] as const;

export const scrollImages = [
  {
    src: 'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&q=80&auto=format',
    title: 'Oto Çekici',
    desc: 'Binek ve ticari araçlar için güvenli taşıma',
    alt: 'Oto çekici hizmeti',
  },
  {
    src: 'https://images.unsplash.com/photo-1625047509248-ec889cbff17f?w=1200&q=80&auto=format',
    title: 'Yol Yardım',
    desc: 'Yolda kaldığınız her an profesyonel destek',
    alt: 'Yol yardım hizmeti',
  },
  {
    src: 'https://images.unsplash.com/photo-1487754180451-c456f719a1fc?w=1200&q=80&auto=format',
    title: 'Akü Takviyesi',
    desc: 'Anında akü takviye ve kontrol hizmeti',
    alt: 'Akü takviye hizmeti',
  },
  {
    src: 'https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=1200&q=80&auto=format',
    title: 'Lastik Değişimi',
    desc: 'Mobil lastik değişim ve tamir desteği',
    alt: 'Lastik değişim hizmeti',
  },
] as const;

export const services = [
  {
    icon: '🚗',
    title: 'Oto Çekici',
    description:
      'Arızalı veya kaza yapmış aracınızı en yakın servise veya istediğiniz adrese güvenle taşıyoruz.',
  },
  {
    icon: '🛟',
    title: 'Acil Yol Yardım',
    description:
      'Yolda kaldığınızda 7/24 ulaşabileceğiniz profesyonel yol yardım ekibimiz hazır.',
  },
  {
    icon: '🔋',
    title: 'Akü Takviyesi',
    description:
      'Bitmiş akünüz için hızlı takviye ve gerekirse yeni akü montajı yapıyoruz.',
  },
  {
    icon: '🛞',
    title: 'Lastik Değişimi',
    description:
      'Patlak veya hasarlı lastiğinizi yerinde değiştiriyor, yola devam etmenizi sağlıyoruz.',
  },
] as const;

export const stats = [
  { value: '7/24', label: 'Kesintisiz Hizmet' },
  { value: '15 dk', label: 'Ortalama Varış' },
  { value: '5000+', label: 'Mutlu Müşteri' },
  { value: '12+', label: 'Yıllık Deneyim' },
] as const;

export const faqs = [
  {
    question: 'İstanbul Anadolu Yakası\'nda ne kadar sürede gelirsiniz?',
    answer:
      'Kadıköy, Üsküdar, Ataşehir ve çevre ilçelerde ortalama 15 dakika içinde ekibimiz yanınızda olur. Trafik yoğunluğuna göre süre değişebilir.',
  },
  {
    question: 'Gece ve hafta sonu hizmet veriyor musunuz?',
    answer:
      'Evet. Çekici Pro olarak 7 gün 24 saat kesintisiz oto çekici ve yol yardım hizmeti sunuyoruz.',
  },
  {
    question: 'Fiyatlandırma nasıl yapılıyor?',
    answer:
      'Mesafe, araç tipi ve hizmet türüne göre şeffaf fiyatlandırma uyguluyoruz. Telefonla aradığınızda net fiyat bilgisi verilir.',
  },
  {
    question: 'Hangi araç tiplerini çekebiliyorsunuz?',
    answer:
      'Binek otomobil, SUV, hafif ticari araç ve motosiklet taşıma hizmeti veriyoruz. Ağır vasıta için ayrı ekipmanımız mevcuttur.',
  },
] as const;

export const navLinks = [
  { href: '#hero', label: 'Ana Sayfa' },
  { href: '#hizmetler', label: 'Hizmetler' },
  { href: '#sss', label: 'SSS' },
  { href: '#iletisim', label: 'İletişim' },
] as const;
