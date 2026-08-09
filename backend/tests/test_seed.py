import pytest
from httpx import ASGITransport, AsyncClient

from app.config.database import Base, async_session, engine
from app.config.settings import settings
from app.main import app as fastapi_app
from app.services.seed_service import SeedService
import app.models  # noqa: F401

HEADERS = {"X-Access-Token": settings.API_ACCESS_TOKEN}

DEMO_ACCOUNTS = [
    ("admin@school.com", "admin123", "super_admin"),
    ("principal@school.com", "demo123", "admin"),
    ("teacher@school.com", "demo123", "teacher"),
    ("finance@school.com", "demo123", "accountant"),
    ("parent@school.com", "demo123", "parent"),
    ("student@school.com", "demo123", "student"),
]


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
@pytest.mark.parametrize("email,password,expected_role", DEMO_ACCOUNTS)
async def test_demo_role_login(client, email, password, expected_role):
    response = await client.post(
        "/api/v1/users/login",
        json={"email": email, "password": password},
        headers=HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["user"]["role"] == expected_role


@pytest.mark.asyncio
async def test_teacher_profile_exists_after_seed(client):
    login = await client.post(
        "/api/v1/users/login",
        json={"email": "teacher@school.com", "password": "demo123"},
        headers=HEADERS,
    )
    token = login.json()["data"]["access_token"]
    response = await client.get(
        "/api/v1/teachers/me",
        headers={**HEADERS, "Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "teacher@school.com"
