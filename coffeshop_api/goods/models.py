from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.
class CategoryModel(MPTTModel):
    """
    Category model

    Refers to itself.
    """

    name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self) -> str:
        return self.name


class ProductModel(models.Model):
    """
    Product model

    Refers to CategoryModel
    """

    name = models.CharField(max_length=100, blank=False, verbose_name="Название продукта")
    category = models.ForeignKey(
        CategoryModel, on_delete=models.CASCADE, related_name="products", verbose_name="Категория", default=None
    )
    price = models.DecimalField(blank=False, max_digits=5, decimal_places=2, verbose_name="Цена")

    def __str__(self) -> str:
        return f"{self.name} {self.price:.2f}"
