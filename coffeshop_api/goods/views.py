from typing import Any

from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from .models import CategoryModel, ProductModel
from .serializers import CategorySerializer, ProductSerializer


# Create your views here.
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vewset for CategoryModel

    Readonly
    """

    queryset = CategoryModel.objects.filter()
    serializer_class = CategorySerializer

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Instead of displaying all categories, the root directory should be displayed.
        """
        object = get_object_or_404(self.queryset.model, parent=None)
        serializer = CategorySerializer(object, context={"request": self.request})
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    Vewset for ProductModel
    """

    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
