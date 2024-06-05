from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import OrderItemModel, OrderModel


class OrderItemListSerializer(serializers.ListSerializer):
    """
    Serializer to create a list OrderItemModel.
    """

    cost = serializers.DecimalField(source="get_cost", max_digits=5, decimal_places=2, read_only=True)

    def create(self, validated_data):
        items = [OrderItemModel(**data) for data in validated_data]
        return OrderItemModel.objects.bulk_create(items)


class OrderItemSerializer(ModelSerializer):
    """
    OrderItemModel serializer.
    """

    cost = serializers.DecimalField(source="get_cost", max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItemModel
        fields = "__all__"
        list_serializer_class = OrderItemListSerializer


class OrderSerializer(ModelSerializer):
    """
    OrderModel serializer.
    """

    items = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(source="get_total_cost", max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = OrderModel
        fields = "__all__"
