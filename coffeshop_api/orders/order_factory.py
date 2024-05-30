from abc import ABC, abstractmethod

from cart.cart import Cart
from django.conf import settings
from django.http import HttpRequest
from goods.models import ProductModel

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

    def create_order(self, request: HttpRequest, cart: Cart):
        """
        Creates and returns an order object.
        """
        if cart is None:
            raise Exception("Нет корзины")
        if self.check_cart(cart):
            order = OrderModel.objects.create(owner=request.user)
            items = self.get_items(cart)
            for item in items:
                order.items.add(item)
            return order

    def check_cart(self, cart: Cart):
        """
        Checks the presence of a cart in the session and the presence of goods in it.
        """
        if not "items" in cart.cart and not "ordered" in cart.cart:
            raise Exception("Нет корзины")
        if not cart.cart["ordered"]:
            raise Exception("Корзина пуста")
        return True

    def get_items(self, cart: Cart):
        """
        Returns ordered items objects from the cart to be attached to the order.

        At the end, clears the order cart.
        """
        items = []
        for item_data in cart:
            item = OrderItemModel.objects.create(
                order=None,
                product=ProductModel.objects.get(pk=item_data["product_id"]),
                price=item_data["price"],
                quantity=item_data["quantity"],
            )
            items.append(item)
        cart.clear()
        return items
