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
echo "1. Point your domain DNS to this EC2 public IP"
echo "2. Configure GitHub secrets (EC2_HOST, EC2_USER, EC2_SSH_KEY, DATABASE_URL, SECRET_KEY, API_ACCESS_TOKEN)"
echo "3. Set GitHub variables VITE_API_URL (e.g. http://YOUR_IP/api/v1) and CORS_ORIGINS"
echo "4. Push to main — deploy.yml syncs to ${APP_ROOT}/backend and ${APP_ROOT}/frontend"
echo "5. Optional HTTPS: sudo certbot --nginx -d your-domain.com"
