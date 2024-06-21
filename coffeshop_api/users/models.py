from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class TelegramUser(AbstractUser):
    """
    Standard user model with additional field telegram_id.
    """

    telegram_id = models.CharField(max_length=15, unique=True, verbose_name="Telegram ID")
