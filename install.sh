#!/usr/bin/env bash
set -euo pipefail

APP_NAME="perpustakaan-flask-web"
REPO_URL="https://github.com/Alief1150/perpustakaan-flask-web.git"
BRANCH="main"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${APP_DIR}/.venv"
ENV_FILE="${APP_DIR}/.env"
SERVICE_NAME="${APP_NAME}"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
NGINX_CONF="/etc/nginx/conf.d/${SERVICE_NAME}.conf"
STATE_DIR="/etc/${SERVICE_NAME}"
STATE_FILE="${STATE_DIR}/install.env"
APP_PORT="8000"
APP_HOST="127.0.0.1"
SERVICE_USER="${SUDO_USER:-$(logname 2>/dev/null || echo root)}"

log() { printf '[install] %s\n' "$*"; }
warn() { printf '[warn] %s\n' "$*" >&2; }
die() { printf '[error] %s\n' "$*" >&2; exit 1; }
require_root() { [[ ${EUID:-$(id -u)} -eq 0 ]] || die "Jalankan script ini dengan sudo/root."; }
command_exists() { command -v "$1" >/dev/null 2>&1; }

install_packages_apt() {
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y git python3 python3-venv python3-pip nginx
}

install_packages_pacman() {
  pacman -Sy --noconfirm --needed git python python-pip nginx
}

install_packages_dnf() {
  dnf install -y git python3 python3-pip python3-devel nginx
}

install_packages_yum() {
  yum install -y git python3 python3-pip python3-devel nginx
}

install_packages_zypper() {
  zypper --non-interactive install git python3 python3-pip python3-devel nginx
}

detect_os() {
  if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    case "${ID_LIKE:-${ID:-}}" in
      *arch*|*manjaro*|arch)
        echo arch
        ;;
      *debian*|*ubuntu*|debian|ubuntu)
        echo debian
        ;;
      *fedora*|*rhel*|*centos*|fedora|rhel|centos)
        echo fedora
        ;;
      *suse*|*opensuse*|sles|opensuse)
        echo suse
        ;;
      *)
        case "${ID:-}" in
          arch|manjaro) echo arch ;;
          debian|ubuntu) echo debian ;;
          fedora|rhel|centos) echo fedora ;;
          opensuse*|sles) echo suse ;;
          *) echo unknown ;;
        esac
        ;;
    esac
  else
    echo unknown
  fi
}

install_system_packages() {
  local os
  os="$(detect_os)"
  log "Detected OS: ${os}"

  case "${os}" in
    arch)
      install_packages_pacman
      ;;
    debian)
      install_packages_apt
      ;;
    fedora)
      if command_exists dnf; then
        install_packages_dnf
      else
        install_packages_yum
      fi
      ;;
    suse)
      install_packages_zypper
      ;;
    *)
      die "Distro tidak dikenali. Script ini mendukung Arch, Debian/Ubuntu, Fedora/RHEL, dan openSUSE."
      ;;
  esac
}

ensure_git_branch_main() {
  if git -C "${APP_DIR}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    log "Git repository ditemukan di ${APP_DIR}. Update ke branch ${BRANCH}."
    git -C "${APP_DIR}" fetch origin "${BRANCH}"
    git -C "${APP_DIR}" checkout "${BRANCH}"
    git -C "${APP_DIR}" reset --hard "origin/${BRANCH}"
  else
    die "Folder ${APP_DIR} bukan git repository. Clone repo ini dulu lalu jalankan install.sh dari root project."
  fi
}

