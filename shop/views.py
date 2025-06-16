from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Comment
from .forms import AddProduct, CommentForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



def index(request, sorting='new'):
    if sorting == 'old':
        products = Product.objects.all()
    else:
        products = Product.objects.all().order_by("-created_at")   
    categories = Category.objects.all()
    return render(
        request, "index.html", {"products": products, "categories": categories, "sorting":sorting}
    )


def category_products(request, slug):
    categories = Category.objects.all()
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(categories=category)
    return render(
        request,
        "category.html",
        {"category": category, "products": products, "categories": categories},
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    comments = Comment.objects.filter(product=product)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comments = form.save(commit=False)
            comments.product = product
            comments.user = request.user
            comments.save()
            return redirect("product_detail", slug=slug)
    else:
        form = CommentForm()
    return render(request, "product_detail.html", {"product": product, "comments":comments, 'form':form})


def add_product(request):
    if request.method == "POST":
        form = AddProduct(request.POST, request.FILES)
        if form.is_valid():
            try:
                product = Product(
                    name=form.cleaned_data["name"],
                    price=form.cleaned_data["price"],
                    description=form.cleaned_data.get("description", ""),
                    slug=form.cleaned_data["slug"],
                    is_active=form.cleaned_data["is_active"],
                )
                if "image" in request.FILES:
                    product.image = form.cleaned_data["image"]

                product.save()

                if hasattr(form, "cleaned_data") and "categories" in form.cleaned_data:
                    product.categories.set(form.cleaned_data["categories"])

                messages.success(request, "Товар успешно добавлен!")
                return redirect("product_detail", slug=product.slug)

            except Exception as e:
                messages.error(request, f"ОШИБКА! {e}")
            return redirect("index")
    else:
        form = AddProduct()

    return render(request, "add_product.html", {"form": form})
