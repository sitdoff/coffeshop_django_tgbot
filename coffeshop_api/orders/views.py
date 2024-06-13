from typing import Any

from cart.serializers import CartSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import OrderModel
from .order_factory import TelegramOrderFactory
from .serializers import OrderSerializer


# Create your views here.
class OrderPagination(PageNumberPagination):
    """
    TODO
    """

    page_size = 5
    page_query_param = "page"


class OrderViewSet(ModelViewSet):
    """
    OrederModel viewset.
    """

    queryset = OrderModel.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "options"]
    pagination_class = OrderPagination

    def get_queryset(self):
        """
        TODO
        """
        queryset = OrderModel.objects.filter(owner=self.request.user.pk).prefetch_related("items")
        return queryset

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        TODO
        """
        cart_serializer = CartSerializer(data=request.data)
        if cart_serializer.is_valid():
            cart = cart_serializer.save()
            try:
                order_factory = TelegramOrderFactory()
                order = order_factory.create_order(request=request, cart=cart)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data=OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(cart_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
