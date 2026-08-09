import pytest
from httpx import ASGITransport, AsyncClient

from app.config.database import Base, async_session, engine
from app.config.settings import settings
from app.main import app as fastapi_app
from app.services.seed_service import SeedService
import app.models  # noqa: F401

API_KEY = settings.API_ACCESS_TOKEN
HEADERS = {"X-Access-Token": API_KEY}


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as db:
        await SeedService.seed_all(db)
    yield
    await engine.dispose()


@pytest.fixture
async def client():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post(
        "/api/v1/users/login",
        json={"email": "admin@school.com", "password": "admin123"},
        headers=HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post(
        "/api/v1/users/login",
        json={"email": "admin@school.com", "password": "wrongpassword"},
        headers=HEADERS,
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dashboard_requires_auth(client):
    response = await client.get("/api/v1/dashboard/summary", headers=HEADERS)
    assert response.status_code == 401
