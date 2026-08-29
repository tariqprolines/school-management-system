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
  ┌─────┴─────┐
  │   nginx   │  :80  → /var/www/sms (React)
  │           │  /api → uvicorn :8000 (FastAPI)
  └─────┬─────┘
        ▼
   PostgreSQL (RDS or local)
```

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

## 4. Workflows

| File | When | What |
|------|------|------|
| `deploy.yml` | Push to `main` | Test → SSH deploy to EC2 |

Manual deploy: **Actions → Deploy → Run workflow**

## 5. Post-deploy checks

- [ ] `http://YOUR_EC2_IP/` loads the login page
- [ ] `http://YOUR_EC2_IP/health` returns `{"status":"healthy",...}`
- [ ] `CORS_ORIGINS` matches the URL users open in the browser
- [ ] `VITE_API_URL` uses the same host with `/api/v1` path
