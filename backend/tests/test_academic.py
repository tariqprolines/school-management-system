import pytest
from httpx import ASGITransport, AsyncClient

from app.config.database import Base, async_session, engine
from app.config.settings import settings
from app.main import app as fastapi_app
from app.services.seed_service import SeedService
import app.models  # noqa: F401

HEADERS = {"X-Access-Token": settings.API_ACCESS_TOKEN}


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as db:
        await SeedService.seed_all(db)
    yield
    await engine.dispose()


@pytest.fixture
async def admin_client():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/api/v1/users/login",
            json={"email": "admin@school.com", "password": "admin123"},
            headers=HEADERS,
        )
        token = login.json()["data"]["access_token"]
        client.headers.update({"Authorization": f"Bearer {token}"})
        yield client


@pytest.mark.asyncio
async def test_list_academic_years(admin_client):
    response = await admin_client.get("/api/v1/academic/years", headers=HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert isinstance(body["data"], list)


@pytest.mark.asyncio
async def test_create_duplicate_academic_year_returns_400(admin_client):
    payload = {
        "name": "2026-2027",
        "start_date": "2026-01-08",
        "end_date": "2027-04-09",
        "is_current": True,
    }
    first = await admin_client.post("/api/v1/academic/years", json=payload, headers=HEADERS)
    assert first.status_code in (200, 201, 400)

    second = await admin_client.post("/api/v1/academic/years", json=payload, headers=HEADERS)
    assert second.status_code == 400
    body = second.json()
    assert body["status"] == "error"
    assert "already exists" in body["message"].lower()
