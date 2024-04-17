from decimal import Decimal

from django.conf import settings
from django.http import HttpRequest
from goods.models import ProductModel


class Cart:
    """
    Shopping cart for managing ordered goods.
    """

    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def save(self) -> None:
        """
        Mark session as "modified" to ensure its preservation.

        This tells Django that the session has changed and needs to be saved.
        """
        self.session.modified = True

    def add(self, product: ProductModel, quantity: int = 1, override_quantity: bool = False) -> None:
        """
        Add the product to the cart in the specified quantity.

        If the parameter "override_quantity" is True, then replace the initial quantity with the specified one. Otherwise, add.
        """
        if quantity <= 0:
            raise ValueError("Quantity cannot be less than 1")
        product_id = str(product.pk)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price), "product_name": product.name}
        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.save()

    def remove(self, product: ProductModel) -> None:
        """
        Remove product from the cart.
        """
        product_id = str(product.pk)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Loop through the shopping cart items and get products from the database.
        """
        product_ids = self.cart.keys()
        products = ProductModel.objects.filter(pk__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.pk)]["product"] = product
        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        """
        Count the number of items in the cart.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())

    def clear(self):
        """
        Remove cart from session.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
