from django.contrib import admin
from .models import *
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_date', 'total_price']

admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(ShoppingCart)