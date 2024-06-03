import json
from decimal import Decimal

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase
from django.urls import reverse
from goods.models import CategoryModel, ProductModel
from rest_framework.test import APIClient, APIRequestFactory

from .cart import Cart
from .serializers import CartSerializer

# Create your tests here.


class TestCart(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = CategoryModel.objects.create(name="category")
        cls.product1 = ProductModel.objects.create(name="poduct1", category=cls.category, price=10.5)
        cls.product2 = ProductModel.objects.create(name="poduct2", category=cls.category, price=11.5)

    def setUp(self) -> None:
        super().setUp()

    def test_init_cart_without_data(self):
        """
        Test cart initiation.
        """

        cart = Cart()
        self.assertEqual(cart.cart, {"items": {}, "ordered": set()})

    def test_init_cart_with_data(self):
        # TODO надо сделать тест на создание корзины, когда передаются уже готовые данные
        pass

    def test_cart_add_product(self):
        """
        Test adding products to cart.
        """
        cart = Cart()

        with self.assertRaises(ValueError):
            cart.add(self.product1, quantity=0)
            cart.add(self.product1, quantity=-1)
        self.assertNotIn(self.product1.pk, cart.cart)
        self.assertFalse(cart.cart["items"])
        self.assertFalse(cart.cart["ordered"])

        cart.add(self.product1)
        self.assertIn(self.product1.pk, cart.cart["items"])
        self.assertEqual(cart.cart["items"][self.product1.pk]["product_id"], self.product1.pk)
        self.assertEqual(cart.cart["items"][self.product1.pk]["product_name"], self.product1.name)
        self.assertEqual(cart.cart["items"][self.product1.pk]["price"], self.product1.price)
        self.assertEqual(cart.cart["items"][self.product1.pk]["quantity"], 1)
        self.assertEqual(cart.cart["items"][self.product1.pk]["cost"], self.product1.price)
        self.assertEqual(cart.cart["ordered"], {self.product1.pk})

        old_quantity = cart.cart["items"][self.product1.pk]["quantity"]
        new_quantity = 2
        cart.add(self.product1, quantity=new_quantity)
        self.assertIn(self.product1.pk, cart.cart["items"])
        self.assertEqual(cart.cart["items"][self.product1.pk]["price"], self.product1.price)
        self.assertEqual(cart.cart["items"][self.product1.pk]["quantity"], old_quantity + new_quantity)
        self.assertEqual(
            cart.cart["items"][self.product1.pk]["cost"], self.product1.price * (old_quantity + new_quantity)
        )

        quantity = 2
        cart.add(self.product1, quantity=quantity, override_quantity=True)
        self.assertIn(self.product1.pk, cart.cart["items"])
        self.assertEqual(cart.cart["items"][self.product1.pk]["price"], self.product1.price)
        self.assertEqual(cart.cart["items"][self.product1.pk]["quantity"], quantity)
        self.assertEqual(cart.cart["items"][self.product1.pk]["cost"], self.product1.price * quantity)

        quantity = 2
        cart.add(self.product2, quantity=quantity)
        self.assertIn(self.product1.pk, cart.cart["items"])
        self.assertEqual(cart.cart["items"][self.product1.pk]["price"], self.product1.price)
        self.assertEqual(cart.cart["items"][self.product1.pk]["quantity"], quantity)
        self.assertEqual(cart.cart["items"][self.product1.pk]["cost"], self.product1.price * quantity)
        self.assertIn(self.product2.pk, cart.cart["items"])
        self.assertEqual(cart.cart["items"][self.product2.pk]["price"], self.product2.price)
        self.assertEqual(cart.cart["items"][self.product2.pk]["quantity"], quantity)
        self.assertEqual(cart.cart["items"][self.product2.pk]["cost"], self.product2.price * quantity)
        self.assertEqual(cart.cart["ordered"], {self.product1.pk, self.product2.pk})

    def test_cart_remove_product(self):
        """
        Test the removal of products from the cart.
        """
        cart = Cart()
        cart.add(self.product1, quantity=1)
        cart.add(self.product2, quantity=2)

        cart.remove(self.product1)
        self.assertNotIn(self.product1.pk, cart.cart["items"])
        self.assertEqual(
            cart.cart,
            {
                "items": {
                    2: {"cost": 23.0, "price": 11.5, "product_id": 2, "product_name": "poduct2", "quantity": 2},
                },
                "ordered": {2},
            },
        )

        cart.remove(self.product2)
        self.assertEqual(cart.cart, {"items": {}, "ordered": set()})

    def test_cart_iter(self):
        """
        Test cart iteration.
        """
        cart = Cart()
        cart.add(self.product1, quantity=1)
        cart.add(self.product2, quantity=2)
        product_list = list(cart.__iter__())
        reference = [
            {
                "quantity": 1,
                "price": Decimal(self.product1.price),
                "product_id": self.product1.pk,
                "product_name": self.product1.name,
                "cost": Decimal(self.product1.price) * 1,
            },
            {
                "quantity": 2,
                "price": Decimal(self.product2.price),
                "product_id": self.product2.pk,
                "product_name": self.product2.name,
                "cost": Decimal(self.product2.price) * 2,
            },
        ]
        self.assertEqual(product_list, reference)

    def test_cart_len(self):
        """
        Test getting cart size.
        """
        cart = Cart()
        self.assertEqual(len(cart), 0)

        cart.add(self.product1, quantity=1)
        cart.add(self.product2, quantity=2)
        self.assertEqual(len(cart), 3)

        cart.add(self.product1, quantity=1)
        self.assertEqual(len(cart), 4)

    def test_cart_get_total_price(self):
        """
        Test getting the total cart value.
        """
        cart = Cart()
        self.assertEqual(cart.get_total_price(), 0)

        cart.add(self.product1, quantity=1)
        self.assertEqual(cart.get_total_price(), Decimal(self.product1.price) * 1)

        cart.add(self.product2, quantity=2)
        self.assertEqual(cart.get_total_price(), Decimal(self.product1.price) * 1 + Decimal(self.product2.price) * 2)

    def test_cart_clear(self):
        """
        Test emptying the cart.
        """
        cart = Cart()
        cart.add(self.product1, quantity=1)
        cart.add(self.product2, quantity=2)
        cart.clear()

        self.assertEqual(cart.cart, {"items": {}, "ordered": set()})


class TestCartSerializer(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = CategoryModel.objects.create(name="category")
        cls.product1 = ProductModel.objects.create(name="poduct1", category=cls.category, price=10.5)
        cls.product2 = ProductModel.objects.create(name="poduct2", category=cls.category, price=11.5)

    def setUp(self) -> None:
        super().setUp()
        self.request_factory = APIRequestFactory()
        request_factory = APIRequestFactory()
        self.request = request_factory.get("/cart/")
        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(self.request)
        self.request.session.save()

    def test_cart_serialization(self):
        """
        Test cart serialization.
        """
        cart = Cart()
        serializer = CartSerializer(cart)
        reference = {
            "items": {},
            "total_price": "0.00",
        }
        self.assertEqual(serializer.data, reference)

        product1_quantity = 1
        cart.add(self.product1, quantity=product1_quantity)
        product2_quantity = 2
        cart.add(self.product2, quantity=product2_quantity)
        serializer = CartSerializer(cart)
        reference = {
            "items": {
                str(self.product1.pk): {
                    "quantity": product1_quantity,
                    "price": self.product1.price,
                    "product_name": self.product1.name,
                    "product_id": self.product1.pk,
                    "cost": self.product1.price * product1_quantity,
                },
                str(self.product2.pk): {
                    "quantity": product2_quantity,
                    "price": self.product2.price,
                    "product_name": self.product2.name,
                    "product_id": self.product2.pk,
                    "cost": self.product2.price * product2_quantity,
                },
            },
            "total_price": "33.50",
        }
        self.assertEqual(serializer.data, reference)
