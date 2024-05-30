from decimal import Decimal

# from django.conf import settings
# from django.http import HttpRequest
# from goods.models import ProductModel

# class Cart:
#     """
#     Shopping cart for managing ordered goods.
#     """
#
#     def __init__(self, request: HttpRequest) -> None:
#         self.session = request.session
#         cart = self.session.get(settings.CART_SESSION_ID)
#         if not cart:
#             cart = self.session[settings.CART_SESSION_ID] = {}
#         self.cart = cart
#
#     def save(self) -> None:
#         """
#         Mark session as "modified" to ensure its preservation.
#
#         This tells Django that the session has changed and needs to be saved.
#         """
#         self.session.modified = True
#
#     def add(self, product: ProductModel, quantity: int = 1, override_quantity: bool = False) -> None:
#         """
#         Add the product to the cart in the specified quantity.
#
#         If the parameter "override_quantity" is True, then replace the initial quantity with the specified one. Otherwise, add.
#
#         If the "override_quantity" parameter is True and the "quantity" value is 0, then the product is removed from the cart.
#         """
#         if quantity < 0:
#             raise ValueError("Quantity cannot be less than 0")
#
#         product_id = str(product.pk)
#         if product_id not in self.cart:
#             self.cart[product_id] = {"quantity": 0, "price": str(product.price), "product_name": product.name}
#
#         if override_quantity:
#             if quantity == 0:
#                 self.remove(product)
#                 self.save()
#                 return
#
#             self.cart[product_id]["quantity"] = quantity
#         else:
#             self.cart[product_id]["quantity"] += quantity
#
#         self.save()
#
#     def remove(self, product: ProductModel) -> None:
#         """
#         Remove product from the cart.
#         """
#         product_id = str(product.pk)
#         if product_id in self.cart:
#             del self.cart[product_id]
#             self.save()
#
#     def __iter__(self):
#         """
#         Loop through the shopping cart items and get products from the database.
#         """
#         product_ids = self.cart.keys()
#         products = ProductModel.objects.filter(pk__in=product_ids)
#         cart = self.cart.copy()
#         for product in products:
#             cart[str(product.pk)]["product"] = product
#         for item in cart.values():
#             item["price"] = Decimal(item["price"])
#             item["total_price"] = item["price"] * item["quantity"]
#             yield item
#
#     def __len__(self):
#         """
#         Count the number of items in the cart.
#         """
#         return sum(item["quantity"] for item in self.cart.values())
#
#     def get_total_price(self):
#         return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())
#
#     def clear(self):
#         """
#         Remove cart from session.
#         """
#         del self.session[settings.CART_SESSION_ID]
#         self.save()


class Cart:
    """
    Shopping cart for managing ordered goods.
    """

    def __init__(self, data=None) -> None:
        if data is None:
            self.cart = {"items": {}, "ordered": set()}
        else:
            print("Data")
            __import__("pprint").pprint(data)
            self.cart = data["cart"]

    def add(self, product, quantity: int = 1, override_quantity: bool = False) -> None:
        """
        Add the product to the cart in the specified quantity.

        If the parameter "override_quantity" is True, then replace the initial quantity with the specified one. Otherwise, add.

        If the "override_quantity" parameter is True and the "quantity" value is 0, then the product is removed from the cart.
        """
        if quantity < 0:
            raise ValueError("Quantity cannot be less than 0")

        if product.id not in self.cart["ordered"]:
            self.cart["items"][product.id] = {
                "product_id": product.id,
                "product_name": product.name,
                "price": product.price,
                "quantity": 0,
                "cost": quantity * product.price,
            }
            self.cart["ordered"].add(product.id)

        if override_quantity:
            if quantity == 0:
                self.remove(product)
                return
            self.cart["items"][product.id]["quantity"] = quantity
        else:
            self.cart["items"][product.id]["quantity"] += quantity

    def remove(self, product) -> None:
        """
        Remove product from the cart.
        """
        product_id = product.id
        if product_id in self.cart["ordered"] and product_id in self.cart["items"]:
            del self.cart["items"][product_id]
            self.cart["ordered"].remove(product_id)

    def __iter__(self):
        """ """
        for item in self.cart["items"].values():
            yield item

    def __len__(self):
        """
        Count the number of items in the cart.
        """
        return sum(item["quantity"] for item in self.cart["items"].values())

    def get_total_price(self):
        return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart["items"].values())

    def clear(self):
        """
        Remove cart from session.
        """
        self.cart = {"items": {}, "ordered": set()}
