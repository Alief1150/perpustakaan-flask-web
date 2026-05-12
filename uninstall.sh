#!/usr/bin/env bash
set -euo pipefail

APP_NAME="perpustakaan-flask-web"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_FILE="/etc/${APP_NAME}/install.env"
SERVICE_NAME="${APP_NAME}"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
NGINX_CONF="/etc/nginx/conf.d/${SERVICE_NAME}.conf"
VENV_DIR="${APP_DIR}/.venv"
ENV_FILE="${APP_DIR}/.env"
STATE_DIR="/etc/${APP_NAME}"

log() { printf '[uninstall] %s\n' "$*"; }
warn() { printf '[warn] %s\n' "$*" >&2; }
die() { printf '[error] %s\n' "$*" >&2; exit 1; }
require_root() { [[ ${EUID:-$(id -u)} -eq 0 ]] || die "Jalankan script ini dengan sudo/root."; }
load_state() {
  if [[ -f "${STATE_FILE}" ]]; then
    # shellcheck disable=SC1090
    source "${STATE_FILE}"
    APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
    VENV_DIR="${VENV_DIR:-${APP_DIR}/.venv}"
    ENV_FILE="${ENV_FILE:-${APP_DIR}/.env}"
    SERVICE_NAME="${SERVICE_NAME:-${APP_NAME}}"
    SERVICE_FILE="${SERVICE_FILE:-/etc/systemd/system/${SERVICE_NAME}.service}"
    NGINX_CONF="${NGINX_CONF:-/etc/nginx/conf.d/${SERVICE_NAME}.conf}"
  fi
}
remove_if_exists() {
  local target="$1"
  if [[ -e "$target" || -L "$target" ]]; then
    rm -rf "$target"
  fi
}
main() {
  require_root
  load_state

  log "Menghentikan service jika ada..."
  systemctl stop "${SERVICE_NAME}" >/dev/null 2>&1 || true
  systemctl disable "${SERVICE_NAME}" >/dev/null 2>&1 || true

  log "Menghapus file service systemd..."
  remove_if_exists "${SERVICE_FILE}"

  log "Menghapus konfigurasi nginx project..."
  remove_if_exists "${NGINX_CONF}"
  nginx -t >/dev/null 2>&1 || true
  systemctl reload nginx >/dev/null 2>&1 || true

  log "Menghapus environment file project..."
  remove_if_exists "${ENV_FILE}"

  log "Menghapus virtualenv project..."
  remove_if_exists "${VENV_DIR}"

  log "Menghapus seluruh folder project..."
  remove_if_exists "${APP_DIR}"

  log "Menghapus state install..."
  remove_if_exists "${STATE_DIR}"

  systemctl daemon-reload
  log "Uninstall selesai. Semua komponen project telah dihapus dari scope project saja."
}

main "$@"
