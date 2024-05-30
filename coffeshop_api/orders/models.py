from django.conf import settings
from django.db import models
from django.db.models.fields.related import RelatedField
from goods.models import ProductModel

# Create your models here.


class OrderModel(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders", verbose_name="Пользователь"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    items: RelatedField

    class Meta:
        ordering = ("-created",)

    def __str__(self) -> str:
        return f"Order {self.pk}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItemModel(models.Model):
    order = models.ForeignKey(
        OrderModel, on_delete=models.CASCADE, null=True, related_name="items", verbose_name="Заказ"
    )
    product_id = models.ForeignKey(
        ProductModel, on_delete=models.CASCADE, related_name="order_item", verbose_name="Товар"
    )
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self) -> str:
        return f"Item {self.pk}"

    def get_cost(self):
        return self.price * self.quantity
