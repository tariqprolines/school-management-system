#!/usr/bin/env bash
# Runs on EC2 via GitHub Actions SSH. Expects upload at /tmp/sms-staging/.
set -euo pipefail

STAGING="/tmp/sms-staging"
APP_ROOT="/var/www/html/school-management-system"
BACKEND_SRC="${STAGING}/backend"
BACKEND_DEST="${APP_ROOT}/backend"
FRONTEND_SRC="${STAGING}/frontend"
FRONTEND_DEST="${APP_ROOT}/frontend"
DEPLOY_USER="${SUDO_USER:-ubuntu}"

for path in "$BACKEND_SRC" "${FRONTEND_SRC}/dist/index.html" "${STAGING}/infra/ec2/sms-api.service"; do
  if [ ! -e "$path" ]; then
    echo "Missing upload: $path"
    find "$STAGING" -maxdepth 4 -type f 2>/dev/null | head -n 40 || true
    exit 1
  fi
done

sudo mkdir -p "$BACKEND_DEST" "$FRONTEND_DEST"
sudo rsync -a --delete --exclude venv --exclude .env --exclude __pycache__ "$BACKEND_SRC/" "$BACKEND_DEST/"
sudo rsync -a --delete --exclude node_modules --exclude .env --exclude '.env.*' "$FRONTEND_SRC/" "$FRONTEND_DEST/"
sudo chown -R "$DEPLOY_USER:$DEPLOY_USER" "$APP_ROOT"

# Restore frontend .env for local dev/rebuilds on EC2 (not used by nginx-served dist)
TOKEN="${API_ACCESS_TOKEN:-${VITE_API_ACCESS_TOKEN:-}}"
if [ -z "$TOKEN" ]; then
  echo "Missing API_ACCESS_TOKEN secret or VITE_API_ACCESS_TOKEN variable" >&2
  exit 1
fi
printf '%s\n' \
  "VITE_API_URL=${VITE_API_URL:-http://localhost/api/v1}" \
  "VITE_API_ACCESS_TOKEN=${TOKEN}" \
  > "${FRONTEND_DEST}/.env"
sudo chown "$DEPLOY_USER:$DEPLOY_USER" "${FRONTEND_DEST}/.env"

# Remove legacy deploy paths from the old CI/CD layout
sudo rm -rf /opt/sms /var/www/sms

cd "$BACKEND_DEST"

DB_URL="${DATABASE_URL:?DATABASE_URL is required}"
case "$DB_URL" in
  postgresql+asyncpg://*) ;;
  postgresql://*) DB_URL="postgresql+asyncpg://${DB_URL#postgresql://}" ;;
  postgres://*) DB_URL="postgresql+asyncpg://${DB_URL#postgres://}" ;;
esac

printf '%s\n' \
  "APP_NAME=School Management System" \
  "DEBUG=false" \
  "ALGORITHM=HS256" \
  "ACCESS_TOKEN_EXPIRE_MINUTES=120" \
  "DB_SCHEMA=public" \
  "DATABASE_URL=${DB_URL}" \
  "SECRET_KEY=${SECRET_KEY:?SECRET_KEY is required}" \
  "API_ACCESS_TOKEN=${TOKEN}" \
  "CORS_ORIGINS=${CORS_ORIGINS:-${VITE_API_URL%/api/v1}}" \
  > .env

if [ ! -x venv/bin/uvicorn ]; then
  python3 -m venv venv
fi
. venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

sudo cp "${STAGING}/infra/ec2/sms-api.service" /etc/systemd/system/sms-api.service
sudo systemctl stop school-management-system.service 2>/dev/null || true
sudo systemctl disable school-management-system.service 2>/dev/null || true
if [ -f "${STAGING}/infra/ec2/nginx.conf" ]; then
  sudo cp "${STAGING}/infra/ec2/nginx.conf" /etc/nginx/sites-available/sms
  sudo ln -sf /etc/nginx/sites-available/sms /etc/nginx/sites-enabled/sms
  sudo rm -f /etc/nginx/sites-enabled/default
fi

sudo systemctl daemon-reload
sudo systemctl enable sms-api nginx
sudo systemctl restart sms-api
sudo nginx -t
sudo systemctl reload nginx

for i in $(seq 1 20); do
  if curl -sf http://127.0.0.1:8000/health >/dev/null; then
    curl -sf http://127.0.0.1/health >/dev/null || { echo "nginx proxy to /health failed"; exit 1; }
    echo "Deploy complete"
    echo "  Backend:  ${BACKEND_DEST}"
    echo "  Frontend: ${FRONTEND_DEST} (nginx serves ${FRONTEND_DEST}/dist)"
    echo "  API URL:  ${VITE_API_URL:-not set}"
    exit 0
  fi
  echo "Waiting for API... ($i/20)"
  sleep 3
done

echo "API failed health check"
sudo systemctl status sms-api --no-pager || true
sudo journalctl -u sms-api -n 50 --no-pager || true
exit 1
