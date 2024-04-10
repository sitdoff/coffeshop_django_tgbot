from django.shortcuts import render
from .models import CategoryModel, ProductModel
from rest_framework import viewsets
from .serializers import CategorySerializer, ProductSerializer


# Create your views here.
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CategoryModel.objects.filter()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer