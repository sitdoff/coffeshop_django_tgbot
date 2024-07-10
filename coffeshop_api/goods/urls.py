from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"categories", views.CategoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("product/<int:pk>/", views.ProductView.as_view(), name="product"),
]
