# Tow_Truck_Temas

Çekici / oto yol yardım tanıtım sitesi — **Astro** frontend + **Django REST API** backend.

Detaylı kurulum, ortam değişkenleri ve prod deploy adımları için [PROJECT.md](PROJECT.md) dosyasına bakın.

## Hızlı başlangıç (geliştirme)

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env   # değerleri düzenleyin
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Üretim (Ubuntu)

- Nginx: `deploy/nginx/temasotoyolyardim.conf.example`
- Gunicorn: `deploy/gunicorn/temasotoyolyardim.py`
- Systemd: `deploy/systemd/temasotoyolyardim-gunicorn.service.example`

Domain: **temasotoyolyardim.com**
