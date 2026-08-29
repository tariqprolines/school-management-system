# School Management System

Industry-grade School Management System (SMS) built with **React**, **FastAPI**, and **PostgreSQL**.

## Features (Phase 1 MVP)

- **Authentication & RBAC** — Super Admin, Admin, Teacher, Accountant roles
- **Admin Dashboard** — Enrollment stats, fee collection, class occupancy
- **Teacher Module** — CRUD, employee ID, department, subject assignments
- **Student Module** — Admissions, guardians, class enrollment
- **Classes & Sections** — Academic years, grades, class sections
- **Timetable** — Weekly schedule, conflict detection
- **Fee Management** — Categories, structures, invoices, collection, defaulters

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Redux Toolkit, Axios |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2 (async), Pydantic v2 |
| Database | PostgreSQL 15 |
| Auth | JWT + API Key (X-Access-Token) |

## Local Development

Run PostgreSQL 15 locally, then start the API and SPA.

**Access:** Frontend http://localhost:5173 · API http://localhost:8000 · Docs http://localhost:8000/docs

**Default login:** `admin@school.com` / `admin123`

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Start local PostgreSQL, then:
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Demo accounts (all roles)

Seeded automatically on backend startup. Password is `demo123` for all except Super Admin.

| Role | Email | Password | Portal |
|------|-------|----------|--------|
| Super Admin | admin@school.com | admin123 | Admin Portal |
| Administrator (Principal) | principal@school.com | demo123 | Admin Portal |
| Teacher | teacher@school.com | demo123 | Teacher Portal |
| Accountant | finance@school.com | demo123 | Finance Portal |
| Parent | parent@school.com | demo123 | Parent Portal |
| Student | student@school.com | demo123 | Student Portal |

The demo teacher has a linked teacher profile; the demo student has a linked student record and guardian (`parent@school.com`).

## API Overview

All endpoints are under `/api/v1` with envelope responses:

```json
{
  "status_code": 200,
  "status": "success",
  "message": "...",
  "data": {}
}
```

| Module | Endpoints |
|--------|-----------|
| Auth | `POST /users/login`, `GET /users/me` |
| Academic | `/academic/years`, `/academic/grades`, `/academic/class-sections` |
| Teachers | `/teachers`, `/teachers/{id}/subjects` |
| Students | `/students`, `/students/{id}/enroll`, `/students/{id}/guardians` |
| Timetable | `/timetable/slots`, `/timetable/check-conflicts` |
| Fees | `/fees/categories`, `/fees/structures`, `/fees/collect`, `/fees/defaulters` |
| Dashboard | `/dashboard/summary` |

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## CI/CD (GitHub Actions → EC2)

Both frontend and backend deploy to the same EC2 instance (nginx + systemd).

| Component | Target |
|-----------|--------|
| React + Vite | **EC2** `/var/www/sms` (nginx static) |
| FastAPI | **EC2** `/opt/sms` (systemd + uvicorn) |
| PostgreSQL | **RDS** or local Postgres |

| Workflow | File | Trigger |
|----------|------|---------|
| **Deploy** | `.github/workflows/deploy.yml` | Push to `main` (tests run before deploy) |

Setup guide: [infra/aws/README.md](infra/aws/README.md)

## Project Structure

```
school-management-system/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── controllers/   # API routes
│   │   ├── services/      # Business logic
│   │   ├── models/        # SQLAlchemy ORM
│   │   └── schemas/       # Pydantic DTOs
│   └── tests/
├── frontend/         # React application
│   └── src/
│       ├── pages/         # Route pages
│       ├── components/    # UI components
│       └── redux/         # State management
└── infra/            # AWS / EC2 deploy scripts
```

## Phase 2 (Planned)

Built-in Education CRM: admissions pipeline, inquiry tracking, parent portal.

## License

MIT
