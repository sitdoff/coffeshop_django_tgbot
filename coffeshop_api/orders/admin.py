from django.contrib import admin

from .models import OrderItemModel, OrderModel


# Register your models here.
class OrderItemModelInLine(admin.StackedInline):
    model = OrderItemModel
    max_num = 2


@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    inlines = [OrderItemModelInLine]
