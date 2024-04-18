from django.urls import include, path

from . import views

app_name = "cart"
urlpatterns = [
    path("", views.CartView.as_view(), name="cart_view"),
]
