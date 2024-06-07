from typing import Any

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import TelegramUser


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = "__all__"


class TelegramAuthSerializer(serializers.Serializer):
    telegram_id = serializers.CharField()

    def validate(self, data):
        telegram_id = data.get("telegram_id")
        user = authenticate(telegram_id=telegram_id)
        if user is None:
            raise serializers.ValidationError("Invalid Telegram ID")
        data["user"] = user
        return data


class CreateTelegramUserSerializer(serializers.ModelSerializer):

    username = serializers.CharField(max_length=150, required=True)
    telegram_id = serializers.CharField(max_length=15, required=True)

    class Meta:
        model = TelegramUser
        fields = ["telegram_id", "username"]

    def create(self, validated_data: Any):
        user = TelegramUser.objects.create(**validated_data)
        return user
