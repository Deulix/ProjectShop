from django.urls import path
from . import views

from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path("", views.index, name="index"),
    path("category/<slug:slug>/", views.category_products, name="category_products"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("add/", views.add_product, name="add_product"),
    path("profile/<int:pk>/", views.profile, name="profile"),
    path("order/<int:pk>/", views.order_detail, name="order_detail"),
    path("cart/", views.cart, name="cart"),
    path("pay/<int:pk>/", views.pay, name="pay"),
    path("cancel/<int:pk>/", views.cancel, name="cancel"),
    path("set_pending/<int:pk>/", views.set_pending, name="set_pending"),
    path("add_to_cart/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("delete_from_cart/<slug:slug>/", views.delete_from_cart, name="delete_from_cart"),
    path("cart_add_amount/<slug:slug>/", views.cart_add_amount, name="cart_add_amount"),
    path("cart_remove_amount/<slug:slug>/", views.cart_remove_amount, name="cart_remove_amount")
]
