# Perpustakaan PNJ

<p align="center">
  <img src="assets/logo_perpustakaan_flask_web.png" alt="Perpustakaan PNJ" width="180" />
</p>

<p align="center"><em>Logo menggunakan file <code>assets/logo_perpustakaan_flask_web.png</code>.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white" alt="Flask badge" />
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white" alt="SQLite badge" />
  <img src="https://img.shields.io/badge/Nginx-Reverse%20Proxy-009639?logo=nginx&logoColor=white" alt="Nginx badge" />
  <img src="https://img.shields.io/badge/Gunicorn-Production-2F855A" alt="Gunicorn badge" />
</p>

Aplikasi web admin-only untuk mengelola koleksi buku Perpustakaan PNJ. Project ini dibuat agar mudah dipahami, mudah dijalankan, dan bisa dipasang di beberapa distribusi Linux dengan script Bash yang sama.

## Ringkasan project

Perpustakaan PNJ adalah web app berbasis Flask untuk:
- mengelola data buku secara terpusat
- menampilkan katalog buku dengan cover lokal
- upload dan download file buku PDF / EPUB
- mengelola akun admin
- menampilkan dashboard ringkas untuk monitoring data

Aplikasi dijalankan dengan Gunicorn di dalam Python virtual environment (`venv`).
Setelah install, Nginx akan diarahkan ke app Flask di port 80 sehingga akses lewat `http://IP_SERVER/` menampilkan Perpustakaan PNJ, bukan halaman default Nginx.

## Kenapa project ini dibuat

Project ini cocok untuk tugas dosen karena memperlihatkan alur deployment yang rapi:
- ada source code web app
- ada dependency Python yang terisolasi di `venv`
- ada service systemd untuk menjalankan aplikasi seperti server sungguhan
- ada Nginx sebagai reverse proxy
- ada script install dan uninstall yang jelas
- bisa dijalankan di beberapa distro Linux tanpa ubah banyak langkah

## Fitur utama

- Dashboard overview
- CRUD buku
- Manage admin / user admin
- Halaman profile admin
- Upload cover buku lokal
- Upload file buku PDF / EPUB
- Download file buku dari halaman detail
- Search dan filter katalog
- Fallback cover `cover not available` jika cover kosong
- Reverse proxy Nginx agar Flask tetap internal di port 8000

## Dukungan Linux

Script install sudah mendeteksi distro otomatis. Dukungan utama:
- Ubuntu / Debian
- Arch Linux / Manjaro
- Fedora / RHEL / CentOS
- openSUSE / SLES

## Struktur penting project

```txt
perpustakaan-flask-web/
├── apps/
├── assets/
│   └── readme/
├── nginx/
├── static/
├── uploads/
├── install.sh
├── uninstall.sh
├── requirements.txt
├── run.py
└── README.md
```

## Cara menjalankan yang paling mudah

### Opsi yang direkomendasikan: pakai install.sh

Kalau repo sudah di-clone:

```bash
git clone https://github.com/Alief1150/perpustakaan-flask-web.git
cd perpustakaan-flask-web
sudo bash install.sh
```

Kalau kamu hanya punya file `install.sh` dan menjalankannya di folder kosong, script akan clone repository ini otomatis lalu lanjut instalasi.

Yang dilakukan script:
- mendeteksi distro Linux
- memasang paket sistem yang dibutuhkan
- clone / update repo ke branch `main`
- membuat virtual environment
- install dependency Python
- membuat file `.env`
- memasang service systemd untuk Gunicorn
- memasang konfigurasi Nginx
- menyalakan service aplikasi

Setelah selesai, aplikasi bisa diakses lewat:
- lokal: `http://127.0.0.1:8000/`
- publik: `http://IP_SERVER/` melalui Nginx

## Contoh instalasi di beberapa distro Linux

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip nginx

git clone https://github.com/Alief1150/perpustakaan-flask-web.git
cd perpustakaan-flask-web
sudo bash install.sh
```

### Arch Linux / Manjaro

```bash
sudo pacman -Syu --needed git python python-pip nginx

git clone https://github.com/Alief1150/perpustakaan-flask-web.git
cd perpustakaan-flask-web
sudo bash install.sh
```

### Fedora / RHEL / CentOS

```bash
sudo dnf install -y git python3 python3-pip python3-devel nginx

