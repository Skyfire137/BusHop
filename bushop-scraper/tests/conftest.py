import os

# Must be set before importing app — Settings() is instantiated at module level
# in app/config.py and will raise ValidationError if INTERNAL_API_KEY is missing.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("DATABASE_URL_SYNC", "postgresql+psycopg2://test:test@localhost/test")
os.environ.setdefault("INTERNAL_API_KEY", "test-api-key")

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
