from rest_framework import serializers

from .models import CategoryModel, ProductModel


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for ProductModel
    """

    class Meta:
        model = ProductModel
        fields = ["name", "category", "price"]


class SubCategorySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for a CategoryModel when it is displayed inside another category.
    """

    class Meta:
        model = CategoryModel
        fields = "__all__"


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for a CategoryModel
    """

    children = SubCategorySerializer(many=True, read_only=True)
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = CategoryModel
        fields = "__all__"
