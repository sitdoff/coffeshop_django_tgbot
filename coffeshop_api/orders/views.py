from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import OrderItemModel, OrderModel
from .order_factory import TelegramOrderFactory
from .serializers import OrderSerializer

# Create your views here.


class OrderViewSet(ReadOnlyModelViewSet):
    """
    OrederModel viewset.
    """

    queryset = OrderModel.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = OrderModel.objects.filter(owner=self.request.user.pk)
        return queryset
