# Perpustakaan PNJ

<p align="center">
  <img src="static/assets/img/logo-ct-dark.png" alt="Perpustakaan PNJ" width="180" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white" alt="Flask badge" />
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white" alt="SQLite badge" />
  <img src="https://img.shields.io/badge/Nginx-Reverse%20Proxy-009639?logo=nginx&logoColor=white" alt="Nginx badge" />
  <img src="https://img.shields.io/badge/Admin-Only-5E72E4" alt="Admin only badge" />
  <img src="https://img.shields.io/badge/PDF%20%2F%20EPUB-Upload%20%26%20Download-111827" alt="PDF EPUB badge" />
</p>

<p align="center">
  Dashboard admin untuk mengelola koleksi buku Perpustakaan PNJ. Fokusnya sederhana: overview, CRUD buku, manage admin, profile, cover lokal, dan upload/download file buku.
</p>

## 🔎 Ikhtisar project

Perpustakaan PNJ adalah web app admin-only berbasis Flask yang memakai template Soft UI Dashboard sebagai fondasi tampilan.

Aplikasi ini dibuat untuk:
- mengelola data buku secara cepat
- menampilkan katalog buku dengan cover lokal
- upload file buku PDF/EPUB dan mengunduhnya kembali
- mengelola akun admin
- melihat ringkasan dashboard secara visual

Aplikasi berjalan internal di `127.0.0.1:8000` dan idealnya diakses publik lewat Nginx reverse proxy di port `80`.

## 📸 Showcase

<p align="center">
  <img src="assets/readme/showcase-dashboard.png" alt="Dashboard showcase" width="32%" />
  <img src="assets/readme/showcase-catalog.png" alt="Catalog showcase" width="32%" />
  <img src="assets/readme/showcase-detail.png" alt="Detail showcase" width="32%" />
</p>

## ⭐ Fitur utama

- Dashboard overview untuk ringkasan data perpustakaan
- CRUD buku lengkap
- Manage admin / user admin
- Halaman profile admin
- Cover buku lokal dari folder aset yang ditentukan
- Upload file buku PDF/EPUB
- Download file buku dari halaman detail
- Tampilan katalog modern berbentuk card/grid
- Search dan filter katalog buku
- Fallback cover `cover not available` jika cover kosong
- Nginx reverse proxy agar Flask tetap internal di port 8000

## 🧱 Tech stack

- Flask
- Flask-Login
- Flask-WTF + CSRF protection
- Flask-SQLAlchemy
- SQLite
- Jinja2 templates
- Soft UI Dashboard template
- Nginx reverse proxy
- Pillow untuk asset showcase README

## 📁 Struktur penting project

```txt
perpustakaan-pnj/
├── apps/
│   ├── authentication/
│   ├── home/
│   ├── config.py
│   ├── forms.py
│   └── models.py
├── assets/
│   └── readme/
│       ├── showcase-dashboard.png
│       ├── showcase-catalog.png
│       └── showcase-detail.png
├── nginx/
│   └── activate-perpustakaan-nginx.sh
├── static/
│   └── assets/img/books/covers/
├── templates/
│   └── pages/
├── uploads/
│   └── books/
├── run.py
└── README.md
```

## ⚙️ Kebutuhan

- Python 3.11+ direkomendasikan
- pip
- Git
- Nginx untuk akses publik

## 🚀 Cara menjalankan secara lokal

1. Clone atau buka project ini.

2. Buat virtual environment:

```bash
python -m venv .venv
```

3. Aktifkan virtual environment:

```bash
source .venv/bin/activate
```

4. Install dependency:

```bash
pip install -r requirements.txt
```

5. Jalankan aplikasi:

```bash
python run.py
```

6. Buka di browser:

```txt
http://127.0.0.1:8000/
```

Catatan:
- database SQLite akan dibuat otomatis saat pertama kali dijalankan
- data seed awal juga dibuat otomatis jika database masih kosong

## 🌐 Akses lewat Nginx

Kalau mau diakses dari laptop lain atau VM, gunakan reverse proxy Nginx:

1. Jalankan Flask internal di port 8000:

```bash
python run.py
```

2. Aktifkan konfigurasi Nginx:

```bash
sudo bash nginx/activate-perpustakaan-nginx.sh
```

3. Akses dari device lain memakai IP host:

```txt
http://IP_HOST/
```

Catatan penting:
- Flask tetap bind ke `127.0.0.1:8000`
- port 8000 bukan pintu publik
- pintu publiknya ada di Nginx port 80

## 📂 Folder file penting

- `static/assets/img/books/covers/` → cover buku lokal
- `uploads/books/` → file PDF/EPUB yang diupload admin
- `assets/readme/` → gambar showcase untuk README
- `nginx/activate-perpustakaan-nginx.sh` → helper untuk mengarahkan Nginx ke app perpustakaan

## 🖼️ Cover dan file buku

Saat menambah atau mengedit buku:
- cover bisa diupload dalam format gambar yang didukung
- file buku hanya menerima PDF atau EPUB
- kalau cover tidak ada, UI akan menampilkan teks fallback `cover not available`
- file yang diupload bisa didownload dari halaman detail buku

## 🔐 Catatan login admin

Aplikasi memakai akun admin seed awal untuk verifikasi pertama kali.

Jika kamu ingin mengganti akun admin:
- buat admin baru dari halaman Admin
- atau update data user yang sudah ada

## 🧪 Checklist verifikasi cepat

```bash
ss -ltnp | grep ':8000'
curl -I http://127.0.0.1:8000/login
```

Hasil yang diharapkan:
- Flask hanya listen di `127.0.0.1:8000`
- halaman login merespons normal
- akses publik tetap lewat Nginx

## 📌 Ringkasan singkat

Project ini sengaja dibuat fokus dan ringan:
- admin-only
- CRUD buku
- manage admin
- profile
- katalog buku yang rapi
- file buku lokal
- reverse proxy Nginx

Kalau kamu mau, langkah berikutnya biasanya adalah memperhalus UI detail/daftar buku lagi atau menambah fitur pencarian/sortir yang lebih advanced.
