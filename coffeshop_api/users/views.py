from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
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
