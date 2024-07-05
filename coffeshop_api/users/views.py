from typing import Any

from django.contrib.auth import authenticate
from django.core.exceptions import BadRequest
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import CreateTelegramUserSerializer, TelegramAuthSerializer


# Create your views here.
class TelegramAuthView(generics.GenericAPIView):
    """
    Authenticates the user using the serializer.
    """

    serializer_class = TelegramAuthSerializer

    def post(self, request, *args, **kwargs):
        """
        Passes data to the serializer, gets a user token from it and returns it.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)


class CreateUserView(generics.CreateAPIView):
    """
    Creates a user using a serializer.
    """

    serializer_class = CreateTelegramUserSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Create User. If user already exists, returns 400.
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(telegram_id=serializer.validated_data["telegram_id"])
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)
