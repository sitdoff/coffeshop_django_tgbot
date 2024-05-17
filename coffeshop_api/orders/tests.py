from cart.cart import Cart
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, TransactionTestCase
from goods.models import CategoryModel, ProductModel
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from .models import OrderItemModel, OrderModel
from .order_factory import OrderFactory, TelegramOrderFactory


# Create your tests here.
class TestOrderItemModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.category = CategoryModel.objects.create(name="category_test_order_item_model")
        cls.product1 = ProductModel.objects.create(name="poduct_1_test_order_item", category=cls.category, price=10.5)
        cls.product2 = ProductModel.objects.create(name="poduct_2_test_order_item", category=cls.category, price=15.5)
        cls.order_item = OrderItemModel.objects.create(
            product=cls.product1,
            price=cls.product1.price,
            quantity=1,
        )
        return super().setUpClass()

    def test_create_order_item(self):
        self.assertEqual(self.order_item.product, self.product1)
        self.assertEqual(self.order_item.price, self.product1.price)
        self.assertEqual(self.order_item.quantity, 1)

    def test_order_item_method_get_cost(self):
        self.assertEqual(self.order_item.get_cost(), self.product1.price)

        old_price = self.order_item.price
        self.order_item.price = old_price * 2
        self.assertEqual(self.order_item.get_cost(), old_price * 2)
        self.order_item.price = old_price

        self.order_item.quantity = 2
        self.assertEqual(self.order_item.get_cost(), self.product1.price * 2)


class TestOrderModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.user = get_user_model().objects.create(
            username="user_test_order_model",
            email="user@mail.com",
        )
        cls.user.set_password("password")
        cls.category = CategoryModel.objects.create(name="category_test_order_model")
        cls.product1 = ProductModel.objects.create(name="poduct1", category=cls.category, price=10.5)
        cls.product2 = ProductModel.objects.create(name="poduct2", category=cls.category, price=15.5)

        cls.order = OrderModel.objects.create(owner=cls.user)
        cls.order_item_1 = OrderItemModel.objects.create(
            product=cls.product1,
            price=cls.product1.price,
            quantity=1,
        )
        cls.order_item_2 = OrderItemModel.objects.create(
            product=cls.product2,
            price=cls.product2.price,
            quantity=2,
        )
        return super().setUpClass()

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        self.order.items.remove(self.order_item_1)
        return super().tearDown()

    def test_create_order(self):
        self.assertEqual(self.order.owner, self.user)
        self.assertFalse(self.order.items.all())

        self.order.items.add(self.order_item_1)
        self.assertIn(self.order_item_1, self.order.items.all())

    def test_order_method_get_total_cost(self):
        self.assertFalse(self.order.items.all())
        self.assertEqual(self.order.get_total_cost(), 0)

        self.order.items.add(self.order_item_1)
        self.assertEqual(self.order.get_total_cost(), self.order_item_1.price * self.order_item_1.quantity)

        self.order.items.add(self.order_item_2)
        self.assertEqual(self.order.get_total_cost(), self.order_item_1.get_cost() + self.order_item_2.get_cost())


class TestOrderFactory(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.user = get_user_model().objects.create(
            username="user_test_order_factory",
            email="user@mail.com",
        )
        cls.user.set_password("password")
        cls.category = CategoryModel.objects.create(name="category_test_order_factory")
        cls.product1 = ProductModel.objects.create(name="poduct1", category=cls.category, price=10.5)
        cls.product2 = ProductModel.objects.create(name="poduct2", category=cls.category, price=15.5)

        cls.order = OrderModel.objects.create(owner=cls.user)
        cls.order_item_1 = OrderItemModel.objects.create(
            product=cls.product1,
            price=cls.product1.price,
            quantity=1,
        )
        cls.order_item_2 = OrderItemModel.objects.create(
            product=cls.product2,
            price=cls.product2.price,
            quantity=2,
        )
        return super().setUpClass()

    def setUp(self) -> None:
        self.request_factory = APIRequestFactory()
        request_factory = APIRequestFactory()
        self.request = request_factory.get("/cart/")
        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(self.request)
        self.request.session.save()
        self.request.user = self.user
        self.request._force_auth_user = self.user
        super().setUp()

    def test_create_order_by_factory(self):
        cart = Cart(self.request)
        factory = TelegramOrderFactory()

        cart.add(self.product1)

        order = factory.create_order(self.request)
        self.assertIsInstance(order, OrderModel)
        self.assertEqual(order.owner, self.user)
        self.assertEqual(len(order.items.all()), 1)

        item_in_order = order.items.first()
        self.assertEqual(item_in_order.product, self.product1)
        self.assertEqual(item_in_order.price, self.product1.price)
        self.assertEqual(item_in_order.quantity, 1)

        cart = Cart(self.request)
        cart.add(self.product1)
        cart.add(self.product2)
        order = factory.create_order(self.request)
        self.assertEqual(len(order.items.all()), 2)

    def test_create_order_no_cart(self):
        factory = TelegramOrderFactory()
        with self.assertRaises(Exception) as context:
            factory.create_order(self.request)
        self.assertEqual(str(context.exception), "Нет корзины")

    def test_create_order_empty_cart(self):
        Cart(self.request)
        factory = TelegramOrderFactory()
        with self.assertRaises(Exception) as context:
            factory.create_order(self.request)
        self.assertEqual(str(context.exception), "Корзина пуста")

    def test_method_get_items(self):
        cart = Cart(self.request)
        factory = TelegramOrderFactory()
        items = factory.get_items(self.request)
        self.assertEqual(items, [])

        cart = Cart(self.request)
        cart.add(self.product1)
        items = factory.get_items(self.request)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertIsInstance(item, OrderItemModel)

    def test_cart_clear_after_order_creation(self):
        cart = Cart(self.request)
        factory = TelegramOrderFactory()

        cart.add(self.product1)

        factory.create_order(self.request)
        self.assertNotIn(settings.CART_SESSION_ID, self.request.session)
