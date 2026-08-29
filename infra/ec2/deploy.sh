#!/usr/bin/env bash
# Runs on EC2 via GitHub Actions SSH. Expects upload at /tmp/sms-staging/.
set -euo pipefail

STAGING="/tmp/sms-staging"
BACKEND_SRC="${STAGING}/backend"

resolve_frontend_src() {
  local candidate
  for candidate in \
    "${STAGING}/frontend/dist" \
    "${STAGING}/frontend" \
    "${STAGING}/dist"; do
    if [ -f "${candidate}/index.html" ]; then
      echo "$candidate"
      return 0
    fi
  done

  candidate="$(find "$STAGING" -type f -name index.html 2>/dev/null | head -n 1 || true)"
  if [ -n "$candidate" ]; then
    dirname "$candidate"
    return 0
  fi

  echo "Frontend build not found under ${STAGING}. Contents:" >&2
  find "$STAGING" -maxdepth 4 -type f 2>/dev/null | head -n 40 >&2 || true
  return 1
}

FRONTEND_SRC="$(resolve_frontend_src)" || exit 1

for path in "$BACKEND_SRC" "$FRONTEND_SRC" "${STAGING}/infra/ec2/sms-api.service"; do
  if [ ! -e "$path" ]; then
    echo "Missing upload: $path"
    exit 1
  fi
done

sudo mkdir -p /opt/sms /var/www/sms
sudo rsync -a --delete --exclude venv --exclude .env "$BACKEND_SRC/" /opt/sms/
sudo rsync -a --delete "$FRONTEND_SRC/" /var/www/sms/
DEPLOY_USER="${SUDO_USER:-ubuntu}"
sudo chown -R "$DEPLOY_USER:$DEPLOY_USER" /opt/sms /var/www/sms

cd /opt/sms

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
  "API_ACCESS_TOKEN=${API_ACCESS_TOKEN:?API_ACCESS_TOKEN is required}" \
  "CORS_ORIGINS=${CORS_ORIGINS:-http://localhost}" \
  > .env

python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

sudo cp "${STAGING}/infra/ec2/sms-api.service" /etc/systemd/system/sms-api.service
if [ -f "${STAGING}/infra/ec2/nginx.conf" ]; then
  sudo cp "${STAGING}/infra/ec2/nginx.conf" /etc/nginx/sites-available/sms
  sudo ln -sf /etc/nginx/sites-available/sms /etc/nginx/sites-enabled/sms
  sudo rm -f /etc/nginx/sites-enabled/default
fi

sudo systemctl daemon-reload
sudo systemctl enable sms-api
sudo systemctl restart sms-api
sudo nginx -t
sudo systemctl reload nginx

for i in $(seq 1 20); do
  if curl -sf http://127.0.0.1:8000/health >/dev/null; then
    echo "API healthy"
    exit 0
  fi
  echo "Waiting for API... ($i/20)"
  sleep 3
done

echo "API failed health check"
sudo systemctl status sms-api --no-pager || true
sudo journalctl -u sms-api -n 50 --no-pager || true
exit 1
