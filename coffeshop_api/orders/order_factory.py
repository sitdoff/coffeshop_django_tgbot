from abc import ABC, abstractmethod
from decimal import Decimal

from cart.cart import Cart
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import QuerySet
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

    def create_order(self, request: HttpRequest, cart: Cart) -> OrderModel | None:
        """
        Creates and returns an order object.

        At the end, clears the order cart.
        """
        if not isinstance(cart, Cart):
            raise ValueError("The cart argument is not an instance of Cart")

        self.check_cart(cart)

        with transaction.atomic():
            order = OrderModel.objects.create(owner=request.user)
            try:
                items = self.get_items(cart, order)
                OrderItemModel.objects.bulk_create(items)

                self.check_order(order, cart)

                cart.clear()
                return order
            except ValueError as e:
                order.delete()
                raise e

    def check_cart(self, cart: Cart) -> bool | None:
        """
        Checks the presence of a cart in the session and the presence of goods in it.
        """
        if cart.cart.get("items") is None or cart.cart.get("ordered") is None:
            raise ValueError("The cart is corrupted")
        if not cart.cart["ordered"]:
            raise ValueError("The cart is empty")
        return True

    def check_order(self, order: OrderModel, cart: Cart) -> bool | None:
        """
        Checks the order.
        """
        if order.get_total_cost() != cart.get_total_price():
            raise ValueError("The total order value and the total cart value do not match.")
        if len(order) != len(cart):
            raise ValueError("The number of items in the order does not match the number of items in the cart.")
        return True

    def get_items(self, cart: Cart, order: OrderModel) -> list[OrderItemModel]:
        """
        Returns ordered items objects from the cart to be attached to the order.
        """
        product_ids = [item["product_id"] for item in cart]
        products: QuerySet[ProductModel] = ProductModel.objects.filter(pk__in=product_ids)
        product_dict = {product.pk: product for product in products}

        items = []
        for item_data_from_cart in cart:
            product_id = item_data_from_cart["product_id"]
            product = product_dict.get(product_id)
            if not product:
                raise ObjectDoesNotExist(f"Product with id {product_id} does not exist.")
            if product.price != Decimal(item_data_from_cart["price"]):
                raise ValueError(f"Item {item_data_from_cart['product_name']} price is wrong!")
            item = OrderItemModel(
                order=order, product_id=product, price=product.price, quantity=item_data_from_cart["quantity"]
            )
            items.append(item)

        return items
