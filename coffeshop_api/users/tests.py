from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .models import TelegramUser
from .serializers import CreateTelegramUserSerializer, TelegramUserSerializer


# Create your tests here.
class TestTelegraUserSerializer(TestCase):
    def setUp(self) -> None:
        self.user = TelegramUser.objects.create(username="Test user", email="test_user@mail.com", telegram_id="123456")
        self.user.set_password("password")
        self.serializer = TelegramUserSerializer(instance=self.user)
        return super().setUp()

    def test_user_serialization(self):
        self.assertEqual(self.serializer.data["username"], self.user.username)
        self.assertEqual(self.serializer.data["email"], self.user.email)
        self.assertEqual(self.serializer.data["telegram_id"], self.user.telegram_id)
        self.assertEqual(self.serializer.data["is_active"], True)
        self.assertEqual(self.serializer.data["is_staff"], False)
        self.assertEqual(self.serializer.data["is_staff"], False)


class TestCreateTelegramUserSerializer(TestCase):
    def test_with_valid_data(self):
        data = {
            "telegram_id": "123456",
            "username": "user",
        }
        serializer = CreateTelegramUserSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            self.assertEqual(user.username, data["username"])
            self.assertEqual(user.telegram_id, data["telegram_id"])

    def test_with_invalid_data(self):
        data = {
            "telegram_id": "123456",
        }
        serializer = CreateTelegramUserSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()

        data = {
            "username": "user",
        }
        serializer = CreateTelegramUserSerializer(data=data)
        with self.assertRaises(ValidationError):
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
