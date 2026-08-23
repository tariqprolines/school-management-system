#!/usr/bin/env bash
# One-time EC2 setup (Ubuntu 22.04+). Run as root or with sudo.
# Usage: sudo ./infra/ec2/setup-server.sh

set -euo pipefail

echo "==> Installing system packages"
apt-get update
apt-get install -y python3 python3-venv python3-pip nginx curl

echo "==> Creating app directory"
mkdir -p /opt/sms
chown -R ubuntu:ubuntu /opt/sms

echo "==> Enabling nginx"
systemctl enable nginx
systemctl start nginx

echo ""
echo "Done. Next steps:"
echo "1. Point api.yourschool.com DNS to this EC2 public IP"
echo "2. Copy infra/ec2/nginx-api.conf to /etc/nginx/sites-enabled/ and reload nginx"
echo "3. Install certbot for HTTPS: sudo certbot --nginx -d api.yourschool.com"
echo "4. Configure GitHub secrets (EC2_HOST, EC2_SSH_KEY, DATABASE_URL, etc.)"
echo "5. Push to main branch to deploy via GitHub Actions"
