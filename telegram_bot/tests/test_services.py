from unittest.mock import AsyncMock, MagicMock, patch



@pytest.fixture
def redis_connection(request):
    connect = FakeRedis(decode_responses=True)
    return connect


@pytest.fixture
def api_url(request):
    return "http://example.com"


@pytest.fixture
def message(request):
    user_mock = MagicMock(spec=User)
    user_mock.id = 555555

    message_mock = MagicMock(spec=Message)
    message_mock.from_user = user_mock

    return message_mock

