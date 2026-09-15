# Filo Yönetim Sistemi

100 araçlık filo kiralama şirketi için kapsamlı takip uygulaması.

## Modüller
- **accounts** — Rol tabanlı kullanıcı yönetimi (Admin / Operasyon / Şoför)
- **vehicles** — Araç bilgileri, durum, fiyatlandırma
- **rentals** — Müşteri, kiralama, sözleşme, müsaitlik/çakışma kontrolü
- **maintenance** — Bakım ve muayene takibi
- **expenses** — HGS harcama kayıtları
- **damages** — Hasar takibi
- **reports** — Doluluk, finansal, bakım, HGS, hasar raporları + Excel/PDF export + otomatik e-posta uyarıları

## Yerel Kurulum (geliştirme)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # değerleri düzenleyin
# DATABASE_URL'i yerel PostgreSQL'inize göre ayarlayın ya da docker-compose ile db'yi ayağa kaldırın

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Docker ile Kurulum (Proxmox / Linux sunucu — önerilen)

```bash
cp .env.example .env   # değerleri düzenleyin, SECRET_KEY'i mutlaka değiştirin
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Uygulama `http://sunucu-ip:8000` adresinde, admin panel `/admin/` altında çalışır.

## GitHub → Sunucu Dağıtım Akışı

1. Bu klasörü GitHub'da özel (private) bir repoya push edin.
2. Sunucuda: `git clone <repo-url> && cd fleet_manager`
3. `.env` dosyasını sunucuda oluşturun (repoya eklemeyin — `.gitignore`'da).
4. `docker compose up -d --build`
5. Güncelleme sonrası: `git pull && docker compose up -d --build && docker compose exec web python manage.py migrate`

## Henüz Tamamlanmayan / Sıradaki Adımlar

- [ ] Kiralama oluşturma/düzenleme formları (rentals app'te view/template'ler)
- [ ] Araç CRUD ekranları (vehicles app'te view/template'ler)
- [ ] Bakım/muayene/HGS/hasar kayıt giriş formları
- [ ] Kiralama onayı sonrası otomatik e-posta gönderimi (SMS'e gerek yok)
- [ ] Kalan rapor şablonları (financial, maintenance, hgs, damage — occupancy_report.html örnek alınarak)
- [ ] Diğer raporlar için PDF export view'ları (excel gibi)
- [ ] Şoför paneli ekranları (teslim/iade onayı, hasar bildirimi formu)
- [ ] Testler

## Notlar
- Min. 3 gün kiralama kuralı sadece bilgilendirme amaçlıdır, sistem engellemez (`Rental.is_below_minimum_days`).
- Araç çakışma kontrolü `Vehicle.is_available_between()` ve `Rental.clean()` içinde yapılır.
- GPS/konum takibi bilerek kapsam dışı bırakılmıştır (TRIOMobil kullanılıyor).
