from typing import Any

from cart.serializers import CartSerializer
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import OrderItemModel, OrderModel
from .order_factory import TelegramOrderFactory
from .serializers import OrderSerializer

# Create your views here.


# class OrderViewSet(ReadOnlyModelViewSet):
#     """
#     OrederModel viewset.
#     """
#
#     queryset = OrderModel.objects.all()
#     serializer_class = OrderSerializer
#
#     def get_queryset(self):
#         queryset = OrderModel.objects.filter(owner=self.request.user.pk)
#         return queryset


class OrderViewSet(ModelViewSet):
    """
    OrederModel viewset.
    """

    queryset = OrderModel.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = OrderModel.objects.filter(owner=self.request.user.pk)
        return queryset

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        cart_serializer = CartSerializer(data=request.data)
        if cart_serializer.is_valid():
            cart = cart_serializer.save()
            order_factory = TelegramOrderFactory()
            order = order_factory.create_order(request=request, cart=cart)
            return Response(data=OrderSerializer(order).data)
        # print(request.data)
        # print(cart.cart)
        # print(order)
