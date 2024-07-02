import json

from django.contrib.auth import get_user_model
from django.core.exceptions import BadRequest
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from .backends import TelegramIdBackend
from .models import TelegramUser
from .serializers import CreateTelegramUserSerializer, TelegramUserSerializer


# Create your tests here.
class TestTelegramIdBackend(TestCase):
    """
    Test the user authentication backend using Telegram ID.
    """

    def setUp(self):
        self.backend = TelegramIdBackend()
        self.telegram_id = 1234567
        self.user = get_user_model().objects.create(username="test_user", telegram_id=self.telegram_id)

    def test_authenticate_with_valid_data(self):
        """
        Test the authentication method with the correct data.
        """
        request = HttpRequest()
        user = self.backend.authenticate(request, telegram_id=self.telegram_id)
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_authenticate_with_invalid_telegram_id(self):
        """
        Test the authentication method with the wrong Telegram ID.
        """
        request = HttpRequest()
        user = self.backend.authenticate(request, telegram_id=111111)
        self.assertIsNone(user)

    def test_authenticate_without_telegram_id(self):
        """
        Test the authentication method without Telegram ID.
        """
        request = HttpRequest()
        user = self.backend.authenticate(request)
        self.assertIsNone(user)

    def test_get_user_with_valid_user_id(self):
        """
        Test getting a user using a valid user ID.
        """
        user = self.backend.get_user(self.user.pk)
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_get_user_with_invalid_user_id(self):
        """
        Test getting a user using an invalid user ID.
        """
        user = self.backend.get_user(999999)
        self.assertIsNone(user)


class TestTelegraUserSerializer(TestCase):
    """
    Test the user's serializer.
    """

    def setUp(self) -> None:
        self.user = TelegramUser.objects.create(username="Test user", email="test_user@mail.com", telegram_id="123456")
        self.user.set_password("password")
        self.serializer = TelegramUserSerializer(instance=self.user)
        return super().setUp()

    def test_user_serialization(self):
        """
        Test the user's serializer.
        """
        self.assertEqual(self.serializer.data["username"], self.user.username)
        self.assertEqual(self.serializer.data["email"], self.user.email)
        self.assertEqual(self.serializer.data["telegram_id"], self.user.telegram_id)
        self.assertEqual(self.serializer.data["is_active"], True)
        self.assertEqual(self.serializer.data["is_staff"], False)
        self.assertEqual(self.serializer.data["is_staff"], False)


class TestCreateTelegramUserSerializer(TestCase):
    """
    Test the serializer to create a user.
    """

    def test_with_valid_data(self):
        """
        Test serializer with valid data.
        """
        data = {
            "telegram_id": "123456",
            "username": "user",
        }
        serializer = CreateTelegramUserSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            self.assertEqual(user.username, data["username"])
            self.assertEqual(user.telegram_id, data["telegram_id"])

    def test_with_valid_data_when_user_already_exists(self):
        """
        Test serializer with valid data when user already exists.
        """
        data = {
            "telegram_id": "123456",
            "username": "user",
        }
        get_user_model().objects.create(**data)

        serializer = CreateTelegramUserSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            with self.assertRaises(BadRequest):
                user = serializer.save()

    def test_with_invalid_data(self):
        """
        Test serializer with invalid data.
        """
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


class TestCreateUserView(TestCase):
    """
    Test view for create user.
    """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_view_method_post_whith_valid_data(self):
        """
        Test POST method with valid data.
        """
        data = {
            "telegram_id": "12345",
            "username": "test_user_create_user_view",
        }
        reference = data

        with self.assertRaises(get_user_model().DoesNotExist):
            user = get_user_model().objects.get(telegram_id=data["telegram_id"], username=data["username"])

        response = self.client.post(reverse("create_user"), data=data)

        self.assertEqual(json.loads(response.content.decode()), reference)
        user = get_user_model().objects.get(telegram_id=data["telegram_id"], username=data["username"])
        self.assertIsNotNone(user)

    def test_view_method_post_whith_valid_data_when_user_already_exists(self):
        """
        Test POST method with valid data when user already exists.
        """
        data = {
            "telegram_id": "12345",
            "username": "test_user_create_user_view",
        }
        reference = {"error": "User with this Telegram ID already exists."}
        get_user_model().objects.create(**data)

        response = self.client.post(reverse("create_user"), data=data)
        self.assertEqual(response.json(), reference)

    def test_view_method_post_whith_invalid_data(self):
        """
        Test POST method with invalid data.
        """
        data = {
            "telegram_id": "12345",
        }
        reference = {"username": ["This field is required."]}
        response = self.client.post(reverse("create_user"), data=data)
        self.assertEqual(json.loads(response.content.decode()), reference)

        data = {
            "username": "test_user_create_user_view",
        }
        reference = {"telegram_id": ["This field is required."]}
        response = self.client.post(reverse("create_user"), data=data)
        self.assertEqual(json.loads(response.content.decode()), reference)

    def test_view_method_get(self):
        """
        Test GET method.
        """
        response = self.client.get(reverse("create_user"))
        reference = {"detail": 'Method "GET" not allowed.'}
        self.assertEqual(json.loads(response.content.decode()), reference)

    def test_view_method_put(self):
        """
        Test PUT method.
        """
        data = {}
        response = self.client.put(reverse("create_user"), data=data)
        reference = {"detail": 'Method "PUT" not allowed.'}
        self.assertEqual(json.loads(response.content.decode()), reference)

    def test_view_method_patch(self):
        """
        Test PATCH method.
        """
        data = {}
        response = self.client.patch(reverse("create_user"), data=data)
        reference = {"detail": 'Method "PATCH" not allowed.'}
        self.assertEqual(json.loads(response.content.decode()), reference)

    def test_view_method_delete(self):
        """
        Test DELETE method.
        """
        data = {}
        response = self.client.delete(reverse("create_user"), data=data)
        reference = {"detail": 'Method "DELETE" not allowed.'}
        self.assertEqual(json.loads(response.content.decode()), reference)
