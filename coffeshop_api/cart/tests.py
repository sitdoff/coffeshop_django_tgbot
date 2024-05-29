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
        self.request_factory = APIRequestFactory()
        request_factory = APIRequestFactory()
        self.request = request_factory.get("/cart/")
        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(self.request)
        self.request.session.save()

    def test_init_cart(self):
        """
        Test cart initiation.
        """
        self.assertNotIn("cart", self.request.session)

        cart = Cart(self.request)
        self.assertEqual(cart.session, self.request.session)
        self.assertEqual(cart.cart, self.request.session["cart"])
        self.assertIn("cart", self.request.session)

    def test_cart_add_product(self):
        """
        Test adding products to cart.
        """
        cart = Cart(self.request)

        with self.assertRaises(ValueError):
            cart.add(self.product1, quantity=0)
            cart.add(self.product1, quantity=-1)
        self.assertNotIn(self.product1.pk, cart.cart)

        cart.add(self.product1)
        product1_pk_str = str(self.product1.pk)
        self.assertEqual(cart.cart, self.request.session["cart"])
        self.assertIn(product1_pk_str, cart.cart)
        self.assertEqual(cart.cart[product1_pk_str]["price"], str(self.product1.price))
        self.assertEqual(cart.cart[product1_pk_str]["quantity"], 1)

        cart.add(self.product1, quantity=2)
        product1_pk_str = str(self.product1.pk)
        self.assertEqual(cart.cart, self.request.session["cart"])
        self.assertIn(product1_pk_str, cart.cart)
        self.assertEqual(cart.cart[product1_pk_str]["price"], str(self.product1.price))
        self.assertEqual(cart.cart[product1_pk_str]["quantity"], 3)

        cart.add(self.product1, quantity=2, override_quantity=True)
        product1_pk_str = str(self.product1.pk)
        self.assertEqual(cart.cart, self.request.session["cart"])
        self.assertIn(product1_pk_str, cart.cart)
        self.assertEqual(cart.cart[product1_pk_str]["price"], str(self.product1.price))
        self.assertEqual(cart.cart[product1_pk_str]["quantity"], 2)

        cart.add(self.product2, quantity=2)
        product1_pk_str = str(self.product1.pk)
        product2_pk_str = str(self.product2.pk)
        self.assertEqual(cart.cart, self.request.session["cart"])
        self.assertIn(product1_pk_str, cart.cart)
        self.assertEqual(cart.cart[product1_pk_str]["price"], str(self.product1.price))
        self.assertEqual(cart.cart[product1_pk_str]["quantity"], 2)
        self.assertIn(product2_pk_str, cart.cart)
        self.assertEqual(cart.cart[product2_pk_str]["price"], str(self.product2.price))
        self.assertEqual(cart.cart[product1_pk_str]["quantity"], 2)

    def test_cart_remove_product(self):
        """
        Test the removal of products from the cart.
        """
        cart = Cart(self.request)
        cart.add(self.product1, quantity=1)
        cart.add(self.product2, quantity=2)

        cart.remove(self.product1)
        self.assertNotIn(str(self.product1.pk), cart.cart)

        cart.remove(self.product2)
        self.assertEqual(cart.cart, {})

    def test_cart_iter(self):
        """
        Test cart iteration.
        """
        cart = Cart(self.request)
        cart.add(self.product1, quantity=1)
        cart.add(self.product2, quantity=2)
        product_list = list(cart.__iter__())
        reference = [
            {
                "quantity": 1,
                "price": Decimal(self.product1.price),
                "product": self.product1,
                "product_name": self.product1.name,
                "total_price": Decimal(self.product1.price) * 1,
            },
            {
                "quantity": 2,
                "price": Decimal(self.product2.price),
                "product": self.product2,
                "product_name": self.product2.name,
                "total_price": Decimal(self.product2.price) * 2,
            },
        ]
        self.assertEqual(product_list, reference)

    def test_car_len(self):
        """
        Test getting cart size.
        """
        cart = Cart(self.request)
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
        cart = Cart(self.request)
        self.assertEqual(cart.get_total_price(), 0)

        cart.add(self.product1, quantity=1)
        self.assertEqual(cart.get_total_price(), Decimal(self.product1.price) * 1)

        cart.add(self.product2, quantity=2)
        self.assertEqual(cart.get_total_price(), Decimal(self.product1.price) * 1 + Decimal(self.product2.price) * 2)

    def test_cart_clear(self):
        """
        Test emptying the cart.
        """
        cart = Cart(self.request)
        cart.add(self.product1, quantity=1)
        cart.add(self.product2, quantity=2)
        cart.clear()

        with self.assertRaises(KeyError):
            self.request.session[settings.CART_SESSION_ID]


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
        cart = Cart(self.request)
        serializer = CartSerializer(cart)
        reference = {
            "items": {},
            "total_price": "0.00",
        }
        self.assertEqual(serializer.data, reference)

        cart.add(self.product1, quantity=1)
        cart.add(self.product2, quantity=2)
        serializer = CartSerializer(cart)
        reference = {
            "items": {
                str(self.product1.pk): {
                    "quantity": 1,
                    "price": "10.5",
                    "product_name": "poduct1",
                },
                str(self.product2.pk): {
                    "quantity": 2,
                    "price": "11.5",
                    "product_name": "poduct2",
                },
            },
            "total_price": "33.50",
        }
        self.assertEqual(serializer.data, reference)


