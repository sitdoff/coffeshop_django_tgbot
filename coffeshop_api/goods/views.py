from django.shortcuts import render
from rest_framework import viewsets

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


class ProductViewSet(viewsets.ModelViewSet):
    """
    Vewset for ProductModel
    """

    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
