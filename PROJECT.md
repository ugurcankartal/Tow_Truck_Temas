# Tow Truck Temas — Proje Dokümantasyonu

Çekici işletmesi için tek sayfalık SEO/GEO odaklı tanıtım sitesi.  
**Frontend:** Astro + Tailwind | **Backend:** Django REST API + MySQL

---

## Klasör yapısı

```
Tow_Truck_Temas/
├── frontend/          # Astro ön yüz (SSG / opsiyonel SSR)
├── backend/           # Django REST API + Admin
├── PROJECT.md         # Bu dosya
```

---

## Frontend (Astro)

### Bölümler (her biri 100vh × 100vw)

| Bölüm | Bileşen | Özellik |
|-------|---------|---------|
| Navigator | `Navigator.astro` | Sabit üst menü, scroll'da blur arka plan |
| Kontainer 1 | `HeroSlider.astro` | Beyaz arka plan, animasyonlu slider, tanıtım metni |
| Kontainer 2 | `ScrollDraw.astro` | Scroll-draw; resimler üst üste, ters scroll destekli |
| Kontainer 3 | `ServicesSection.astro` | İstatistikler, hizmetler, SSS, iletişim formu |
| Footer | `Footer.astro` | NAP, hizmet bölgeleri, CTA |

### SEO / GEO

- Semantik HTML (`header`, `main`, `section`, `footer`)
- `Layout.astro` → title, description, keywords, canonical, Open Graph
- `JsonLd.astro` → API'den gelen `json_ld` (LocalBusiness, FAQPage)
- `robots.txt`, sitemap (`@astrojs/sitemap`)
- H1: ana anahtar kelime odaklı

### API entegrasyonu

- `src/lib/site-settings.ts` → `GET /api/site-settings/`
- **Dev:** her sayfa yenilemede API çağrılır (`cache: no-store`)
- **Static prod:** build anında API verisi HTML'e gömülür
- **SSR prod:** her istekte API (`ASTRO_OUTPUT=server`)

### Ortam değişkenleri (`frontend/.env`)

```env
PUBLIC_API_URL=http://127.0.0.1:8000
```

### Komutlar

```bash
cd frontend
npm install
npm run dev              # http://localhost:4321
npm run build            # Statik dist/ (SSG)
npm run build:ssr        # SSR build (Node gerekir)
npm run start:ssr        # SSR sunucu
npm run webhook:rebuild  # Webhook dinleyici (port 9876)
```

---

## Backend (Django)

### Modeller

| Model | Açıklama |
|-------|----------|
| `SiteSettings` | Tekil (singleton) — SEO meta, NAP, sosyal, koordinat |
| `FAQ` | SSS — JSON-LD FAQPage için |
| `ContactMessage` | İletişim formu kayıtları |

### API uç noktaları

| Method | URL | Açıklama |
|--------|-----|----------|
| GET | `/api/site-settings/` | SEO + business + faqs + json_ld |
| POST | `/api/contact/` | İletişim formu |
| POST | `/api/trigger-rebuild/` | Manuel rebuild (X-Webhook-Secret gerekli) |

### Veritabanı

MySQL — ayarlar `backend/.env`:

```env
DEV_DB_NAME=tow_truck_temas
DEV_DB_USER=root
DEV_DB_PASSWORD=...
DEV_DB_HOST=127.0.0.1
DEV_DB_PORT=3306
```

Driver: **PyMySQL**

### Admin

- `/admin/` → Site Ayarları, SSS, İletişim Mesajları
- URL alanları özel form ile düzenlenebilir (`core/forms.py`)

### Komutlar

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_site
python manage.py createsuperuser
python manage.py runserver
python manage.py trigger_astro_rebuild --sync
```

---

## Astro rebuild akışı (admin → prod HTML)

Admin'de **SiteSettings** veya **FAQ** kaydedilince Django sinyali tetiklenir:

```
Admin Kaydet
    ↓
core/signals.py
    ↓
core/services/astro_rebuild.py
    ├── ASTRO_REBUILD_WEBHOOK_URL → POST webhook (build sunucusuna)
    └── ASTRO_REBUILD_LOCAL=true  → npm run build (subprocess)
