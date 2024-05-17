from abc import ABC, abstractmethod

from cart.cart import Cart
from django.conf import settings
from django.http import HttpRequest

from .models import OrderItemModel, OrderModel


class OrderFactory(ABC):
    """
    Abstract class for order factory.
    """

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
    """
    Class for creating orders from telegram.
    """

    def create_order(self, request: HttpRequest):
        """
        Creates and returns an order object.
        """
        if self.check_cart(request):
            order = OrderModel.objects.create(owner=request.user)
            items = self.get_items(request)
            for item in items:
                order.items.add(item)
            return order

    def check_cart(self, request: HttpRequest):
        """
        Checks the presence of a cart in the session and the presence of goods in it.
        """
        if settings.CART_SESSION_ID not in request.session:
            raise Exception("Нет корзины")
        if len(request.session[settings.CART_SESSION_ID]) == 0:
            raise Exception("Корзина пуста")
        return True

    def get_items(self, request):
        """
        Returns ordered items objects from the cart to be attached to the order.

        At the end, clears the order cart.
        """
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
