import json
from decimal import Decimal

from cart.cart import Cart
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase
from django.urls import reverse
from goods.models import CategoryModel, ProductModel
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory

from .models import OrderItemModel, OrderModel
from .order_factory import TelegramOrderFactory
from .serializers import OrderItemSerializer, OrderSerializer


# Create your tests here.
class TestOrderItemModel(TestCase):
    """
    Testing OrderItemModel.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.category = CategoryModel.objects.create(name="category_test_order_item_model")
        cls.product1 = ProductModel.objects.create(name="poduct_1_test_order_item", category=cls.category, price=10.5)
        cls.product2 = ProductModel.objects.create(name="poduct_2_test_order_item", category=cls.category, price=15.5)
        cls.order_item = OrderItemModel.objects.create(
            product_id=cls.product1,
            price=cls.product1.price,
            quantity=1,
        )
        return super().setUpClass()

    def test_create_order_item(self):
        """
        Test create ordet item
        """
        self.assertEqual(self.order_item.product_id, self.product1)
        self.assertEqual(self.order_item.price, self.product1.price)
        self.assertEqual(self.order_item.quantity, 1)

    def test_order_item_method_get_cost(self):
        """
        Test method get_cost.
        """
        self.assertEqual(self.order_item.get_cost(), self.product1.price)

        old_price = self.order_item.price
        self.order_item.price = old_price * 2
        self.assertEqual(self.order_item.get_cost(), old_price * 2)
        self.order_item.price = old_price

        self.order_item.quantity = 2
        self.assertEqual(self.order_item.get_cost(), self.product1.price * 2)


class TestOrderModel(TestCase):
    """
    Testing OrderModel.
    """

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
            product_id=cls.product1,
            price=cls.product1.price,
            quantity=1,
        )
        cls.order_item_2 = OrderItemModel.objects.create(
            product_id=cls.product2,
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
        """
        Test create OrderModel.
        """
        self.assertEqual(self.order.owner, self.user)
        self.assertFalse(self.order.items.all())

        self.order.items.add(self.order_item_1)
        self.assertIn(self.order_item_1, self.order.items.all())

    def test_order_method_get_total_cost(self):
        """
        Test method get_total_cost.
        """
        self.assertFalse(self.order.items.all())
        self.assertEqual(self.order.get_total_cost(), 0)

        self.order.items.add(self.order_item_1)
        self.assertEqual(self.order.get_total_cost(), self.order_item_1.price * self.order_item_1.quantity)

        self.order.items.add(self.order_item_2)
        self.assertEqual(self.order.get_total_cost(), self.order_item_1.get_cost() + self.order_item_2.get_cost())


class TestTelegramOrderFactory(TestCase):
    """
    Testing OrderFactory class.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.user = get_user_model().objects.create(
            username="user_test_order_factory", email="user@mail.com", telegram_id="1234"
        )
        cls.user.set_password("password")
        cls.category = CategoryModel.objects.create(name="category_test_order_factory")
        cls.product1 = ProductModel.objects.create(name="poduct1", category=cls.category, price=10.5)
        cls.product2 = ProductModel.objects.create(name="poduct2", category=cls.category, price=15.5)

        cls.order = OrderModel.objects.create(owner=cls.user)
        cls.order_item_1 = OrderItemModel.objects.create(
            product_id=cls.product1,
            price=cls.product1.price,
            quantity=1,
        )
        cls.order_item_2 = OrderItemModel.objects.create(
            product_id=cls.product2,
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
        """
        Test create order by factory.
        """
        cart = Cart()
        factory = TelegramOrderFactory()

        cart.add(self.product1)

        order = factory.create_order(self.request, cart)
        self.assertIsInstance(order, OrderModel)
        self.assertEqual(order.owner, self.user)
        self.assertEqual(len(order.items.all()), 1)

        item_in_order = order.items.first()
        self.assertEqual(item_in_order.product_id, self.product1)
        self.assertEqual(item_in_order.price, self.product1.price)
        self.assertEqual(item_in_order.quantity, 1)

        cart = Cart()
        cart.add(self.product1)
        cart.add(self.product2)
        order = factory.create_order(self.request, cart)
        self.assertEqual(len(order.items.all()), 2)

    def test_create_order_no_cart(self):
        """
        Tests raise exception when there is no cart.
        """
        factory = TelegramOrderFactory()
        with self.assertRaises(ValueError) as context:
            factory.create_order(self.request, None)
        self.assertEqual(str(context.exception), "The cart argument is not an instance of Cart")

    def test_create_order_empty_cart(self):
        """
        Test raise exception when cart is empty.
        """
        cart = Cart()
        factory = TelegramOrderFactory()
        with self.assertRaises(ValueError) as context:
            factory.create_order(self.request, cart)
        self.assertEqual(str(context.exception), "The cart is empty")

    def test_create_order_corrupted_cart(self):
        """
        Test raise exception when cart is corrupted.
        """

        factory = TelegramOrderFactory()

        cart = Cart()
        del cart.cart["items"]

        with self.assertRaises(ValueError) as context:
            factory.create_order(self.request, cart)
        self.assertEqual(str(context.exception), "The cart is corrupted")

        cart = Cart()
        del cart.cart["ordered"]

        with self.assertRaises(ValueError) as context:
            factory.create_order(self.request, cart)
        self.assertEqual(str(context.exception), "The cart is corrupted")

    def test_method_get_items(self):
        """
        Test method get_items.
        """
        cart = Cart()
        factory = TelegramOrderFactory()
        order = OrderModel.objects.create(owner=self.request.user)
        items = factory.get_items(cart, order)
        self.assertEqual(items, [])

        cart = Cart()
        cart.add(self.product1)
        items = factory.get_items(cart, order)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertIsInstance(item, OrderItemModel)

    def test_cart_clear_after_order_creation(self):
        """
        Test emptying the cart after an order is created.
        """
        cart = Cart()
        factory = TelegramOrderFactory()

        cart.add(self.product1)
        self.assertEqual(len(cart), 1)

        factory.create_order(self.request, cart)
        self.assertEqual(len(cart), 0)


class TestOrderSerializer(TestCase):
    """
    Test order serializer.
    """

    def setUp(self) -> None:
        self.user = get_user_model().objects.create(username="testuser", telegram_id="1")
        self.order = OrderModel.objects.create(owner=self.user)
        self.category = CategoryModel.objects.create(name="Test Category")
        self.product = ProductModel.objects.create(name="Test Product", category=self.category, price=Decimal("10.00"))
        self.order_item = OrderItemModel.objects.create(product_id=self.product, price=Decimal("10.00"), quantity=2)
        self.serializer = OrderSerializer(instance=self.order)
        return super().setUp()

    def test_empty_order(self):
        self.assertEqual(self.serializer.data["id"], self.order.pk)
        self.assertEqual(self.serializer.data["items"], [])
        self.assertEqual(Decimal(self.serializer.data["total_cost"]), Decimal(self.order.get_total_cost()))
        self.assertEqual(self.serializer.data["paid"], self.order.paid)
        self.assertEqual(self.serializer.data["owner"], self.order.owner.pk)

    def test_order_with_item(self):
        self.order.items.add(self.order_item)
        self.assertEqual(self.serializer.data["id"], self.order.pk)
        self.assertEqual(self.serializer.data["items"], [OrderItemSerializer(instance=self.order_item).data])
        self.assertEqual(Decimal(self.serializer.data["total_cost"]), Decimal(self.order.get_total_cost()))
        self.assertEqual(self.serializer.data["paid"], self.order.paid)
        self.assertEqual(self.serializer.data["owner"], self.order.owner.pk)


class TestOrderItemSerializer(TestCase):
    """
    Test order item serializer.
    """

    def setUp(self) -> None:
        self.category = CategoryModel.objects.create(name="Test Category")
        self.product = ProductModel.objects.create(name="Test Product", category=self.category, price=Decimal("10.00"))
        self.order_item = OrderItemModel.objects.create(product_id=self.product, price=Decimal("10.00"), quantity=2)
        self.serializer = OrderItemSerializer(instance=self.order_item)
        return super().setUp()

    def test_order_item(self):
        expected_item_data = {
            "id": self.order_item.pk,
            "cost": str(self.order_item.get_cost()),
            "price": str(self.order_item.price),
            "quantity": self.order_item.quantity,
            "order": None,
            "product_id": self.product.pk,
        }
        self.assertEqual(self.serializer.data, expected_item_data)


class TestOrderViewSet(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            username="test_user_order_view_set", email="user@mail.com", telegram_id="123456"
        )
        self.auth_token, _ = Token.objects.get_or_create(user=self.user)
        self.headers = {"Authorization": f"Token {self.auth_token}"}
        self.category = CategoryModel.objects.create(name="test_category")
        self.product1 = ProductModel.objects.create(name="test_product1", category=self.category, price=100)
        self.product2 = ProductModel.objects.create(name="test_product2", category=self.category, price=120)

    def test_get_method(self):
        response = self.client.get(reverse("order-list"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content.decode(), '{"detail":"Authentication credentials were not provided."}')

        response = self.client.get(reverse("order-list"), headers=self.headers)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("count", response_data)
        self.assertEqual(response_data["count"], 0)
        self.assertIn("results", response_data)
        self.assertEqual(response_data["results"], [])

    def test_post_method_with_invalid_data(self):
        # Invalid price
        data = {
            "items": {
                self.product1.pk: {
                    "product_id": self.product1.pk,
                    "product_name": "Экспресса",
                    "price": self.product1.price - 5,
                    "quantity": 3,
                    "cost": "100.00",
                },
                self.product2.pk: {
                    "product_id": self.product2.pk,
                    "product_name": "Американа",
                    "price": self.product2.price,
                    "quantity": 2,
                    "cost": "240.00",
                },
            },
            "total_cost": "220.00",
            "telegram_id": self.user.telegram_id,
        }

        response = self.client.post(reverse("order-list"), data=data, headers=self.headers, format="json")
        self.assertEqual(
            response.content.decode(),
            '{"error":"Item %s price is wrong!"}' % (data["items"][self.product1.pk]["product_name"]),
        )

    def test_post_method_with_valid_data(self):
        # Общая стоимость подуктов специально указана неправильно. В дальнейшем, когда добавятся проверки, это будет исправленно.
        # По идее, если общая стоимость товаров в корзине не совпадает с общей стоимостью заказа, то должна выбрасываться ошибка.
        data = {
            "items": {
                self.product1.pk: {
                    "product_id": self.product1.pk,
                    "product_name": "Экспресса",
                    "price": self.product1.price,
                    "quantity": 3,
                    "cost": "100.00",
                },
                self.product2.pk: {
                    "product_id": self.product2.pk,
                    "product_name": "Американа",
                    "price": self.product2.price,
                    "quantity": 2,
                    "cost": "240.00",
                },
            },
            "total_cost": "220.00",
            "telegram_id": self.user.telegram_id,
        }
        response = self.client.post(path=reverse("order-list"), data=data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content.decode(), '{"detail":"Authentication credentials were not provided."}')

        response = self.client.post(path=reverse("order-list"), data=data, headers=self.headers, format="json")
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response_data)
        self.assertIn("items", response_data)
        self.assertIn("owner", response_data)
        self.assertIn("paid", response_data)
        self.assertIn("total_cost", response_data)
        self.assertEqual(response_data["owner"], self.user.pk)
        self.assertFalse(response_data["paid"])
        self.assertEqual(
            Decimal(response_data["total_cost"]),
            sum(Decimal(item["price"]) * Decimal(item["quantity"]) for item in response_data["items"]),
        )
        products = OrderItemModel.objects.filter(order=response_data["id"])

        reference = [
            {
                "cost": str(self.product1.price * data["items"][self.product1.pk]["quantity"]) + ".00",
                "id": products.get(product_id=self.product1.pk).pk,
                "order": response_data["id"],
                "price": str(self.product1.price) + ".00",
                "product_id": self.product1.pk,
                "quantity": data["items"][self.product1.pk]["quantity"],
            },
            {
                "cost": str(self.product2.price * data["items"][self.product2.pk]["quantity"]) + ".00",
                "id": products.get(product_id=self.product2.pk).pk,
                "order": response_data["id"],
                "price": str(self.product2.price) + ".00",
                "product_id": self.product2.pk,
                "quantity": data["items"][self.product2.pk]["quantity"],
            },
        ]
        self.assertEqual(response_data["items"], reference)

    def test_put_method(self):
        response = self.client.put(reverse("order-list"), headers=self.headers, format="json")
        self.assertEqual(response.json(), {"detail": 'Method "PUT" not allowed.'})

    def test_patch_method(self):
        response = self.client.patch(reverse("order-list"), headers=self.headers, format="json")
        self.assertEqual(response.json(), {"detail": 'Method "PATCH" not allowed.'})

    def test_delete_method(self):
        response = self.client.delete(reverse("order-list"), headers=self.headers, format="json")
        self.assertEqual(response.json(), {"detail": 'Method "DELETE" not allowed.'})

    def test_options_method(self):
        response = self.client.options(reverse("order-list"), headers=self.headers, format="json")
        self.assertTrue(response.content)
