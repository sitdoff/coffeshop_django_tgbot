from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import OrderItemModel, OrderModel


class OrderItemSerializer(ModelSerializer):
    """
    OrderItemModel serializer.
    """

    cost = serializers.DecimalField(source="get_cost", max_digits=5, decimal_places=2)

    class Meta:
        model = OrderItemModel
        fields = "__all__"


class OrderSerializer(ModelSerializer):
    """
    OrderModel serializer.
    """

    items = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(source="get_total_cost", max_digits=5, decimal_places=2)

    class Meta:
        model = OrderModel
        fields = "__all__"