git clone https://github.com/Alief1150/perpustakaan-flask-web.git
cd perpustakaan-flask-web
sudo bash install.sh
```

### openSUSE / SLES

```bash
sudo zypper --non-interactive install git python3 python3-pip python3-devel nginx

git clone https://github.com/Alief1150/perpustakaan-flask-web.git
cd perpustakaan-flask-web
sudo bash install.sh
```

Catatan:
- langkah manual di atas menunjukkan perbedaan paket antar distro
- sebenarnya `install.sh` sudah menangani instalasi paket sistem secara otomatis
- kalau paket sistem sudah ada, script akan lanjut ke tahap setup project

## Menjalankan manual untuk development

Kalau ingin menjalankan tanpa service production:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Akses:

```txt
http://127.0.0.1:8000/
```

## Cara akses lewat Nginx

Secara arsitektur:
- Flask / Gunicorn jalan di `127.0.0.1:8000`
- Nginx menjadi pintu publik di port `80`

Jadi alurnya seperti ini:

```txt
Browser -> Nginx (80) -> Gunicorn (127.0.0.1:8000) -> Flask app
```

Ini adalah pola yang umum dipakai untuk deployment web app Python di Linux server.

## Cara uninstall

Untuk menghapus komponen project yang dipasang oleh script:

```bash
sudo bash uninstall.sh
```

Yang dihapus oleh uninstall:
- service systemd
- konfigurasi Nginx project
- `.env`
- folder virtual environment `.venv`
- folder project
- state instalasi milik project

Uninstall tidak menghapus dependency global sistem, jadi lebih aman.

## File penting

- `run.py` → entrypoint aplikasi
- `gunicorn-cfg.py` → konfigurasi Gunicorn
- `env.sample` → contoh environment variable
- `install.sh` → installer otomatis multi-distro
- `uninstall.sh` → penghapus komponen project
- `nginx/perpustakaan.conf` → contoh konfigurasi reverse proxy

## Catatan database

Project ini memakai SQLite secara default, jadi tidak perlu install database server terpisah.
Data disimpan di file database lokal pada project.

## Screenshot

<p align="center">
  <img src="assets/readme/showcase-dashboard.png" alt="Dashboard showcase" width="32%" />
  <img src="assets/readme/showcase-catalog.png" alt="Catalog showcase" width="32%" />
  <img src="assets/readme/showcase-detail.png" alt="Detail showcase" width="32%" />
</p>

## Ringkasan singkat untuk dosen

Project ini menunjukkan deployment Flask yang rapi dan realistis:
- source code jelas
- dependency Python terisolasi di venv
- aplikasi dijalankan oleh Gunicorn
- akses publik lewat Nginx
- bisa dipasang di beberapa distro Linux
- ada script install dan uninstall yang seimbang

### Penjelasan singkat `install.sh`

Script `install.sh` dipakai untuk memasang seluruh stack aplikasi secara otomatis. Alurnya dibuat berurutan supaya instalasi bisa jalan di banyak distro Linux tanpa langkah manual yang panjang.

1. Persiapan awal
   - script berjalan dengan mode aman `set -euo pipefail`
   - wajib dijalankan sebagai root atau lewat `sudo`
   - nama aplikasi, lokasi project, file service, file `.env`, dan konfigurasi Nginx sudah didefinisikan dari awal

2. Deteksi distro Linux
   - script membaca `/etc/os-release`
   - lalu menyesuaikan perintah instalasi paket untuk:
     - Arch / Manjaro
     - Debian / Ubuntu
     - Fedora / RHEL / CentOS
     - openSUSE / SLES
   - kalau distro tidak dikenali, instalasi dihentikan dengan pesan yang jelas

3. Instalasi paket sistem
   - memasang paket yang dibutuhkan: `git`, `python3`, `python3-venv`, `python3-pip`, dan `nginx`
   - untuk beberapa distro, script juga menyesuaikan paket tambahan seperti `python3-devel`

4. Ambil source code project
   - kalau repo sudah ada di folder project, script akan `fetch`, `checkout main`, lalu `reset --hard origin/main`
   - kalau repo belum ada, script akan clone dari GitHub ke folder target
   - kalau ada folder target yang bukan repo Git, script akan berhenti agar tidak menimpa data lain

5. Menyiapkan folder runtime
   - membuat folder untuk cover buku, upload file buku, dan aset README jika belum ada
   - ini penting supaya aplikasi tidak gagal saat menyimpan file atau menampilkan gambar

6. Membuat / melengkapi file `.env`
   - jika `.env` belum ada, script membuat file baru berisi konfigurasi dasar aplikasi
   - jika `.env` sudah ada, script mempertahankan isi lama lalu memastikan variabel penting tetap tersedia
   - variabel yang disiapkan mencakup:
     - `DEBUG`
     - `FLASK_APP`
     - `FLASK_DEBUG`
     - `SECRET_KEY`
     - `DATABASE_URL`
     - `ASSETS_ROOT`

7. Menyiapkan virtual environment
   - script membuat folder `.venv` jika belum ada
   - lalu meng-upgrade `pip`, `wheel`, dan `setuptools`
   - setelah itu semua dependency di `requirements.txt` dipasang ke environment tersebut
   - tujuan utamanya supaya package Python tidak bercampur dengan sistem

8. Menyesuaikan ownership folder project
   - script mengubah ownership folder project ke user yang menjalankan instalasi
   - ini mencegah masalah izin saat aplikasi menulis file upload, asset, atau database

9. Membuat service systemd untuk Gunicorn
   - script menulis file service di `/etc/systemd/system/perpustakaan-flask-web.service`
   - Gunicorn dijalankan sebagai service systemd
   - aplikasi dibind ke `127.0.0.1:8000`
   - jadi Flask tetap internal, sementara akses publik nanti ditangani Nginx
   - service di-enable agar otomatis hidup saat server restart

10. Membuat konfigurasi Nginx
   - script menulis konfigurasi reverse proxy ke `/etc/nginx/conf.d/perpustakaan-flask-web.conf`
   - Nginx diset mendengar di port `80` dengan `default_server`
   - request dari browser diteruskan ke Gunicorn di `127.0.0.1:8000`
   - script juga menghapus konfigurasi default Nginx bawaan supaya tidak muncul halaman “Welcome to nginx”
   - setelah itu konfigurasi diuji dengan `nginx -t`

11. Menyimpan state instalasi
   - script menyimpan file state di `/etc/perpustakaan-flask-web/install.env`
   - file ini dipakai oleh proses uninstall agar bisa tahu lokasi service, folder project, dan konfigurasi yang harus dihapus

12. Menyalakan service
   - `systemd` dan `nginx` direstart
   - lalu script menampilkan status service sebagai verifikasi awal
   - hasil akhirnya:
     - akses lokal tetap bisa lewat `http://127.0.0.1:8000/`
     - akses jaringan lewat `http://IP_SERVER/`

