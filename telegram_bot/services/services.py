import aiohttp
import redis
from aiogram.types import Message


def set_auth_token(token: str, message: Message, redis_connection: redis.Redis) -> None:
    redis_connection.set(f"token:{message.from_user.id}", token)


def get_auth_token(message: Message, redis_connection: redis.Redis) -> str:
    return redis_connection.get(f"token:{message.from_user.id}")


async def authorize_user(message: Message, redis_connection: redis.Redis, session: aiohttp.ClientSession) -> str:
    token = get_auth_token(message, redis_connection)
    if not token:
        async with session.post(
            "http://web:8080/auth/telegram/",
            json={"telegram_id": message.from_user.id},
        ) as response:
            response_data = await response.json()
            token = response_data["token"]
            set_auth_token(token, message, redis_connection)
    return token
