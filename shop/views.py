from django.shortcuts import render, get_object_or_404
from .models import Product, Comment, Category


def index(request):
    products = Product.objects.all().order_by("-created_at")
    return render(request, "index.html", {"products": products})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, "category.html", {"category":category, "products":products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "product_detail.html", {"product": product})
