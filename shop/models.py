from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator, RegexValidator
from django.contrib import admin
   
regex_phone_validator = RegexValidator(
    regex="^[\d+]\d+$",
    message="Введите корректный номер телефона (например, +375 12 345 67 89)"
)

def validate_str(value: str):
    if not value.isalpha():
        raise ValidationError("Допустимы только буквенные значения и дефис (-)")

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
    name = models.CharField(max_length=100, verbose_name="Название")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена, BYN"
    )
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
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
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
    user = models.OneToOneField(
        User, verbose_name=("Пользователь"), related_name='cart', on_delete=models.CASCADE
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
    
    @property
    def price(self):
        return sum(item.price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name=("Корзина"), related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, verbose_name=("Товар"), on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество, шт.")
    created_at = models.DateTimeField(
        auto_now=False, auto_now_add=True, verbose_name="Создано"
    )
    class Meta:
        ordering = ['-id']
        verbose_name = "предмет корзины"
        verbose_name_plural = "Предметы корзины"

    @property
    def price(self):
        return self.product.price * self.quantity
    
    @property
    def price_per_one(self):
        return self.product.price

    def __str__(self):
        return f"Предмет #{self.pk} ({self.product.name}) добавлен в корзину #{self.cart.pk} -- количество: {self.quantity} шт. --  цена: {self.price} BYN"


class Order(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Подтвержден"),
        ("canceled", "Отменен"),
        ("pending", "В обработке"),
    ]
    user = models.ForeignKey(
        User, verbose_name=("Пользователь"), null=True, on_delete=models.CASCADE
    )
    first_name = models.CharField(verbose_name="Имя", max_length=50)
    last_name = models.CharField(verbose_name="Фамилия", max_length=50)
    email = models.EmailField(max_length=254)
    phone = models.CharField(
        verbose_name="Телефон", max_length=15, validators=[regex_phone_validator, MinLengthValidator(10)]
    )
    address_street = models.CharField(verbose_name="Улица", max_length=100, validators=[validate_str])
    address_building = models.PositiveIntegerField(verbose_name="Номер дома", null=True, blank=True, validators=[MaxValueValidator(300)])
    address_apartment = models.PositiveIntegerField(verbose_name="Квартира", null=True, blank=True, validators=[MaxValueValidator(2000)])
    address_floor = models.PositiveIntegerField(verbose_name="Этаж", null=True, blank=True, validators=[MaxValueValidator(50)])
    discount = models.IntegerField("Скидка(от 0 до 100), %", null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending", verbose_name="Статус"
    )
    created_at = models.DateTimeField(
        auto_now=False, auto_now_add=True, verbose_name="Создано"
    )

    def __str__(self):
        return f"Заказ #{self.pk} -- пользователь {self.user} -- создан {self.created_at.strftime('%d-%m-%Y в %H:%M')}"

    @property
    def price(self):
        return sum(item.price for item in self.items.all())

    @property
    def discount_amount(self):
        return  self.price / 100 * self.discount

    @property
    # @admin.display(description='Итоговая цена')
    def total_price(self):
        if self.discount is None:
            return self.price
        else:
            return self.price - (self.price / 100 * self.discount)

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name=("Заказ"), related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, verbose_name=("Товар"), on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество, шт.")
   
    @property
    def price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"Предмет #{self.pk} ({self.product.name}) добавлен в  заказ #{self.order.pk} -- количество: {self.quantity} шт. --  цена: {self.price} BYN"

    class Meta:
        verbose_name = "предмет заказа"
        verbose_name_plural = "Предметы заказов"

