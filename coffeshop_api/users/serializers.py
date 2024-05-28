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
