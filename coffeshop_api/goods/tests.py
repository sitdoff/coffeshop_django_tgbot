from django.test import TestCase
from django.urls import reverse
from goods.models import CategoryModel, ProductModel
from goods.serializers import (
    CategorySerializer,
    ProductSerializer,
    SubCategorySerializer,
)
from goods.urls import router
from goods.views import CategoryViewSet
from rest_framework.test import APIRequestFactory


# Create your tests here.
class TestCategoryModel(TestCase):
    """
    Tets CategoryModel
    """

    def test_create(self):
        """
        Test create CategoryModel
        """
        CategoryModel.objects.create(name="instance")
        isinstance = CategoryModel.objects.get(name="instance")
        self.assertEqual(isinstance.name, "instance")

    def test_parent(self):
        """
        Test connection with another category.
        """
        isinstance = CategoryModel.objects.create(name="instance")
        child = CategoryModel.objects.create(name="child", parent=isinstance)
        self.assertEqual(child.parent, isinstance)
        self.assertIn(child, isinstance.children.all())


class TestProductModel(TestCase):
    """
    Test ProductModel
    """

    def test_create(self):
        """
        Test create ProductModel
        """
        category = CategoryModel.objects.create(name="category")
        product = ProductModel.objects.create(name="poduct", category=category, price=10.5)
        self.assertEqual(product.name, "poduct")
        self.assertEqual(product.category, category)
        self.assertEqual(product.price, 10.5)


class TestCategorySerializer(TestCase):
    """
    Test CategorySerializer
    """

    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.category_parent_1 = CategoryModel.objects.create(name="category_parent_1")
        self.category_parent_2 = CategoryModel.objects.create(name="category_parent_2")
        self.category_child_1 = CategoryModel.objects.create(name="category_child_1", parent=self.category_parent_1)
        self.category_child_2 = CategoryModel.objects.create(name="category_child_2", parent=self.category_parent_2)
        self.category_child_3 = CategoryModel.objects.create(name="category_child_3", parent=self.category_parent_2)

    def test_serializer_parent(self):
        """
        Test CategorySerializer parent side
        """
        request = self.request_factory.get("/category/")
        serializer_parent_1 = CategorySerializer(instance=self.category_parent_1, context={"request": request})
        children_url = request.build_absolute_uri(
            reverse("categorymodel-detail", kwargs={"pk": self.category_child_1.pk})
        )
        self.assertEqual(children_url, serializer_parent_1.data["children"][0]["url"])
        self.assertIsNone(serializer_parent_1.data["parent"])
        self.assertEqual(len(serializer_parent_1.data["children"]), 1)

        serializer_parent_2 = CategorySerializer(instance=self.category_parent_2, context={"request": request})
        self.assertIsNone(serializer_parent_2.data["parent"])
        self.assertEqual(len(serializer_parent_2.data["children"]), 2)

    def test_serializer_child(self):
        """
        Test CategorySerializer child side
        """

        request = self.request_factory.get("/category/")
        serializer_child_1 = CategorySerializer(instance=self.category_child_1, context={"request": request})
        self.assertEqual(serializer_child_1.data["children"], [])
        parent_url = request.build_absolute_uri(
            reverse("categorymodel-detail", kwargs={"pk": self.category_parent_1.pk})
        )
        self.assertEqual(serializer_child_1.data["parent"], parent_url)
