from decimal import Decimal


class Cart:
    """
    Shopping cart for managing ordered goods.
    """

    def __init__(self, data=None) -> None:
        if data is None:
            self.cart = {"items": {}, "ordered": set()}
        else:
            self.cart = data["cart"]
            self.cart["ordered"] = set(self.cart["items"])

    def add(self, product, quantity: int = 1, override_quantity: bool = False) -> None:
        """
        Add the product to the cart in the specified quantity.

        If the parameter "override_quantity" is True, then replace the initial quantity with the specified one. Otherwise, add.

        If the "override_quantity" parameter is True and the "quantity" value is 0, then the product is removed from the cart.
        """

        if quantity < 0:
            raise ValueError("Quantity cannot be less than 0")

        if product.id not in self.cart["ordered"] and quantity == 0:
            raise ValueError("The product is not in the cart. A value of 0 cannot be applied.")

        if product.id not in self.cart["ordered"]:
            self.cart["items"][product.id] = {
                "product_id": product.id,
                "product_name": product.name,
                "price": Decimal(product.price),
                "quantity": 0,
            }

            # Add item id in ordered set
            self.cart["ordered"].add(product.id)

        # Set product quantity
        if override_quantity:
            if quantity == 0:
                self.remove(product)
                return
            self.cart["items"][product.id]["quantity"] = quantity
        else:
            self.cart["items"][product.id]["quantity"] += quantity

        # Set product cost
        self.cart["items"][product.id]["cost"] = Decimal(
            self.cart["items"][product.id]["price"] * self.cart["items"][product.id]["quantity"]
        )

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
        self.__init__(data=None)
