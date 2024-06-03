from rest_framework import serializers

from .cart import Cart


class CartSerializer(serializers.Serializer):
    """
    Serializes the cart.
    """

    items = serializers.DictField(source="cart.items")
    total_price = serializers.DecimalField(source="get_total_price", max_digits=5, decimal_places=2, read_only=True)

    def create(self, validated_data):
        return Cart(data=validated_data)
