from django.urls import include, path

from . import views

urlpatterns = [
    path("auth/telegram/", views.TelegramAuthView.as_view(), name="telegram_auth"),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
