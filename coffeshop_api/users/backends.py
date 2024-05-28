from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.http import HttpRequest

User = get_user_model()


class TelegramIdBackend(BaseBackend):
    """
    Backend for user authorization using Telegram ID.
    """

    def authenticate(self, request: HttpRequest | None, telegram_id=None, **kwargs):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return None
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
