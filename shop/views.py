from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Comment, Cart, CartItem, Order, OrderItem
from .forms import AddProduct, CommentForm, CustomRegister, CustomLogin, OrderConfirm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from django.urls import reverse


def index(request):
    sort = request.GET.get("sort", "new")

    if sort == "old":
        products = Product.objects.all().order_by("-created_at")
    else:
        products = Product.objects.all().order_by("created_at")

    categories = Category.objects.all()
    return render(
        request,
        "index.html",
        {"products": products, "categories": categories, "sort": sort},
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
    return render(
        request,
        "product_detail.html",
        {"product": product, "comments": comments, "form": form},
    )


@login_required
def profile(request, pk):
    if request.user.pk != pk:
        return redirect("index")
    orders = Order.objects.filter(user=request.user).prefetch_related("items").order_by('-created_at')
    return render(request, "profile.html", {"user": request.user, "orders": orders})


@login_required
def order_detail(request, pk):
    order = Order.objects.get(pk=pk)
    if request.user.pk != order.user.pk:
        return redirect("index")
    return render(request, "order_detail.html", {"user": request.user, "order": order})


@login_required
def cart(request):
    cart, _ = Cart.objects.prefetch_related("items__product").get_or_create(user=request.user)
    if request.method == "POST":
        form = OrderConfirm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user = request.user,
                first_name = form.cleaned_data['first_name'],
                last_name = form.cleaned_data['last_name'],
                email = form.cleaned_data['email'],
                phone = form.cleaned_data['phone'],
                address_street = form.cleaned_data['address_street'],
                address_building = form.cleaned_data['address_building'],
                address_apartment = form.cleaned_data['address_apartment'],
                address_floor = form.cleaned_data['address_floor']
            )
            order.save()
            print(request.POST)
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order = order,
                    product = cart_item.product,
                    quantity = cart_item.quantity
                )
            cart.items.all().delete()
            
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderConfirm()

    return render(
        request,
        "cart.html",
        {"user": request.user, "cart": cart, "items": cart.items.all(), "form":form},
    )


@login_required
def add_to_cart(request, slug):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, slug=slug)
    if request.method == "POST":
        item, created = CartItem.objects.get_or_create(product=product, cart=cart)
        if created:
            item.quantity = 1
        else:
            item.quantity += 1
            item.save()
        messages.success(request, mark_safe(f'Предмет успешно добавлен в <a href="{reverse("cart")}" class="alert-link">корзину!</a>'))
        return redirect("product_detail", slug=slug)

    return redirect("product_detail", slug=slug)


@login_required
def delete_from_cart(request, slug):
    if request.method == "POST":
        cart = Cart.objects.get(user=request.user)
        CartItem.objects.filter(cart=cart, product__slug=slug).delete()
        messages.success(request, "Предмет успешно удалён из корзины!")
        return redirect("cart")

    return redirect("cart")

@login_required
def cart_add_amount(request, slug):
    # if request.method == "POST":
        cart = Cart.objects.get(user=request.user)
        item = CartItem.objects.get(cart=cart, product__slug=slug)
        item.quantity += 1
        item.save()
        return redirect("cart")

    # return redirect("cart")

@login_required
def cart_remove_amount(request, slug):
    # if request.method == "POST":
        cart = Cart.objects.get(user=request.user)
        item = CartItem.objects.get(cart=cart, product__slug=slug)
        if item.quantity <= 1:
            item.delete()
            messages.success(request, "Предмет успешно удалён из корзины!")
        else:
            item.quantity -= 1
            item.save()

        return redirect("cart")

    # return redirect("cart")

@login_required
def pay(request, pk):
    order = Order.objects.get(pk=pk)
    if request.user.pk != order.user.pk:
        return redirect("index")
    if request.method == "POST":
        order.status = "confirmed"
        order.save()
        messages.success(request, "Ваш заказ успешно оформлен! Благодарим за оплату!")
        return redirect("profile", pk=request.user.pk)
    return redirect("index")


@login_required
def cancel(request, pk):
    order = Order.objects.get(pk=pk)
    if request.user.pk != order.user.pk:
        return redirect("index")
    if request.method == "POST":
        order.status = "canceled"
        order.save()
        return redirect("profile", pk=request.user.pk)
    return redirect("index")


@login_required
def set_pending(request, pk):
    order = Order.objects.get(pk=pk)
    if request.method == "POST":
        order.status = "pending"
        order.save()
        return redirect("order_detail", pk=pk)
    return redirect("index")


@login_required
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


def register(request):
    if request.method == "POST":
        form = CustomRegister(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = CustomRegister()
    return render(request, "registration/register.html", {"form": form})


class CustomLoginView(LoginView):
    form_class = CustomLogin
    template_name = "registration/login.html"
