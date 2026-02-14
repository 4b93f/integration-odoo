import pytest
from unittest.mock import MagicMock
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from src.models.partner import Partner


@pytest.fixture(scope="session")
def test_engine():
    """Create an in-memory SQLite database for testing."""
    # Use SQLite in-memory database for tests - never touches your real PostgreSQL DB
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    return engine


@pytest.fixture(scope="function")
async def test_db(test_engine):
    """Create tables for each test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield test_engine
    
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
def mock_odoo_client():
    client = MagicMock()
    client.uid = 1
    client.db = "test_db"
    client.connect.return_value = True
    client.authenticate.return_value = 1
    return client


@pytest.fixture
def sample_partner_data():
    return {
        'id': 1,
        'name': 'Test Partner',
        'email': 'test@example.com',
        'phone': '+1234567890',
        'function': 'Developer',
        'active': True
    }


@pytest.fixture
def sample_partners_list(sample_partner_data):
    return [
        sample_partner_data,
        {
            'id': 2,
            'name': 'Another Partner',
            'email': 'another@example.com',
            'phone': None,
            'function': 'Manager',
            'active': True
        }
    ]
