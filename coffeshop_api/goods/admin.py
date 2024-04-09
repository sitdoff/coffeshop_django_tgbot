from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import CategoryModel, ProductModel

# Register your models here.
admin.site.register(CategoryModel, MPTTModelAdmin)
admin.site.register(ProductModel, admin.ModelAdmin)
