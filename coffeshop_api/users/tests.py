from django.test import TestCase

from .models import TelegramUser
from .serializers import TelegramUserSerializer


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