class TestCartView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = CategoryModel.objects.create(name="category")
        cls.product1 = ProductModel.objects.create(name="poduct1", category=cls.category, price=10.5)
        cls.product2 = ProductModel.objects.create(name="poduct2", category=cls.category, price=11.5)

    def setUp(self) -> None:
        self.client = APIClient()
        super().setUp()

    def test_get_cart(self):
        """
        Test get a cart
        """
        response = self.client.get(reverse("cart:cart_view"))
        self.assertEqual(response.status_code, 200)
        reference = {
            "items": {},
            "total_price": "0.00",
        }
        self.assertEqual(response.json(), reference)

    def test_put_cart(self):
        """
        Test put a item in the cart
        """
        data = {
            "id": self.product1.pk,
        }
        response = self.client.put(reverse("cart:cart_view"), data=data)
        reference = {
            "items": {
                str(self.product1.pk): {
                    "quantity": 1,
                    "price": "10.50",
                    "product_name": "poduct1",
                }
            },
            "total_price": "10.50",
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), reference)

        data = {
            "id": self.product1.pk,
            "quantity": 2,
        }
        response = self.client.put(reverse("cart:cart_view"), data=data)
        reference = {
            "items": {
                str(self.product1.pk): {
                    "quantity": 3,
                    "price": "10.50",
                    "product_name": "poduct1",
                }
            },
            "total_price": "31.50",
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), reference)

        data = {
            "id": self.product1.pk,
            "quantity": 0,
        }
        response = self.client.put(reverse("cart:cart_view"), data=data)
        reference = {
            "items": {
                str(self.product1.pk): {
                    "quantity": 3,
                    "price": "10.50",
                    "product_name": "poduct1",
                }
            },
            "total_price": "31.50",
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), reference)

        data = {
            "id": self.product1.pk,
            "quantity": -1,
        }
        with self.assertRaises(ValueError):
            response = self.client.put(reverse("cart:cart_view"), data=data)

    def test_patch_cart(self):
        """
        Test change the quantity of an item.
        """
        self.client.put(reverse("cart:cart_view"), data={"id": 1})
        self.client.put(reverse("cart:cart_view"), data={"id": 2})

        data = {
            "id": self.product1.pk,
            "quantity": 2,
        }
        response = self.client.patch(reverse("cart:cart_view"), data=data)
        reference = {
            "items": {
                str(self.product1.pk): {
                    "quantity": 2,
                    "price": "10.50",
                    "product_name": "poduct1",
                },
            },
            "total_price": "21.00",
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), reference)

        data = {
            "id": self.product2.pk,
            "quantity": 0,
        }
        response = self.client.patch(reverse("cart:cart_view"), data=data)
        reference = {
            "items": {
                str(self.product1.pk): {
                    "quantity": 2,
                    "price": "10.50",
                    "product_name": "poduct1",
                },
            },
            "total_price": "21.00",
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), reference)

        data = {
            "id": self.product1.pk,
            "quantity": -1,
        }
        with self.assertRaises(ValueError):
            response = self.client.patch(reverse("cart:cart_view"), data=data)

    def test_delete_cart(self):
        """
        Test clear the cart
        """
        self.client.put(reverse("cart:cart_view"), data={"id": 1})
        self.client.put(reverse("cart:cart_view"), data={"id": 2})

        response = self.client.delete(reverse("cart:cart_view"))
        referense = {"items": {}, "total_price": "0.00"}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), referense)
