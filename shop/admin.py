from django.contrib import admin
from .models import Product, Comment, Category, Cart, CartItem, Order, OrderItem

class ProductAdmin(admin.ModelAdmin):
    search_fields = ('categories',)
    filter_horizontal = ('categories',)

admin.site.register(Product, ProductAdmin)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
