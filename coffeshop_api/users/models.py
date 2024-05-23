from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class TelegramUser(AbstractUser):
    telegram_id = models.CharField(max_length=15, verbose_name="Telegram ID")
