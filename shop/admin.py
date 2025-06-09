from django.contrib import admin
from .models import Product, Comment, Category

class ProductAdmin(admin.ModelAdmin):
    search_fields = ('categories',)
    filter_horizontal = ('categories',)

admin.site.register(Product, ProductAdmin)
admin.site.register(Comment)
admin.site.register(Category)
