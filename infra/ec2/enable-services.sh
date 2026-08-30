#!/usr/bin/env bash
# Enable backend + frontend to run in background and start on boot.
# Run once on EC2: sudo bash infra/ec2/enable-services.sh
set -euo pipefail

APP_ROOT="/var/www/html/school-management-system"
REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "==> Stopping duplicate/old services (if any)"
systemctl stop school-management-system.service 2>/dev/null || true
systemctl disable school-management-system.service 2>/dev/null || true
rm -f /etc/systemd/system/school-management-system.service

echo "==> Installing nginx + API systemd units"
cp "${REPO_DIR}/infra/ec2/nginx.conf" /etc/nginx/sites-available/sms
ln -sf /etc/nginx/sites-available/sms /etc/nginx/sites-enabled/sms
rm -f /etc/nginx/sites-enabled/default

cp "${REPO_DIR}/infra/ec2/sms-api.service" /etc/systemd/system/sms-api.service

echo "==> Enabling services (start on boot, survive terminal close)"
systemctl daemon-reload
systemctl enable nginx
systemctl enable sms-api
systemctl restart sms-api
nginx -t
systemctl reload nginx

echo ""
echo "Done. Services:"
systemctl is-active nginx sms-api
echo ""
echo "Backend:  sms-api.service  (uvicorn on 127.0.0.1:8000)"
echo "Frontend: nginx            (serves ${APP_ROOT}/frontend/dist)"
echo ""
echo "Check:"
echo "  curl http://127.0.0.1/health"
echo "  curl http://127.0.0.1/"
echo ""
echo "Logs:"
echo "  sudo journalctl -u sms-api -f"
echo "  sudo tail -f /var/log/nginx/error.log"
