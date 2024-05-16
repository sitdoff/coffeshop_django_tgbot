from django.contrib import admin

from .models import OrderItemModel, OrderModel


# Register your models here.
class OrderItemModelInLine(admin.TabularInline):
    model = OrderItemModel


@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    inlines = [OrderItemModelInLine]
