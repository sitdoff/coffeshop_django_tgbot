from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import TelegramUser


# Register your models here.
class TelegramUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Telegram ID", {"fields": ("telegram_id",)}),)


admin.site.register(TelegramUser, TelegramUserAdmin)
