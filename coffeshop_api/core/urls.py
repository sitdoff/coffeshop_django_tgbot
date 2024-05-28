"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

# from drf_yasg import openapi
# from drf_yasg.views import get_schema_view
from rest_framework import permissions

# schema_view = get_schema_view(
#     openapi.Info(
#         title="Snippets API",
#         default_version="v1",
#         description="Coffeshop",
#         terms_of_service="",
#         # contact="",
#         # license="",
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

urlpatterns = [
    # path("swagger/<format>/", schema_view.without_ui(cache_timeout=0), name="schema_json"),
    # path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema_swagger_ui"),
    # path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema_redoc"),
    path("admin/", admin.site.urls),
    path("", include("goods.urls")),
    path("cart/", include("cart.urls", namespace="cart")),
    path("order/", include("orders.urls")),
    path("users/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("api-auth/", include("rest_framework.urls")),
        path("__debug__/", include("debug_toolbar.urls")),
    ]