create_env_file() {
  local secret_key database_url
  secret_key="$(python3 - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
)"
  database_url="sqlite:///${APP_DIR}/apps/perpustakaan_pnj.db"

  if [[ -f "${ENV_FILE}" ]]; then
    log ".env sudah ada, mempertahankan isi yang ada dan memastikan key penting tersedia."
    grep -q '^DEBUG=' "${ENV_FILE}" || printf '\nDEBUG=False\n' >> "${ENV_FILE}"
    grep -q '^FLASK_APP=' "${ENV_FILE}" || printf 'FLASK_APP=run.py\n' >> "${ENV_FILE}"
    grep -q '^FLASK_DEBUG=' "${ENV_FILE}" || printf 'FLASK_DEBUG=0\n' >> "${ENV_FILE}"
    grep -q '^ASSETS_ROOT=' "${ENV_FILE}" || printf 'ASSETS_ROOT=/static/assets\n' >> "${ENV_FILE}"
    grep -q '^SECRET_KEY=' "${ENV_FILE}" || printf 'SECRET_KEY=%s\n' "${secret_key}" >> "${ENV_FILE}"
    grep -q '^DATABASE_URL=' "${ENV_FILE}" || printf 'DATABASE_URL=%s\n' "${database_url}" >> "${ENV_FILE}"
  else
    cat > "${ENV_FILE}" <<EOF
DEBUG=False
FLASK_APP=run.py
FLASK_DEBUG=0
SECRET_KEY=${secret_key}
DATABASE_URL=${database_url}
ASSETS_ROOT=/static/assets
EOF
  fi
  chmod 640 "${ENV_FILE}"
}

setup_virtualenv() {
  if [[ ! -d "${VENV_DIR}" ]]; then
    log "Membuat virtualenv di ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
  fi
  "${VENV_DIR}/bin/python" -m pip install --upgrade pip wheel setuptools
  "${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"
}

fix_ownership() {
  chown -R "${SERVICE_USER}:${SERVICE_USER}" "${APP_DIR}"
}

ensure_runtime_dirs() {
  mkdir -p "${APP_DIR}/static/assets/img/books/covers"
  mkdir -p "${APP_DIR}/uploads/books"
  mkdir -p "${APP_DIR}/assets/readme"
}

install_systemd_service() {
  local gunicorn_workers
  gunicorn_workers="${GUNICORN_WORKERS:-2}"

  cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=Perpustakaan PNJ Flask app (Gunicorn)
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${APP_DIR}
EnvironmentFile=-${ENV_FILE}
ExecStart=${VENV_DIR}/bin/gunicorn --bind ${APP_HOST}:${APP_PORT} --workers ${gunicorn_workers} --access-logfile - --error-logfile - run:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

  systemctl daemon-reload
  systemctl enable "${SERVICE_NAME}"
}

install_nginx_config() {
  cat > "${NGINX_CONF}" <<EOF
server {
    listen 80;
    server_name _;
    client_max_body_size 25m;

    location / {
        proxy_pass http://${APP_HOST}:${APP_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }
}
EOF

  nginx -t
  systemctl enable nginx >/dev/null 2>&1 || true
}

save_install_state() {
  mkdir -p "${STATE_DIR}"
  cat > "${STATE_FILE}" <<EOF
APP_NAME=${APP_NAME}
APP_DIR=${APP_DIR}
VENV_DIR=${VENV_DIR}
ENV_FILE=${ENV_FILE}
SERVICE_NAME=${SERVICE_NAME}
SERVICE_FILE=${SERVICE_FILE}
NGINX_CONF=${NGINX_CONF}
SERVICE_USER=${SERVICE_USER}
REPO_URL=${REPO_URL}
BRANCH=${BRANCH}
EOF
  chmod 640 "${STATE_FILE}"
}

start_services() {
  systemctl restart "${SERVICE_NAME}"
  systemctl restart nginx
}

verify_installation() {
  log "Cek service..."
  systemctl --no-pager --full status "${SERVICE_NAME}" || true
  log "Jika firewall aktif, pastikan port 80 dibuka. Akses lokal: http://${APP_HOST}:${APP_PORT}/"
}

main() {
  require_root
  command_exists git || die "git belum tersedia di sistem."
  command_exists python3 || die "python3 belum tersedia di sistem."
  command_exists systemctl || die "systemd/systemctl tidak ditemukan di sistem ini."

  log "Mulai instalasi ${APP_NAME}"
  install_system_packages
  ensure_git_branch_main
  ensure_runtime_dirs
  create_env_file
  setup_virtualenv
  fix_ownership
  install_systemd_service
  install_nginx_config
  save_install_state
  start_services
  verify_installation
  log "Instalasi selesai."
}

main "$@"
