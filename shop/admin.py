from django.contrib import admin
from .models import Product, Comment, Category, Cart, CartItem, Order, OrderItem


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active")
    search_fields = ("categories",)
    filter_horizontal = ("categories",)
    list_filter = ("is_active",)



class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "created_at",
        "first_name",
        "last_name",
        "email",
        "address_street",
        "address_building",
        "total_price",
        "status",
    )
    list_filter = ("status",)


class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "price")


class CartAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "created_at", "session_key")


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "product", "created_at")

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")




admin.site.register(Product, ProductAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
