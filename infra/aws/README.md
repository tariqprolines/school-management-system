# Simple AWS Deployment

```
GitHub → git push → GitHub Actions
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
     React + Vite               FastAPI
            │                         │
            ▼                         ▼
    S3 + CloudFront              EC2 (systemd)
                                       │
                                       ▼
                               PostgreSQL RDS
```

## 1. AWS resources

### RDS PostgreSQL
- Engine: PostgreSQL 15
- Database: `sms_db`
- Note the endpoint and credentials

Connection string for GitHub secret `DATABASE_URL`:
```
postgresql+asyncpg://USER:PASSWORD@your-rds.xxx.rds.amazonaws.com:5432/sms_db
```

### EC2 (backend)
- Ubuntu 22.04, `t3.small` or larger
- Security group: allow **22** (SSH), **80/443** (nginx), restrict **8000** to localhost only
- Elastic IP recommended
- Run one-time setup:
  ```bash
  sudo bash infra/ec2/setup-server.sh
  ```
- Configure nginx with `infra/ec2/nginx-api.conf` for `api.yourschool.com`

### S3 + CloudFront (frontend)
1. Create S3 bucket (e.g. `sms-frontend-prod`)
2. Enable static website hosting OR use CloudFront OAC
3. Create CloudFront distribution:
   - Origin: S3 bucket
   - Default root object: `index.html`
   - Custom error response: 403/404 → `/index.html` (SPA routing)
4. Point `school.yourschool.com` CNAME to CloudFront

## 2. GitHub configuration

### Secrets (Settings → Secrets → Actions)

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user for S3 + CloudFront |
| `AWS_SECRET_ACCESS_KEY` | IAM secret |
| `EC2_HOST` | EC2 public IP or hostname |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | Private SSH key (full PEM contents) |
| `DATABASE_URL` | RDS connection string |
| `SECRET_KEY` | JWT secret (long random string) |
| `API_ACCESS_TOKEN` | API key (backend + Vite build) |

### Variables (Settings → Variables → Actions)

| Variable | Example |
|----------|---------|
| `AWS_REGION` | `ap-south-1` |
| `S3_BUCKET` | `sms-frontend-prod` |
| `CLOUDFRONT_DISTRIBUTION_ID` | `E1234567890ABC` |
| `VITE_API_URL` | `https://api.yourschool.com/api/v1` |
| `CORS_ORIGINS` | `https://school.yourschool.com` |

### IAM permissions (deploy user)
- `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket` on frontend bucket
- `cloudfront:CreateInvalidation` on distribution

## 3. Workflows

| File | Trigger | What it does |
|------|---------|--------------|
| `.github/workflows/ci.yml` | PR / push | Tests + build verify |
| `.github/workflows/deploy.yml` | Push to `main` | S3 sync + EC2 SSH deploy |

### Manual deploy
**Actions → Deploy to AWS → Run workflow**

## 4. Local development

```bash
# Backend
cd backend && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && cp .env.example .env
npm run dev
```

## 5. Post-deploy checklist

- [ ] `https://api.yourschool.com/health` returns 200
- [ ] `https://school.yourschool.com` loads login page
- [ ] `CORS_ORIGINS` matches CloudFront domain
- [ ] RDS security group allows EC2 only
- [ ] HTTPS on both domains (certbot / ACM)
