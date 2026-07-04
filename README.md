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

Proje dizini: **`/home/ubuntu/Tow_Truck_Temas/`**

```bash
git clone https://github.com/ugurcankartal/Tow_Truck_Temas.git /home/ubuntu/Tow_Truck_Temas
cd /home/ubuntu/Tow_Truck_Temas

python3 -m venv venv
source venv/bin/activate

cd backend
cp .env.example .env
# .env içinde DB_* ve PROD_SECRET_KEY değerlerini doldurun:
#   python ../generate_env_secrets.py --write
pip install -r requirements.txt
python manage_prod.py migrate
python manage_prod.py collectstatic --noinput
python manage_prod.py createsuperuser   # isteğe bağlı

cd ../frontend
npm install
sudo chown -R ubuntu:ubuntu /home/ubuntu/Tow_Truck_Temas/frontend
sudo -u ubuntu npm run build:prod

sudo chmod 755 /home/ubuntu
```

**Önemli:** Önyüz statik (`frontend/dist`). Admin’de metin/resim değişince otomatik yansıması için **Astro rebuild webhook** servisini kurun (aşağıya bakın).

- Nginx: `deploy/nginx/temasotoyolyardim.conf.example`
- Gunicorn: `deploy/gunicorn/temasotoyolyardim.py`
- Systemd: `deploy/systemd/temasotoyolyardim-gunicorn.service.example`
- Astro rebuild: `deploy/systemd/temasotoyolyardim-astro-rebuild.service.example`

Domain: **temasotoyolyardim.com**

### Admin → önyüz otomatik güncelleme (prod)

Dev’de `ASTRO_REBUILD_LOCAL=true` veya webhook vardı. Prod’da aynı akış:

```
Admin Kaydet → Django sinyali → POST /rebuild → npm run build:prod → dist/ güncellenir
```

1. `backend/.env` içinde (satır sonu `#` yorumu kullanmayın):

```env
ASTRO_REBUILD_WEBHOOK_URL=http://127.0.0.1:9876/rebuild
PROD_ASTRO_REBUILD_WEBHOOK_SECRET=...   # python ../generate_env_secrets.py --write
ASTRO_BUILD_SCRIPT=build:prod
ASTRO_REBUILD_LOCAL=false
```

2. Webhook systemd servisi (`ubuntu` kullanıcısı `.env` okuyabilmeli — `usermod -aG www-data ubuntu`):

```bash
sudo usermod -aG www-data ubuntu
sudo cp deploy/systemd/temasotoyolyardim-astro-rebuild.service.example \
  /etc/systemd/system/temasotoyolyardim-astro-rebuild.service
sudo systemctl daemon-reload
sudo systemctl enable --now temasotoyolyardim-astro-rebuild
curl http://127.0.0.1:9876/health
```

**Frontend izinleri:** Webhook servisi `ubuntu` kullanıcısıyla `npm run build` çalıştırır. **`root` ile build yapmayın** — `.astro/` ve `dist/` root’a kalırsa webhook `EACCES` verir. Düzeltme:

```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/Tow_Truck_Temas/frontend
# nginx okuyabilsin (dist statik)
chmod -R o+rX /home/ubuntu/Tow_Truck_Temas/frontend/dist
```

3. İlk deploy build’i **ubuntu** ile: `sudo -u ubuntu npm run build:prod` (veya `su - ubuntu`)

4. Admin’de Site Ayarları kaydedin → birkaç saniye sonra view-source’ta SEO/JSON-LD güncellenmiş olmalı.

Manuel tetikleme: `python manage_prod.py trigger_astro_rebuild --sync`
