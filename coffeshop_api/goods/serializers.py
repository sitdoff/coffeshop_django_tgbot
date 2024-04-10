from .models import CategoryModel, ProductModel
from rest_framework import serializers

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProductModel
        fields = ["name", "category", "price"]

class SubCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CategoryModel
        fields = "__all__"

class CategorySerializer(serializers.HyperlinkedModelSerializer):
    children = SubCategorySerializer(many=True, read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = CategoryModel
        fields = "__all__"