### Penjelasan singkat `uninstall.sh`

Script `uninstall.sh` dipakai untuk membersihkan komponen project yang dipasang oleh `install.sh`. Fokusnya adalah menghapus semua bagian milik project tanpa mengganggu dependency global sistem.

1. Persiapan awal
   - script juga memakai `set -euo pipefail`
   - wajib dijalankan dengan `sudo` atau root
   - kalau file state instalasi tersedia, script membacanya untuk mendapatkan lokasi file yang benar

2. Menghentikan service aplikasi
   - service `perpustakaan-flask-web` dihentikan
   - lalu di-disable supaya tidak otomatis berjalan saat boot

3. Menghapus file service systemd
   - file service di `/etc/systemd/system/perpustakaan-flask-web.service` dihapus
   - setelah itu `systemctl daemon-reload` dijalankan agar systemd memperbarui daftar service

4. Menghapus konfigurasi Nginx project
   - file konfigurasi Nginx project dihapus dari `/etc/nginx/conf.d/`
   - setelah itu Nginx diuji dan di-reload supaya konfigurasi lama tidak dipakai lagi

5. Menghapus environment dan virtual environment
   - file `.env` project dihapus
   - folder `.venv` juga dihapus karena isinya hanya milik project ini

6. Menghapus folder project
   - seluruh folder project dihapus dari disk
   - ini termasuk source code dan folder kerja yang dipakai instalasi

7. Menghapus state instalasi
   - folder `/etc/perpustakaan-flask-web/` dihapus
   - jadi tidak ada sisa metadata instalasi yang tertinggal

8. Hasil akhir uninstall
   - service aplikasi hilang
   - konfigurasi Nginx project hilang
   - virtual environment hilang
   - file environment hilang
   - folder project hilang
   - dependency global sistem tetap aman karena tidak ikut dihapus

Kalau ingin, saya juga bisa bantu menambahkan versi yang lebih singkat lagi untuk presentasi lisan di depan dosen.
