import pytest
from fakeredis.aioredis import FakeRedis
from models.cart import Cart


@pytest.fixture
def redis_connection():
    conn = FakeRedis()
    yield conn

@pytest.fixture
def user_id():
    yield "123456"