```

### 1. Django admin → otomatik rebuild

| Yöntem | Env | Ne yapar |
|--------|-----|----------|
| **Webhook** | `ASTRO_REBUILD_WEBHOOK_URL` | Build sunucusuna POST |
| **Yerel build** | `ASTRO_REBUILD_LOCAL=true` | `npm run build` subprocess |

`backend/.env` örneği (hazır):

```env
ASTRO_REBUILD_WEBHOOK_URL=http://127.0.0.1:9876/rebuild
ASTRO_REBUILD_WEBHOOK_SECRET=dev-webhook-secret-change-in-prod
ASTRO_REBUILD_LOCAL=false
ASTRO_BUILD_SCRIPT=build
FRONTEND_DIR=../frontend
```

**Manuel tetikleme:**

```bash
python manage.py trigger_astro_rebuild --sync
```

```http
POST /api/trigger-rebuild/
Header: X-Webhook-Secret: <ASTRO_REBUILD_WEBHOOK_SECRET>
```

### 2. Webhook dinleyici

```bash
cd frontend
WEBHOOK_SECRET=dev-webhook-secret-change-in-prod npm run webhook:rebuild
```

→ `http://127.0.0.1:9876/rebuild` adresini dinler, `npm run build` çalıştırır.  
Health check: `http://127.0.0.1:9876/health`

Admin'de kayıt → webhook logunda build görünür → `dist/` güncellenir.

### 3. Astro SSR (prod alternatifi)

```bash
npm run build:ssr    # ASTRO_OUTPUT=server
npm run start:ssr    # Node sunucu — her istekte API'den SEO
```

- Varsayılan hâlâ **SSG** (`npm run build`).
- SSR'ye prod'da geçmek için `ASTRO_BUILD_SCRIPT=build:ssr` yeterli (backend `.env`).

### Prod seçenekleri

| Mod | Ne zaman | Nasıl |
|-----|----------|-------|
| **SSG + webhook** | Statik hosting (Netlify, Nginx) | Admin kaydı → CI/build sunucusu rebuild |
| **SSR** | Dinamik SEO, Node sunucu | `npm run build:ssr` + `npm run start:ssr` |
| **Dev** | Geliştirme | `npm run dev` — API anlık, rebuild gerekmez |

Prod'da sorun çıkarsa yukarıdaki tablodan **SSG+webhook** veya **SSR** yolunu seçip ince ayar yapın.

### Prod test akışı (3 terminal)

```bash
# 1 — Django
cd backend && python manage.py runserver

# 2 — Webhook
cd frontend && npm run webhook:rebuild

# 3 — Astro dev
cd frontend && npm run dev
```

**Test adımları:**

1. Admin'de title veya description değiştir → **Kaydet**
2. Webhook terminalinde build logunu kontrol et
3. `frontend/dist/index.html` içinde güncel meta etiketlerini doğrula
4. Dev için: `http://localhost:4321/` → view-source ile anlık SEO kontrolü

---

## Ortam değişkenleri özeti

### backend/.env

| Değişken | Açıklama |
|----------|----------|
| `DEBUG` | Geliştirme modu |
| `SECRET_KEY` | Django secret |
| `CORS_ALLOWED_ORIGINS` | Astro dev URL |
| `DEV_DB_*` | MySQL bağlantısı |
| `ASTRO_REBUILD_WEBHOOK_URL` | Rebuild webhook URL |
| `ASTRO_REBUILD_WEBHOOK_SECRET` | Webhook güvenlik anahtarı |
| `ASTRO_REBUILD_LOCAL` | `true` ise Django doğrudan npm build çalıştırır |
| `ASTRO_BUILD_SCRIPT` | `build` veya `build:ssr` |
| `FRONTEND_DIR` | Frontend klasör yolu |

### frontend/.env

| Değişken | Açıklama |
|----------|----------|
| `PUBLIC_API_URL` | Django API base URL |
| `ASTRO_OUTPUT` | `server` → SSR (build sırasında) |
| `SITE_URL` | Canonical site URL (astro.config) |

---

## Geliştirme sırası (hatırlatma)

1. ✅ Astro tek sayfa arayüz (slider, scroll-draw, hizmetler, footer)
2. ✅ SEO/GEO: meta, JSON-LD, sitemap, semantik HTML
3. ✅ Django REST: SiteSettings API, Contact API
4. ✅ MySQL geçişi
5. ✅ Admin → Astro dev dinamik SEO (API fetch)
6. ✅ Admin save → webhook rebuild altyapısı
7. ✅ Astro SSR hazırlığı (`build:ssr`, `@astrojs/node`)
8. ⏳ Prod deploy ince ayarı (CI, Nginx, SSL)

---

## Hızlı başlangıç (geliştirme)

```bash
# 1 — Backend
cd backend && python manage.py runserver

# 2 — Webhook (opsiyonel, prod benzeri rebuild test)
cd frontend && npm run webhook:rebuild

# 3 — Frontend
cd frontend && npm run dev
```

Admin: http://127.0.0.1:8000/admin/  
Site: http://localhost:4321/

> Tam prod test akışı için yukarıdaki **Prod test akışı (3 terminal)** bölümüne bakın.

*Son güncelleme: 2026-07-03*
