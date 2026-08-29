# EC2 Deployment (frontend + backend)

```
GitHub push to main
        │
        ▼
  GitHub Actions
   (test → deploy)
        │
        ▼
      EC2
  /var/www/html/school-management-system/
  ├── backend/   → FastAPI (systemd + uvicorn :8000)
  └── frontend/  → React source + dist/
                   nginx serves frontend/dist on :80
```

## Deploy paths on EC2

| Component | Path |
|-----------|------|
| Backend | `/var/www/html/school-management-system/backend` |
| Frontend source | `/var/www/html/school-management-system/frontend` |
| Frontend (browser) | `/var/www/html/school-management-system/frontend/dist` |

Legacy paths `/opt/sms` and `/var/www/sms` are removed on each deploy.

## 1. One-time EC2 setup

Ubuntu 22.04+, security group: **22** (SSH), **80/443** (HTTP/S).

```bash
sudo bash infra/ec2/setup-server.sh
```

Optional HTTPS after DNS points to the server:

```bash
sudo certbot --nginx -d your-domain.com
```

## 2. GitHub secrets

| Secret | Description |
|--------|-------------|
| `EC2_HOST` | EC2 public IP or hostname |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | Private SSH key (full PEM) |
| `DATABASE_URL` | `postgresql+asyncpg://USER:PASS@host:5432/sms_db` |
| `SECRET_KEY` | JWT secret (long random string) |
| `API_ACCESS_TOKEN` | API key (backend + frontend build) |

## 3. GitHub variables

| Variable | Example |
|----------|---------|
| `VITE_API_URL` | `http://YOUR_EC2_IP/api/v1` or `https://your-domain.com/api/v1` |
| `CORS_ORIGINS` | `http://YOUR_EC2_IP` or `https://your-domain.com` |

## 4. Workflow

| File | When | What |
|------|------|------|
| `deploy.yml` | Push to `main` | Test → sync to EC2 paths above |

Manual deploy: **Actions → Deploy → Run workflow**

## 5. Post-deploy checks

- [ ] `http://YOUR_EC2_IP/` loads the login page
- [ ] `http://YOUR_EC2_IP/health` returns `{"status":"healthy",...}`
- [ ] `frontend/src/pages/LoginPage.tsx` on EC2 matches GitHub `main`
- [ ] `CORS_ORIGINS` matches the URL users open in the browser
