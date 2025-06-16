from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError


def validate_phone(value):
    if not value[0] == "+":
        raise ValidationError("Номер телефона должен быть в формате +XXX...")
    elif not "".join(value[1:]).isdigit():
        raise ValidationError("Номер телефона должен состоять из цифр")


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Уникальный URL",
        help_text="Короткая метка для контента, содержащая только буквы, цифры, подчеркивания (_) или дефисы (-)",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена, BYN")
    description = models.TextField(verbose_name="Описание", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, verbose_name="Категория")
    slug = models.SlugField(
        max_length=50,
        unique=True,
        null=True,
        verbose_name="Уникальный URL",
        help_text="Короткая метка для контента, содержащая только буквы, цифры, подчеркивания (_) или дефисы (-)",
    )
    image = models.ImageField(
        upload_to="images/products", verbose_name="Изображение", null=True, blank=True
    )
    is_active = models.BooleanField(default=True, verbose_name="Товар активен")

    @property
    def cats(self):
        return [cat.name for cat in self.categories.all()]

    def __str__(self):
        # catword = "категории" if self.categories.count() > 1 else "категория"
        # return f"{self.name} -- {self.price} BYN -- активен: {self.is_active} -- {catword}: {', '.join(self.cats)}"
        return self.name

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "Товары"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="comments", verbose_name="Товар"
    )
    text = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    image = models.ImageField(
        upload_to="images/comments",
        verbose_name="Изображение",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Комментарий {self.user} на товар {self.product} создан {self.created_at.strftime('%d-%m-%Y в %H:%M')}"

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"


class Cart(models.Model):
    user = models.ForeignKey(
        User, verbose_name=("Пользователь"), null=True, on_delete=models.CASCADE
    )
    session_key = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Ключ сессии"
    )
    created_at = models.DateTimeField(
        auto_now=False, auto_now_add=True, verbose_name="Создано"
    )

    class Meta:
        verbose_name = "корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина #{self.pk} -- пользователь {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name=("Корзина"), on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, verbose_name=("Товар"), on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество, шт.")
    price = models.DecimalField(verbose_name="Цена, BYN", max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = "предмет корзины"
        verbose_name_plural = "Предметы корзины"

    def __str__(self):
        return f"Предмет #{self.pk} ({self.product.name}) добавлен в корзину #{self.cart.pk} -- количество: {self.quantity} шт. --  цена: {self.price} BYN"


class Order(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Подтверждено"),
        ("cancrled", "Отменено"),
        ("pending", "В обработке"),
    ]
    user = models.ForeignKey(
        User, verbose_name=("Пользователь"), null=True, on_delete=models.CASCADE
    )
    first_name = models.CharField(verbose_name="Имя", max_length=50)
    last_name = models.CharField(verbose_name="Фамилия", max_length=50)
    email = models.EmailField(max_length=254)
    phone = models.CharField(
        verbose_name="Телефон", max_length=15, validators=[validate_phone]
    )
    address = models.TextField(verbose_name="Адрес")
    total_price = models.DecimalField(
        verbose_name="Итоговая Цена, BYN", max_digits=8, decimal_places=2
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending", verbose_name="Статус"
    )
    created_at = models.DateTimeField(
        auto_now=False, auto_now_add=True, verbose_name="Создано"
    )

    def __str__(self):
        return f"Заказ #{self.pk} -- пользователь {self.user} -- создан {self.created_at.strftime('%d-%m-%Y в %H:%M')}"

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name=("Заказ"), on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, verbose_name=("Товар"), on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество, шт.")
    price = models.DecimalField(verbose_name="Цена, BYN", max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Предмет #{self.pk} ({self.product.name}) добавлен в  заказ #{self.order.pk} -- количество: {self.quantity} шт. --  цена: {self.price} BYN"
    

    class Meta:
        verbose_name = "предмет заказа"
        verbose_name_plural = "Предметы заказов"
