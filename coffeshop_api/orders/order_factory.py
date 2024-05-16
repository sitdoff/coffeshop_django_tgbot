from abc import ABC, abstractmethod

from cart.cart import Cart
from django.conf import settings
from django.http import HttpRequest

from .models import OrderItemModel, OrderModel


class OrderFactory(ABC):

    @abstractmethod
    def create_order(self):
        pass

    @abstractmethod
    def check_cart(self):
        pass

    @abstractmethod
    def get_items(self):
        pass


class TelegramOrderFactory(OrderFactory):

    def create_order(self, request: HttpRequest):
        if self.check_cart(request):
            order = OrderModel.objects.create(owner=request.user)
            items = self.get_items(request)
            for item in items:
                order.items.add(item)
            return order

    def check_cart(self, request: HttpRequest):
        if settings.CART_SESSION_ID not in request.session:
            raise Exception("Нет корзины")
        if len(request.session[settings.CART_SESSION_ID]) == 0:
            raise Exception("Корзина пуста")
        return True

    def get_items(self, request):
        cart = Cart(request)
        items = []
        for item_data in cart:
            item = OrderItemModel.objects.create(
                order=None,
                product=item_data["product"],
                price=item_data["price"],
                quantity=item_data["quantity"],
            )
            items.append(item)
        cart.clear()
        return items
