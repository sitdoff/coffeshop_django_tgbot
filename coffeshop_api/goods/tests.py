from django.test import TestCase
from goods.models import CategoryModel, ProductModel


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
