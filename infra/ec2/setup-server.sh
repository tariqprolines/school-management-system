#!/usr/bin/env bash
# One-time EC2 setup (Ubuntu 22.04+). Run as root or with sudo.
# Usage: sudo ./infra/ec2/setup-server.sh

set -euo pipefail

APP_ROOT="/var/www/html/school-management-system"

echo "==> Installing system packages"
apt-get update
apt-get install -y python3 python3-venv python3-pip nginx curl rsync

echo "==> Creating app directories"
mkdir -p "${APP_ROOT}/backend" "${APP_ROOT}/frontend"
chown -R ubuntu:ubuntu /var/www/html

echo "==> Enabling nginx"
systemctl enable nginx
systemctl start nginx

echo ""
echo "Done. Next steps:"
echo "1. Deploy code (push to main) or copy project to ${APP_ROOT}"
echo "2. Enable background services:"
echo "     sudo bash infra/ec2/enable-services.sh"
echo "3. Configure GitHub secrets/variables for CI/CD deploy"
echo "4. Optional HTTPS: sudo certbot --nginx -d your-domain.com"
echo ""
echo "Do NOT run uvicorn or npm run dev in a terminal for production."
echo "  Backend  → sms-api.service (systemd)"
echo "  Frontend → nginx serves frontend/dist (no Node process needed)"
