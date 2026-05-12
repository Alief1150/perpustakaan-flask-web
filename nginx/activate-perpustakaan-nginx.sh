#!/usr/bin/env bash
set -euo pipefail

# Jalankan sebagai root:
#   sudo bash nginx/activate-perpustakaan-nginx.sh
#
# Script ini mengarahkan nginx ke Flask Perpustakaan PNJ di 127.0.0.1:8000
# dan mematikan default proxy ke localhost:3000 yang sebelumnya dipakai web lain.

NGINX_SITES_AVAILABLE=/etc/nginx/sites-available
NGINX_SITES_ENABLED=/etc/nginx/sites-enabled
TARGET_CONF="$NGINX_SITES_AVAILABLE/inventory"
BACKUP_CONF="$NGINX_SITES_AVAILABLE/inventory.bak.$(date +%Y%m%d-%H%M%S)"

if [[ $EUID -ne 0 ]]; then
  echo "Please run as root: sudo bash $0"
  exit 1
fi

if [[ -f "$TARGET_CONF" ]]; then
  cp "$TARGET_CONF" "$BACKUP_CONF"
  echo "Backup saved to: $BACKUP_CONF"
fi

cat > "$TARGET_CONF" <<'EOF'
upstream perpustakaan_pnj_app {
    server 127.0.0.1:8000;
}

server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass http://perpustakaan_pnj_app;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

if [[ -L "$NGINX_SITES_ENABLED/inventory" || -e "$NGINX_SITES_ENABLED/inventory" ]]; then
  rm -f "$NGINX_SITES_ENABLED/inventory"
fi
ln -sf "$TARGET_CONF" "$NGINX_SITES_ENABLED/inventory"

echo "Testing nginx config..."
nginx -t

echo "Reloading nginx..."
systemctl reload nginx

echo "Done. Test from another device: http://<IP_HOST>/ and http://<IP_HOST>:8000/"
