from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .serializers import CreateTelegramUserSerializer, TelegramAuthSerializer


# Create your views here.
class TelegramAuthView(generics.GenericAPIView):
    serializer_class = TelegramAuthSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)


class CreateUserView(generics.CreateAPIView):
    serializer_class = CreateTelegramUserSerializer
