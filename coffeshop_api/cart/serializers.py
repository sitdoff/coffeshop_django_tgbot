from rest_framework import serializers


class CartSerializer(serializers.Serializer):
    """
    Serializes the cart.
    """

    items = serializers.DictField(source="cart")
    total_price = serializers.DecimalField(source="get_total_price", max_digits=5, decimal_places=2)
